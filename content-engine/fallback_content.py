"""
Fallback content used when no Groq keys are configured, or every key has
hit its quota mid-run. Deliberately clearly-templated, not meant to be
published as-is for SEO - its job is letting you verify the whole
pipeline (page layout, internal linking, sitemap, GitHub Actions wiring)
works correctly before spending any real API quota, and to keep a run
from hard-failing if Groq is temporarily unavailable.

check_is_fallback() lets generate_guides.py tag fallback-generated pages
so they can be found and regenerated later once quota is available again.
"""

FALLBACK_MARKER = "<!-- fallback-content -->"


def fallback_tips(game):
    return {
        "intro": f"Getting started with {game['title']}? Here's what to focus on early.",
        "tips": [
            f"Learn the core controls before chasing a high score in {game['title']}.",
            "Take it slow on your first few runs to understand the game's rhythm.",
            "Watch for patterns - most challenges repeat in a predictable way.",
            "Don't rush upgrades or purchases until you understand what matters most.",
            "Replay early levels once you've learned the mechanics - scores improve fast.",
        ],
        "conclusion": f"With a bit of practice, {game['title']} becomes much easier to pick up.",
    }


def fallback_controls(game):
    return {
        "intro": f"Here's how to control {game['title']} on both desktop and mobile.",
        "desktop": "Use your mouse and keyboard as prompted on-screen when the game loads.",
        "mobile": "Tap and swipe directly on the game screen - most controls map to simple touch gestures.",
        "tips": [
            "Fullscreen mode usually makes touch controls more accurate.",
            "If controls feel unresponsive, try reloading the page once.",
        ],
    }


def fallback_beginner_guide(game):
    return {
        "intro": f"New to {game['title']}? This covers what you need to know before your first playthrough.",
        "what_it_is": f"{game['title']} is a {game['category'].lower()} game you can play instantly in your browser, no download required.",
        "first_steps": [
            "Start the game and get familiar with the main screen.",
            "Play through the first level or round without worrying about your score.",
            "Check the in-game instructions if you're unsure what to do next.",
        ],
        "who_its_for": f"Fans of {game['category'].lower()} games looking for something quick to play.",
    }


def fallback_similar_intro(game):
    return {
        "intro": f"If you enjoy {game['title']}, here are more {game['category'].lower()} games worth trying on Pixelsprout.",
    }


def fallback_collection_intro(display_name):
    return {
        "intro": f"Looking for games like {display_name}? Here's a hand-picked list you can play free, right in your browser.",
    }
