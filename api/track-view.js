import { supabaseConfigured, rpcCall, applyCors } from "./_supabase.js";

// Fire-and-forget: called once per real game-page load (not the tool
// pages, which are pinned separately). Deliberately fails soft - a broken
// view counter should never break a page load for a visitor.
export default async function handler(req, res) {
  applyCors(res);

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }
  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }
  if (!supabaseConfigured()) {
    res.status(200).json({ ok: false });
    return;
  }

  try {
    const body = req.body && typeof req.body === "object" ? req.body : JSON.parse(req.body || "{}");
    const slug = String(body.slug || "").slice(0, 200);
    // Slugs are always lowercase-kebab in this catalog - reject anything
    // else rather than trying to sanitize it.
    if (!slug || !/^[a-z0-9-]+$/.test(slug)) {
      res.status(400).json({ error: "invalid slug" });
      return;
    }
    await rpcCall("increment_view", { p_slug: slug });
    res.status(200).json({ ok: true });
  } catch (err) {
    res.status(200).json({ ok: false });
  }
}
