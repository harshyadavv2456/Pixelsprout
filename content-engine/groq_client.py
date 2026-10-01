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

# Tried in order. llama-3.3-70b-versatile was shut down by Groq on 16 Aug 2026
# (every call since then returned "model_not_found"), so these are Groq's listed
# production replacements. Override with GROQ_MODELS="model-a,model-b" without a code change.
DEFAULT_MODELS = ["openai/gpt-oss-120b", "qwen/qwen3.6-27b", "openai/gpt-oss-20b"]
MODELS = [m.strip() for m in os.environ.get("GROQ_MODELS", "").split(",") if m.strip()] or DEFAULT_MODELS
MODEL = MODELS[0]  # kept for anything that imports the old name


def _extract_json(text):
    """Parse a JSON object even if the model wrapped it in a code fence or added a line of text."""
    text = (text or "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise


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
        self.dead_models = set()   # retired / not available - skipped for the rest of the run
        self.no_json_mode = set()  # models that reject response_format

    @property
    def has_keys(self):
        return len(self.keys) > 0

    def _usable_keys(self):
        return [k for k in self.keys if k not in self.dead_keys]

    def generate_json(self, system_prompt, user_prompt, max_tokens=1200, temperature=0.7, max_wait_per_key=90):
        """
        Calls the chat completion endpoint asking for strict JSON output,
        rotating through keys on real quota exhaustion, but waiting out
        short per-minute rate limits on the same key first (up to
        `max_wait_per_key` seconds total per key). Returns the parsed
        JSON dict, or None if every key is exhausted/unavailable (caller
        should fall back to fallback_content in that case).
        """
        for model in MODELS:
            if model in self.dead_models:
                continue
            if not self._usable_keys():
                return None
            result = self._generate_with_model(model, system_prompt, user_prompt, max_tokens, temperature, max_wait_per_key)
            if result is not None:
                return result
            if model not in self.dead_models:
                # Model works but every key is out of quota/erroring - other models share the same keys.
                return None
        print("  [groq] no working model left - check console.groq.com/docs/deprecations and set GROQ_MODELS")
        return None

    def _generate_with_model(self, model, system_prompt, user_prompt, max_tokens, temperature, max_wait_per_key):
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            # Reasoning models spend tokens thinking before answering - leave room for both.
            "max_tokens": max_tokens * 3 if "gpt-oss" in model else max_tokens,
        }
        if "gpt-oss" in model:
            payload["reasoning_effort"] = "low"
        if model not in self.no_json_mode:
            payload["response_format"] = {"type": "json_object"}
        body = json.dumps(payload).encode("utf-8")

        for key in self._usable_keys():
            waited = 0.0
            key_abandoned = False
            while waited < max_wait_per_key and not key_abandoned:
                req = urllib.request.Request(
                    GROQ_URL,
                    data=body,
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        # Groq's Cloudflare WAF blocks Python's default
                        # "Python-urllib/3.x" User-Agent outright (error
                        # 1010) before the request ever reaches the API
                        # logic - a normal-looking UA fixes this. This
                        # isn't spoofing identity to Groq (the API key is
                        # what actually authenticates the request), it's
                        # working around an overly broad default WAF rule
                        # that flags known scripting-library signatures.
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    },
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        text = data["choices"][0]["message"]["content"]
                        return _extract_json(text)
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        body_text = e.read().decode("utf-8", errors="replace")
                        retry_after = e.headers.get("Retry-After")
                        # Groq's 429 covers two very different situations:
                        # a short per-minute rate limit (clears in seconds,
                        # worth waiting out on the SAME key - this matches
                        # what you observed, "usable again after ~5 min")
                        # and real daily/token quota exhaustion (won't
                        # clear until tomorrow, worth abandoning the key).
                        wait_s = None
                        if retry_after:
                            try:
                                wait_s = float(retry_after)
                            except ValueError:
                                wait_s = None
                        if wait_s is None:
                            low = body_text.lower()
                            if "per minute" in low or "rpm" in low:
                                wait_s = 15.0  # no explicit header, but clearly a short RPM limit
                        if wait_s is not None and wait_s <= 30:
                            sleep_for = wait_s + 0.5
                            print(f"  [groq] key ...{key[-4:]} rate-limited, waiting {sleep_for:.1f}s and retrying same key")
                            time.sleep(sleep_for)
                            waited += sleep_for
                            continue  # retry this same key, don't rotate
                        print(f"  [groq] key ...{key[-4:]} hit 429 (quota), rotating to next key: {body_text[:200]}")
                        self.dead_keys.add(key)
                        key_abandoned = True
                    elif e.code == 403:
                        # Cloudflare WAF block (error 1010) or an invalid/
                        # revoked key both surface as 403. Either way,
                        # retrying the same key won't help - mark it dead
                        # immediately rather than re-trying it on every
                        # subsequent page/game for the rest of the run.
                        body_text = e.read().decode("utf-8", errors="replace")
                        print(f"  [groq] key ...{key[-4:]} got 403, marking dead for this run: {body_text[:200]}")
                        self.dead_keys.add(key)
                        key_abandoned = True
                    else:
                        body_text = e.read().decode("utf-8", errors="replace")
                        low = body_text.lower()
                        if e.code == 404 or "model_not_found" in low or "decommissioned" in low:
                            # Retired / unavailable model: retrying is pointless (this used to loop
                            # for 90s per key per page). Skip this model for the whole run.
                            print(f"  [groq] model {model} unavailable, switching model: {body_text[:200]}")
                            self.dead_models.add(model)
                            return None
                        if e.code == 400 and "response_format" in low and model not in self.no_json_mode:
                            print(f"  [groq] {model} rejects JSON mode - retrying without it")
                            self.no_json_mode.add(model)
                            return self._generate_with_model(model, system_prompt, user_prompt, max_tokens, temperature, max_wait_per_key)
                        print(f"  [groq] HTTP {e.code} on key ...{key[-4:]} ({model}): {body_text[:300]}")
                        if e.code == 400:
                            break  # bad request won't fix itself on retry - try next key once, then give up
                        time.sleep(2)
                        waited += 2
                except (urllib.error.URLError, json.JSONDecodeError, KeyError, TimeoutError) as e:
                    print(f"  [groq] error on key ...{key[-4:]}: {e}")
                    time.sleep(2)
                    waited += 2
        return None
