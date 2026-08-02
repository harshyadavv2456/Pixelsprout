// Tiny helper around Supabase's auto-generated REST API (PostgREST). No
// SDK, no npm dependency, no build step — plain fetch calls against one
// table, same "add only what's needed" philosophy as the rest of this site.
//
// Requires two env vars set in Vercel → Settings → Environment Variables:
//   SUPABASE_URL              e.g. https://abcxyz.supabase.co
//   SUPABASE_SERVICE_ROLE_KEY the "service_role" key (NOT the anon key)
//
// The service_role key bypasses Row Level Security, which is fine here
// because it only ever runs inside this serverless function — it is never
// sent to the browser. The frontend pages only ever talk to /api/..., never
// to Supabase directly.
//
// Expects one table, created once via the Supabase SQL editor:
//
//   create table kv_store (
//     key text primary key,
//     value jsonb not null,
//     updated_at timestamptz not null default now()
//   );

const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

export function supabaseConfigured() {
  return Boolean(SUPABASE_URL && SERVICE_ROLE_KEY);
}

function headers(extra) {
  return {
    apikey: SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SERVICE_ROLE_KEY}`,
    ...extra,
  };
}

// Returns the parsed JS value stored at `key`, or null if no row exists yet.
export async function kvGet(key) {
  const url = `${SUPABASE_URL}/rest/v1/kv_store?key=eq.${encodeURIComponent(key)}&select=value`;
  const r = await fetch(url, {
    headers: headers({ Accept: "application/vnd.pgrst.object+json" }),
  });
  if (r.status === 406) return null; // PGRST116: no row found (single-object accept header)
  if (!r.ok) {
    const body = await r.text().catch(() => "");
    throw new Error(`Supabase GET failed: ${r.status} ${body}`);
  }
  const data = await r.json();
  return data.value ?? null;
}

// Upserts (insert-or-update) the row for `key` with `value` (any JSON-able JS value).
export async function kvSet(key, value) {
  const url = `${SUPABASE_URL}/rest/v1/kv_store`;
  const r = await fetch(url, {
    method: "POST",
    headers: headers({
      "Content-Type": "application/json",
      Prefer: "resolution=merge-duplicates,return=minimal",
    }),
    body: JSON.stringify([{ key, value, updated_at: new Date().toISOString() }]),
  });
  if (!r.ok) {
    const body = await r.text().catch(() => "");
    throw new Error(`Supabase UPSERT failed: ${r.status} ${body}`);
  }
  return true;
}

export function applyCors(res) {
  // These endpoints serve non-sensitive, self-learning game/gift data and
  // are called from both the apex domain and the gifts.* subdomain, so an
  // open CORS policy avoids subdomain cookie/origin headaches entirely.
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}
