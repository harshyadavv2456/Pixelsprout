import crypto from "node:crypto";
import { supabaseConfigured, kvGet, kvSet, applyCors } from "./_supabase.js";
import { ATTR_KEYS, SEED_ENTITIES } from "./_cold-read-seed.js";

// Stored value: { schema: 2, entities: [{ name, v }], gamesPlayed }.
// The browser can NEVER send the whole dataset. POST accepts exactly one of:
//   { action: "guess", id, answers }  - a confirmed guess for an existing entry
//   { action: "teach", id, answers }  - "it was X" where X already exists
//   { action: "add",   name, answers } - one brand-new entry
// id = slug of the entry name (see slugify). answers = { attrKey: 0|0.25|0.75|1 }.
const KEY = "coldread:dataset";
const SCHEMA = 2;

const MAX_BODY_BYTES = 2048;
const MAX_NAME_LEN = 60;
const MAX_ID_LEN = 64;
const MAX_ENTITIES = 3000;
const ID_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const ALLOWED_VALUES = new Set([0, 0.25, 0.75, 1]);
const ATTR_SET = new Set(ATTR_KEYS);
const ACTION_FIELDS = {
  guess: ["action", "id", "answers"],
  teach: ["action", "id", "answers"],
  add: ["action", "name", "answers"],
};
const BLEND = { guess: 0.15, teach: 0.35 };

// Rate limit: 30 writes / 60 s and 5 writes / 5 s per IP.
const RL_MINUTE = 30;
const RL_BURST = 5;
const RL_BURST_WINDOW_MS = 5000;

export function slugify(name) {
  return String(name)
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

class BadRequest extends Error {
  constructor(msg, status = 400) { super(msg); this.status = status; }
}

function isPlainObject(x) {
  return x !== null && typeof x === "object" && !Array.isArray(x) && Object.getPrototypeOf(x) === Object.prototype;
}

function validateAnswers(answers) {
  if (!isPlainObject(answers)) throw new BadRequest("answers must be an object");
  const keys = Object.keys(answers);
  if (keys.length > ATTR_KEYS.length) throw new BadRequest("too many answers");
  for (const k of keys) {
    if (!ATTR_SET.has(k)) throw new BadRequest(`unknown attribute: ${k.slice(0, 40)}`);
    const v = answers[k];
    if (typeof v !== "number" || !ALLOWED_VALUES.has(v)) throw new BadRequest(`invalid value for ${k}`);
  }
  return keys;
}

export function validateUpdate(body) {
  if (!isPlainObject(body)) throw new BadRequest("body must be a JSON object");
  if ("entities" in body || "gamesPlayed" in body) {
    throw new BadRequest("full dataset replacement is not allowed", 403);
  }
  const fields = ACTION_FIELDS[body.action];
  if (!fields) throw new BadRequest("action must be one of: guess, teach, add");
  for (const k of Object.keys(body)) {
    if (!fields.includes(k)) throw new BadRequest(`unexpected field: ${String(k).slice(0, 40)}`);
  }
  validateAnswers(body.answers);
  if (body.action === "add") {
    if (typeof body.name !== "string") throw new BadRequest("name must be a string");
    const name = body.name.trim().replace(/\s+/g, " ");
    if (name.length < 1 || name.length > MAX_NAME_LEN) throw new BadRequest(`name must be 1-${MAX_NAME_LEN} chars`);
    if (/[\u0000-\u001f\u007f<>{}]/.test(name)) throw new BadRequest("name contains invalid characters");
    const id = slugify(name);
    if (!id || id.length > MAX_ID_LEN || !ID_RE.test(id)) throw new BadRequest("name must contain letters or digits");
    return { action: "add", name, id, answers: body.answers };
  }
  if (typeof body.id !== "string" || body.id.length > MAX_ID_LEN || !ID_RE.test(body.id)) {
    throw new BadRequest("invalid id format");
  }
  if (Object.keys(body.answers).length === 0) throw new BadRequest("answers must not be empty");
  return { action: body.action, id: body.id, answers: body.answers };
}

// ---- one-time migration: server-side backup + reseed merge ----------------
export function mergeSeed(entities) {
  const out = [];
  const seen = new Set();
  const existing = new Map();
  for (const e of Array.isArray(entities) ? entities : []) {
    if (!e || typeof e.name !== "string") continue;
    const id = slugify(e.name);
    if (!id || existing.has(id)) continue;
    existing.set(id, e);
  }
  let kept = 0, added = 0;
  for (const s of SEED_ENTITIES) {
    const id = slugify(s.name);
    if (existing.has(id)) {
      const e = existing.get(id);
      out.push({ name: e.name, v: isPlainObject(e.v) ? e.v : { ...s.v } });
      kept++;
    } else {
      out.push({ name: s.name, v: { ...s.v } });
      added++;
    }
    seen.add(id);
  }
  let extra = 0;
  for (const [id, e] of existing) {
    if (seen.has(id)) continue;
    out.push({ name: e.name, v: isPlainObject(e.v) ? e.v : {} });
    extra++;
  }
  return { entities: out, stats: { before: existing.size, keptFromServer: kept, addedFromSeed: added, extraServerOnly: extra, after: out.length } };
}

async function loadDataset() {
  const value = await kvGet(KEY);
  if (value && value.schema === SCHEMA && Array.isArray(value.entities)) return value;
  // Not migrated yet: keep a server-side copy of the raw value, then reseed.
  const stamp = new Date().toISOString().slice(0, 10);
  if (value) {
    const backupKey = `${KEY}:backup-${stamp}`;
    const existingBackup = await kvGet(backupKey);
    if (!existingBackup) await kvSet(backupKey, value);
  }
  const { entities, stats } = mergeSeed(value && value.entities);
  const migrated = {
    schema: SCHEMA,
    entities,
    gamesPlayed: Number.isFinite(value && value.gamesPlayed) ? value.gamesPlayed : 0,
    migration: { at: new Date().toISOString(), ...stats },
  };
  await kvSet(KEY, migrated);
  return migrated;
}

function publicView(value) {
  return {
    entities: value.entities.map((e) => ({ id: slugify(e.name), name: e.name, v: e.v })),
    gamesPlayed: value.gamesPlayed || 0,
  };
}

// ---- rate limiting -----------------------------------------------------------
const memHits = new Map(); // ipHash -> [timestamps]

function clientIp(req) {
  const vf = String(req.headers["x-vercel-forwarded-for"] || "").split(",")[0].trim();
  if (vf) return vf;
  const xff = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  return xff || String(req.headers["x-real-ip"] || "") || (req.socket && req.socket.remoteAddress) || "unknown";
}

// IPv6 clients commonly rotate addresses inside their /64, so bucket IPv6 by /64.
export function ipBucket(ip) {
  ip = String(ip).trim().toLowerCase();
  if (ip.startsWith("::ffff:")) return ip.slice(7);
  if (!ip.includes(":")) return ip;
  const [head, tail = ""] = ip.split("::");
  const h = head ? head.split(":") : [];
  const t = tail ? tail.split(":") : [];
  const full = ip.includes("::") ? [...h, ...Array(Math.max(0, 8 - h.length - t.length)).fill("0"), ...t] : h;
  return full.slice(0, 4).map((x) => (parseInt(x || "0", 16) || 0).toString(16)).join(":") + "::/64";
}

function ipHash(ip) {
  return crypto.createHash("sha256").update("coldread:" + ipBucket(ip)).digest("hex").slice(0, 24);
}

function memoryLimit(h, now) {
  const arr = (memHits.get(h) || []).filter((t) => now - t < 60_000);
  const burst = arr.filter((t) => now - t < RL_BURST_WINDOW_MS).length;
  if (arr.length >= RL_MINUTE || burst >= RL_BURST) { memHits.set(h, arr); return false; }
  arr.push(now);
  memHits.set(h, arr);
  if (memHits.size > 5000) memHits.delete(memHits.keys().next().value);
  return true;
}

// Shared (cross-instance) minute counter in the same Supabase kv_store.
// Best effort: on any storage error we fall back to the in-memory limiter alone.
async function sharedLimit(h, now) {
  try {
    const key = `coldread:rl:${h}`;
    const cur = await kvGet(key);
    const hits = (cur && Array.isArray(cur.hits) ? cur.hits : []).filter((t) => typeof t === "number" && now - t < 60_000);
    const burst = hits.filter((t) => now - t < RL_BURST_WINDOW_MS).length;
    if (hits.length >= RL_MINUTE || burst >= RL_BURST) return false;
    hits.push(now);
    await kvSet(key, { hits });
    sharedLimit.lastRemaining = RL_MINUTE - hits.length;
    return true;
  } catch (err) {
    console.error("cold-read rate-limit store unavailable", String((err && err.message) || err).slice(0, 200));
    return null; // fall back to the in-memory limiter
  }
}

async function rateLimit(req, res) {
  const h = ipHash(clientIp(req));
  const now = Date.now();
  if (!memoryLimit(h, now)) { res.setHeader("X-RateLimit-Source", "memory"); return false; }
  const r = await sharedLimit(h, now);
  res.setHeader("X-RateLimit-Source", r === null ? "memory-fallback" : "shared");
  if (r === true) res.setHeader("X-RateLimit-Remaining", String(sharedLimit.lastRemaining));
  return r !== false;
}

// ---- body parsing -----------------------------------------------------------
async function readBody(req) {
  const len = Number(req.headers["content-length"] || 0);
  if (len > MAX_BODY_BYTES) throw new BadRequest("payload too large", 413);
  let parsedBody;
  try {
    parsedBody = req.body; // Vercel's lazy parser throws on invalid JSON
  } catch {
    throw new BadRequest("malformed JSON");
  }
  let raw;
  if (typeof parsedBody === "string") raw = parsedBody;
  else if (Buffer.isBuffer(parsedBody)) raw = parsedBody.toString("utf8");
  else if (parsedBody && typeof parsedBody === "object") raw = JSON.stringify(parsedBody);
  else raw = "";
  if (Buffer.byteLength(raw, "utf8") > MAX_BODY_BYTES) throw new BadRequest("payload too large", 413);
  if (!raw) throw new BadRequest("empty body");
  try {
    return JSON.parse(raw);
  } catch {
    throw new BadRequest("malformed JSON");
  }
}

function applyUpdate(value, upd) {
  const entities = value.entities;
  const idx = entities.findIndex((e) => slugify(e.name) === upd.id);
  if (upd.action === "add") {
    if (idx >= 0) throw new BadRequest("entry already exists; use action 'teach' with its id", 409);
    if (entities.length >= MAX_ENTITIES) throw new BadRequest("dataset is full", 507);
    entities.push({ name: upd.name, v: { ...upd.answers } });
  } else {
    if (idx < 0) throw new BadRequest("unknown id", 404);
    const w = BLEND[upd.action];
    const e = { ...entities[idx], v: { ...(entities[idx].v || {}) } };
    for (const [k, val] of Object.entries(upd.answers)) {
      const old = e.v[k];
      e.v[k] = typeof old === "number" ? Math.round((old * (1 - w) + val * w) * 1e4) / 1e4 : val;
    }
    entities[idx] = e;
  }
  value.gamesPlayed = (value.gamesPlayed || 0) + 1;
  return idx < 0 ? entities.length - 1 : idx;
}

export const config = { api: { bodyParser: { sizeLimit: "4kb" } } };

export default async function handler(req, res) {
  applyCors(res);
  res.setHeader("Cache-Control", "no-store");

  if (req.method === "OPTIONS") { res.status(204).end(); return; }
  if (req.method !== "GET" && req.method !== "POST") {
    res.setHeader("Allow", "GET, POST, OPTIONS");
    res.status(405).json({ error: "Method not allowed" });
    return;
  }
  if (!supabaseConfigured()) {
    res.status(500).json({ error: "Storage not configured." });
    return;
  }

  if (req.method === "GET") {
    try {
      res.status(200).json(publicView(await loadDataset()));
    } catch (err) {
      console.error("cold-read GET", err);
      res.status(500).json({ error: "Failed to read dataset" });
    }
    return;
  }

  try {
    // Every POST attempt (valid or not) counts toward the per-IP limit.
    if (!(await rateLimit(req, res))) {
      res.setHeader("Retry-After", "60");
      res.status(429).json({ error: "Too many updates, slow down" });
      return;
    }
    const body = await readBody(req);
    const upd = validateUpdate(body);
    const value = await loadDataset();
    const idx = applyUpdate(value, upd);
    await kvSet(KEY, value);
    const e = value.entities[idx];
    res.status(200).json({ ok: true, entry: { id: slugify(e.name), name: e.name, v: e.v }, gamesPlayed: value.gamesPlayed, count: value.entities.length });
  } catch (err) {
    if (err instanceof BadRequest) { res.status(err.status).json({ error: err.message }); return; }
    if (err && err.type === "entity.too.large") { res.status(413).json({ error: "payload too large" }); return; }
    console.error("cold-read POST", err);
    res.status(500).json({ error: "Failed to write dataset" });
  }
}
