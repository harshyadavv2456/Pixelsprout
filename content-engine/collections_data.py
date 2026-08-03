"""
Curated collection pages, two kinds:

  "versus" - "Games Like [Famous Title]" - targets searches for games
             Pixelsprout doesn't host, converts to plays of similar
             catalog games.
  "best"   - "Best [Category] Games" - global genre hub pages, not tied
             to any specific famous title.

Both are a small, hand-picked list, not auto-generated per catalog game.
Add more entries any time; the generator picks them up automatically.
category_keywords/title_keywords feed similar_games.find_by_keywords()
against the real catalog - category_keywords should match real category
folder slugs where possible (see content-engine/README.md for the
verified list) so any auto-added category cross-link stays accurate.
"""

COLLECTIONS = [
    {"slug": "subway-surfers", "display_name": "Subway Surfers", "kind": "versus",
     "category_keywords": ["runner"], "title_keywords": ["run", "subway", "dash", "rush"]},
    {"slug": "temple-run", "display_name": "Temple Run", "kind": "versus",
     "category_keywords": ["runner"], "title_keywords": ["run", "temple", "escape", "chase"]},
    {"slug": "minecraft", "display_name": "Minecraft", "kind": "versus",
     "category_keywords": ["sandbox", "simulation"], "title_keywords": ["craft", "block", "steve", "miner", "builder"]},
    {"slug": "gta", "display_name": "GTA", "kind": "versus",
     "category_keywords": ["action"], "title_keywords": ["crime", "gangster", "city", "mafia", "heist"]},
    {"slug": "among-us", "display_name": "Among Us", "kind": "versus",
     "category_keywords": [], "title_keywords": ["impostor", "among", "crewmate"]},
    {"slug": "fall-guys", "display_name": "Fall Guys", "kind": "versus",
     "category_keywords": ["multiplayer", "party"], "title_keywords": ["obstacle", "race", "party", "obby"]},
    {"slug": "candy-crush", "display_name": "Candy Crush", "kind": "versus",
     "category_keywords": ["match-3"], "title_keywords": ["match", "candy", "sweet", "bubble"]},
    {"slug": "2048", "display_name": "2048", "kind": "versus",
     "category_keywords": ["2048"], "title_keywords": ["2048", "merge"]},
    {"slug": "roblox", "display_name": "Roblox", "kind": "versus",
     "category_keywords": ["simulation"], "title_keywords": ["tycoon", "simulator", "obby", "roleplay"]},
    {"slug": "fortnite", "display_name": "Fortnite", "kind": "versus",
     "category_keywords": ["shooter", "action"], "title_keywords": ["battle", "shooter", "royale", "gun"]},
    {"slug": "flappy-bird", "display_name": "Flappy Bird", "kind": "versus",
     "category_keywords": [], "title_keywords": ["flappy", "flap", "bird", "jump"]},
    {"slug": "snake", "display_name": "Snake", "kind": "versus",
     "category_keywords": [], "title_keywords": ["snake"]},
    {"slug": "solitaire", "display_name": "Solitaire", "kind": "versus",
     "category_keywords": ["board"], "title_keywords": ["solitaire", "card"]},
    {"slug": "chess", "display_name": "Chess", "kind": "versus",
     "category_keywords": ["board", "strategy"], "title_keywords": ["chess"]},
    {"slug": "tetris", "display_name": "Tetris", "kind": "versus",
     "category_keywords": [], "title_keywords": ["block", "tetris", "stack"]},
    {"slug": "cooking-fever", "display_name": "Cooking Fever", "kind": "versus",
     "category_keywords": ["simulation"], "title_keywords": ["cooking", "restaurant", "chef", "kitchen"]},
    {"slug": "geometry-dash", "display_name": "Geometry Dash", "kind": "versus",
     "category_keywords": ["arcade"], "title_keywords": ["geometry", "dash", "rhythm"]},
    {"slug": "stumble-guys", "display_name": "Stumble Guys", "kind": "versus",
     "category_keywords": ["multiplayer"], "title_keywords": ["stumble", "race", "obstacle"]},

    # -- Global "Best X games" collections --
    {"slug": "best-racing-games", "display_name": "Racing Games", "kind": "best",
     "category_keywords": ["racing", "car", "driving"], "title_keywords": []},
    {"slug": "best-offline-games", "display_name": "Offline-Friendly Games", "kind": "best",
     "category_keywords": ["board", "brain"], "title_keywords": ["solitaire", "chess", "puzzle"]},
    {"slug": "best-browser-games", "display_name": "Browser Games", "kind": "best",
     "category_keywords": ["arcade", "action", "casual"], "title_keywords": []},
    {"slug": "best-games-for-kids", "display_name": "Games for Kids", "kind": "best",
     "category_keywords": ["kids", "animal"], "title_keywords": []},
    {"slug": "hardest-platformers", "display_name": "Platformer Games", "kind": "best",
     "category_keywords": ["platformer"], "title_keywords": ["trap", "impossible", "hard", "escape"]},
    {"slug": "best-endless-runners", "display_name": "Endless Runner Games", "kind": "best",
     "category_keywords": ["runner"], "title_keywords": ["run", "dash", "endless"]},
    {"slug": "best-puzzle-games", "display_name": "Puzzle Games", "kind": "best",
     "category_keywords": ["board", "brain"], "title_keywords": ["puzzle", "match"]},
    {"slug": "best-multiplayer-games", "display_name": "Multiplayer Games", "kind": "best",
     "category_keywords": ["two-player", "battle"], "title_keywords": ["multiplayer"]},
]
