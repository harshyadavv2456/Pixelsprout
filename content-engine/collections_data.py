"""
Curated "games like [famous title]" collection pages.

This is deliberately a small, hand-picked list, not auto-generated per
catalog game - these pages exist to rank for searches about famous games
Pixelsprout doesn't host (Subway Surfers, Minecraft, GTA, etc.) and
convert that traffic into plays of similar games Pixelsprout DOES have.
Add more entries here any time; each one becomes /games-like/<slug>/.

category_keywords / title_keywords feed similar_games.find_by_keywords()
against your real catalog - tune these if a collection pulls in bad
matches once you see the generated page.
"""

COLLECTIONS = [
    {
        "slug": "subway-surfers",
        "display_name": "Subway Surfers",
        "category_keywords": ["runner"],
        "title_keywords": ["run", "subway", "dash", "rush"],
    },
    {
        "slug": "temple-run",
        "display_name": "Temple Run",
        "category_keywords": ["runner"],
        "title_keywords": ["run", "temple", "escape", "chase"],
    },
    {
        "slug": "minecraft",
        "display_name": "Minecraft",
        "category_keywords": ["sandbox", "simulation"],
        "title_keywords": ["craft", "block", "steve", "miner", "builder"],
    },
    {
        "slug": "gta",
        "display_name": "GTA",
        "category_keywords": ["action"],
        "title_keywords": ["crime", "gangster", "city", "mafia", "heist"],
    },
    {
        "slug": "among-us",
        "display_name": "Among Us",
        "category_keywords": [],
        "title_keywords": ["impostor", "among", "crewmate"],
    },
    {
        "slug": "fall-guys",
        "display_name": "Fall Guys",
        "category_keywords": ["multiplayer", "party"],
        "title_keywords": ["obstacle", "race", "party", "obby"],
    },
    {
        "slug": "candy-crush",
        "display_name": "Candy Crush",
        "category_keywords": ["match"],
        "title_keywords": ["match", "candy", "sweet", "bubble"],
    },
    {
        "slug": "2048",
        "display_name": "2048",
        "category_keywords": [],
        "title_keywords": ["2048", "merge"],
    },
    {
        "slug": "roblox",
        "display_name": "Roblox",
        "category_keywords": ["simulation", "sandbox"],
        "title_keywords": ["tycoon", "simulator", "obby", "roleplay"],
    },
    {
        "slug": "fortnite",
        "display_name": "Fortnite",
        "category_keywords": ["shooter", "action"],
        "title_keywords": ["battle", "shooter", "royale", "gun"],
    },
    {
        "slug": "flappy-bird",
        "display_name": "Flappy Bird",
        "category_keywords": [],
        "title_keywords": ["flappy", "flap", "bird", "jump"],
    },
    {
        "slug": "snake",
        "display_name": "Snake",
        "category_keywords": [],
        "title_keywords": ["snake"],
    },
    {
        "slug": "solitaire",
        "display_name": "Solitaire",
        "category_keywords": ["board", "card"],
        "title_keywords": ["solitaire", "card"],
    },
    {
        "slug": "chess",
        "display_name": "Chess",
        "category_keywords": ["board", "strategy"],
        "title_keywords": ["chess"],
    },
    {
        "slug": "tetris",
        "display_name": "Tetris",
        "category_keywords": ["puzzle"],
        "title_keywords": ["block", "tetris", "stack"],
    },
    {
        "slug": "cooking-fever",
        "display_name": "Cooking Fever",
        "category_keywords": ["simulation"],
        "title_keywords": ["cooking", "restaurant", "chef", "kitchen"],
    },
    {
        "slug": "geometry-dash",
        "display_name": "Geometry Dash",
        "category_keywords": ["arcade"],
        "title_keywords": ["geometry", "dash", "rhythm"],
    },
    {
        "slug": "stumble-guys",
        "display_name": "Stumble Guys",
        "category_keywords": ["multiplayer", "party"],
        "title_keywords": ["stumble", "race", "obstacle"],
    },
]
