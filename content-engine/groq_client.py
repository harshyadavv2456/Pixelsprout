"""
Thin Groq API wrapper with automatic key rotation.

Reads up to 5 keys from env vars GROQ_API_KEY_1 .. GROQ_API_KEY_5. On a
rate-limit/quota response (HTTP 429, or Groq's daily-token-limit error),
it moves to the next key automatically and retries the same request -
so a full day's generation run can burn through 5 keys' worth of free
quota before actually failing.

If NO keys are configured at all, generate() falls back to a deterministic
template-based placeholder (see fallback_content.py) so the rest of the
pipeline (HTML rendering, sitemap updates, internal linking, GitHub Actions
wiring) can be built, tested, and reviewed before you've wired any real
API keys in.
"""

import json
import os
import time
import urllib.request
import urllib.error

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Ordered by general writing-quality reputation among Groq's currently
# hosted open models. Change this if Groq adds/retires models - nothing
# else in the pipeline depends on the exact model name.
MODEL = "llama-3.3-70b-versatile"


def _load_keys():
    keys = []
    for i in range(1, 6):
        k = os.environ.get(f"GROQ_API_KEY_{i}", "").strip()
        if k:
            keys.append(k)
    return keys


class GroqRotatingClient:
    def __init__(self):
        self.keys = _load_keys()
        self.dead_keys = set()

    @property
    def has_keys(self):
        return len(self.keys) > 0

    def _usable_keys(self):
        return [k for k in self.keys if k not in self.dead_keys]

    def generate_json(self, system_prompt, user_prompt, max_tokens=1200, temperature=0.7, retries_per_key=1):
        """
        Calls the chat completion endpoint asking for strict JSON output,
        rotating through keys on quota/rate-limit errors. Returns the
        parsed JSON dict, or None if every key is exhausted/unavailable
        (caller should fall back to fallback_content in that case).
        """
        usable = self._usable_keys()
        if not usable:
            return None

        body = json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }).encode("utf-8")

        for key in usable:
            for attempt in range(retries_per_key):
                req = urllib.request.Request(
                    GROQ_URL,
                    data=body,
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        text = data["choices"][0]["message"]["content"]
                        return json.loads(text)
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        # Quota/rate limit on this key - mark it dead for
                        # the rest of this run and move to the next key.
                        print(f"  [groq] key ...{key[-4:]} hit 429, rotating to next key")
                        self.dead_keys.add(key)
                        break
                    else:
                        body_text = e.read().decode("utf-8", errors="replace")
                        print(f"  [groq] HTTP {e.code} on key ...{key[-4:]}: {body_text[:300]}")
                        time.sleep(2)
                except (urllib.error.URLError, json.JSONDecodeError, KeyError, TimeoutError) as e:
                    print(f"  [groq] error on key ...{key[-4:]}: {e}")
                    time.sleep(2)
        return None
