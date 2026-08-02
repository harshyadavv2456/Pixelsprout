import { supabaseConfigured, restGet, applyCors } from "./_supabase.js";

export default async function handler(req, res) {
  applyCors(res);

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return;
  }
  if (!supabaseConfigured()) {
    res.status(200).json({ games: [] }); // fail soft - homepage falls back to its static list
    return;
  }

  try {
    const rows = await restGet("game_views?select=slug,views&order=views.desc&limit=20");
    res.status(200).json({ games: rows });
  } catch (err) {
    res.status(200).json({ games: [] });
  }
}
