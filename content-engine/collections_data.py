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


# -- Hand-picked hubs (kind "curated") --
# Written and checked by hand (Studio-approved 23 Oct 2026). generate_collections.py renders these
# straight from this data: no keyword matching, no Groq intro, no SEO Bot intro. Every fact in a
# note comes from that game's live page; edit here, never in the generated HTML.
CURATED_HUBS = [{'slug': 'getting-over-it',
  'display_name': 'Getting Over It',
  'kind': 'curated',
  'curated': True,
  'game_slug': 'getting-over-it',
  'title_tag': 'Games Like Getting Over It - Climbing and Patience Games | Pixelsprout',
  'meta_desc': 'Browser games on Pixelsprout that share the slow, careful climbing of Getting Over It: '
               'hammer climbs, mountain climbs and hard platformers. Free to play, no download needed.',
  'h1': 'Games Like Getting Over It',
  'intro': ['Getting Over It on Pixelsprout is a fan-made Scratch remake by griffpatch, not the original '
            'game. You guide a cat in a flower pot and use a hammer to climb a pile of giant Scratch code '
            'blocks above the water. Every move goes through that hammer, progress is slow, and one slip can '
            'cost you a lot of height. The first load can take a few minutes.'],
  'tips_title': 'Quick tips for Getting Over It',
  'tips_intro': 'These come from our Getting Over It guides:',
  'tips': ['The whole game is played with the mouse. Arrow keys and WASD do nothing, and no clicking is '
           'needed once a run starts.',
           'Hook the hammer head over the top edge of a block before you pull. The pot only moves when the '
           'hammer head is pressing against something.',
           'Use slow, wide sweeps of the mouse, then push the hammer against a block and pull the cursor the '
           'opposite way to move the pot up.',
           'Ease off when the pot lands somewhere flat. The cat keeps some momentum after you stop, so let '
           'it settle before the next move.',
           'A timer in the top right corner runs the whole time.'],
  'next_title': 'Games to try next',
  'next_intro': ['If that mix of awkward control, patience and starting over is what kept you playing, the '
                 'games below are a good next step. Each one is on Pixelsprout, and each short note uses '
                 "only what the game's own page says about it. We grouped them by what they share with "
                 'Getting Over It: climbing with an unusual control, climbing a mountain, or hard levels '
                 'that ask for precise moves.'],
  'sections': [{'heading': 'Climbing with an unusual control',
                'games': [{'title': 'Hammer Climb MinisCrafter',
                           'note': 'This is the closest match on the list if the hammer is what you liked. '
                                   'Its page says you use a hammer to move, swinging back and forth with a '
                                   'friend, and that the goal of each level is to reach the lucky box at the '
                                   'end while watching out for obstacles.',
                           'slug': 'hammer-climb-miniscrafter'},
                          {'title': 'Carrot Climber',
                           'note': 'Its page says a hungry rabbit climbs walls to collect carrots by jumping '
                                   'from one hook to the next. You have to aim each jump carefully, because '
                                   'a missed hook means the rabbit falls, and the page says carrots and '
                                   'coins collected along the way unlock the next level.',
                           'slug': 'carrot-climber'}]},
               {'heading': 'Climbing a mountain',
                'games': [{'title': 'Climb Up',
                           'note': 'Its page describes a climb up a large mountain with slippery surfaces '
                                   'and unpredictable obstacles, and says a gift waits at the summit. It is '
                                   'a good pick if the long climb itself, rather than the hammer, is what '
                                   'kept you coming back.',
                           'slug': 'climb-up'},
                          {'title': 'Mad Climbing',
                           'note': 'Its page says you guide a ninja up tall peaks over difficult terrain, '
                                   'and that precision and speed both matter.',
                           'slug': 'mad-climbing'}]},
               {'heading': 'Hard levels that ask for precision',
                'games': [{'title': 'Bike Mania 2',
                           'note': 'Bike Mania 2 is precision biking over different kinds of terrain, and '
                                   'its page says it has 20 levels. The page puts the focus on balance, '
                                   'control and patience as you work around obstacles, which is close to the '
                                   'careful, physical feel of moving the pot and hammer.',
                           'slug': 'bike-mania-2'},
                          {'title': 'Trap Adventure 2',
                           'note': 'Its page says Trap Adventure 2 has 25 hard platforming levels that ask '
                                   'for precise moves and quick reactions, with a retro look. If what you '
                                   'liked about Getting Over It was a game that does not go easy on you, '
                                   'this is a direct fit.',
                           'slug': 'trap-adventure-2'},
                          {'title': 'Rage Maze Troll Hardest Platformer',
                           'note': 'Its page describes traps, puzzles and very hard jumps, with troll '
                                   'mechanics made to catch you out. According to the page, there are 15 '
                                   'levels, characters to unlock and a Speedrun Mode.',
                           'slug': 'rage-maze-troll-hardest-platformer'}]}],
  'pick_title': 'How to pick one',
  'pick': ['If you liked the hammer, start with Hammer Climb MinisCrafter. If the long climb itself was the '
           'draw, try Climb Up or Mad Climbing. If you want hard levels where every jump has to be exact, go '
           "to Trap Adventure 2 or Rage Maze Troll Hardest Platformer. Carrot Climber's page describes it as "
           'fun for all ages, and Bike Mania 2 is the one to try if you liked careful balance more than '
           'climbing.'],
  'footer_note': 'Not tested on touch screens.',
  'more_links': [['Back to Getting Over It', '/games/getting-over-it.html'],
                 ['Getting Over It tips', '/guides/getting-over-it-tips/'],
                 ['Getting Over It controls', '/guides/getting-over-it-controls/'],
                 ['Hardest platformers on Pixelsprout', '/games-like/hardest-platformers/']]},
 {'slug': 'bubble-up-endless',
  'display_name': 'Bubble Up Endless',
  'kind': 'curated',
  'curated': True,
  'game_slug': 'bubble-up-endless',
  'title_tag': 'Games Like Bubble Up Endless - Bubble Shooter Games | Pixelsprout',
  'meta_desc': 'Bubble shooter and color-matching games on Pixelsprout for fans of Bubble Up Endless, with a '
               'short note on each. Free to play, no download needed.',
  'h1': 'Games Like Bubble Up Endless',
  'intro': ['Bubble Up Endless is a bubble shooter about aim and planning rather than speed. You pop '
            'color-matched balls, read the next color, line up shots along the dotted aiming line and look '
            'for the one bubble holding up a big section. Its page says levels get trickier as you go and '
            'lists power-ups such as bombs and rainbows for setting off chain reactions. A big drop sends '
            'bubbles into the point buckets, and a score multiplier rises when you clear bubbles on '
            'consecutive shots.'],
  'tips_title': 'Quick tips for Bubble Up Endless',
  'tips_intro': 'These come from our Bubble Up Endless guides:',
  'tips': ['Press and hold the left mouse button to aim, move to swing the dotted aiming line, and release '
           'to fire. There is no penalty for taking time to aim.',
           'Check the small bubble beside the launcher. It shows the color coming next, so you can save a '
           'spot for it.',
           'Go for the bubbles that hold a big section in place. In one run, a single shot like that took '
           'the score from 850 to 3,400.',
           'Loose bubbles fall into five buckets worth 50, 100, 150, 100 and 50 points, so the middle bucket '
           'pays the most.',
           'Keep the cluster away from the red dashed line above the launcher. The run ends with FAILED when '
           'it gets there.'],
  'next_title': 'Games to try next',
  'next_intro': ['If you like that shot-by-shot style, the games below are all on Pixelsprout and all ask '
                 "you to aim and match colors in some way. Each short note uses only what the game's own "
                 'page says about it. We grouped them into classic bubble shooters and bubble shooters with '
                 'a theme.'],
  'sections': [{'heading': 'Classic bubble shooters',
                'games': [{'title': 'Puzzlebubble',
                           'note': 'This is the classic setup. Its page says you control a launch pad at the '
                                   'bottom and shoot colored bubbles, and three or more of the same color '
                                   'connected together disappear. The goal it describes is to clear the '
                                   "screen, or meet a level's condition such as collecting items, before the "
                                   'bubbles reach the bottom.',
                           'slug': 'puzzlebubble'},
                          {'title': 'Bubble Shooter POP',
                           'note': 'A 2D bubble shooter where you aim and shoot to clear the colors before '
                                   'they fill the screen. Its page says multipliers and bombs help you score '
                                   'more and set off chain reactions, much like the boosters in Bubble Up '
                                   'Endless.',
                           'slug': 'bubble-shooter-pop'},
                          {'title': 'Bubble Shooter Blast Master',
                           'note': 'Its page says you aim and launch bubbles to make chains and clear each '
                                   'level, and describes the gameplay as intuitive and suited for all ages. '
                                   'It is a straightforward pick if you want more of the same core loop.',
                           'slug': 'bubble-shooter-blast-master'},
                          {'title': 'Sticky Balls - Match 3 Bubble Shooter',
                           'note': 'Its page describes a match-3 bubble shooter where you clear clusters of '
                                   'sticky balls and plan your shots for chain reactions.',
                           'slug': 'sticky-balls-match-3-bubble-shooter'}]},
               {'heading': 'Bubble shooters with a theme',
                'games': [{'title': 'Nebula Bubble Pop',
                           'note': 'A space-themed bubble shooter, and its page says it has 50 levels. You '
                                   'match and pop colorful nebulas to clear the board, and the page says '
                                   'careful aim lets you drop large groups that are no longer attached, '
                                   'which is the same "find the bubble holding it up" idea that drives '
                                   'Bubble Up Endless.',
                           'slug': 'nebula-bubble-pop'},
                          {'title': 'Pop-Pop Kitties',
                           'note': 'A match-3 puzzle shooter where you connect matching cats before they '
                                   'come down or time runs out. Its page lists more than 100 levels and '
                                   'stars to collect.',
                           'slug': 'pop-pop-kitties'},
                          {'title': 'Alien Bubbles',
                           'note': 'Its page says a dinosaur with a launcher pops colorful bubble invaders '
                                   'to stop an alien invasion, choosing shots and using power-ups along the '
                                   'way.',
                           'slug': 'alien-bubbles'},
                          {'title': 'ShipPop Saga',
                           'note': 'You command a ship and shoot and match bubbles to keep them from filling '
                                   'the screen. Its page says the patterns get harder as you go and '
                                   'describes the game as fast-paced, so it is the pick if you want more '
                                   'pressure than Bubble Up Endless gives you.',
                           'slug': 'shippop-saga'}]}],
  'pick_title': 'How to pick one',
  'pick': ['If you want the closest match, start with Puzzlebubble or Bubble Shooter POP. If dropping big '
           'sections is your favorite part, try Nebula Bubble Pop. For a longer run of levels, Pop-Pop '
           "Kitties' page lists more than 100. If you would like a faster pace, try ShipPop Saga. If you "
           'want a theme around the puzzle, Alien Bubbles and Pop-Pop Kitties put a story or a cast of '
           'characters around the same aim-and-match idea.'],
  'footer_note': 'Not tested on touch screens.',
  'more_links': [['Back to Bubble Up Endless', '/games/bubble-up-endless.html'],
                 ['Bubble Up Endless tips', '/guides/bubble-up-endless-tips/'],
                 ['Bubble Up Endless controls', '/guides/bubble-up-endless-controls/'],
                 ['All puzzle games', '/puzzle/']]}]
