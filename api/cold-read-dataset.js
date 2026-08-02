import { supabaseConfigured, kvGet, kvSet, applyCors } from "./_supabase.js";

// Single row, mirrors the shape the offline React prototype expected from
// window.storage: { entities: [...], gamesPlayed: number }. One key, one
// round trip in each direction.
const KEY = "coldread:dataset";

const MAX_BODY_BYTES = 400_000; // guard against runaway payloads

export default async function handler(req, res) {
  applyCors(res);

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }

  if (!supabaseConfigured()) {
    res.status(500).json({
      error:
        "Storage not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in Vercel env vars.",
    });
    return;
  }

  if (req.method === "GET") {
    try {
      const value = await kvGet(KEY);
      if (!value) {
        res.status(200).json({ entities: null, gamesPlayed: 0 });
        return;
      }
      res.status(200).json(value);
    } catch (err) {
      res.status(500).json({ error: "Failed to read dataset", detail: String(err && err.message || err) });
    }
    return;
  }

  if (req.method === "POST") {
    try {
      const body = req.body && typeof req.body === "object" ? req.body : JSON.parse(req.body || "{}");
      const { entities, gamesPlayed } = body;
      if (!Array.isArray(entities)) {
        res.status(400).json({ error: "entities must be an array" });
        return;
      }
      const value = {
        entities,
        gamesPlayed: Number.isFinite(gamesPlayed) ? gamesPlayed : 0,
      };
      if (JSON.stringify(value).length > MAX_BODY_BYTES) {
        res.status(413).json({ error: "Payload too large" });
        return;
      }
      await kvSet(KEY, value);
      res.status(200).json({ ok: true });
    } catch (err) {
      res.status(500).json({ error: "Failed to write dataset", detail: String(err && err.message || err) });
    }
    return;
  }

  res.status(405).json({ error: "Method not allowed" });
}
