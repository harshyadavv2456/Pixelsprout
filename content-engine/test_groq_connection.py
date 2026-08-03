#!/usr/bin/env python3
"""
One tiny API call, clear pass/fail output. Run this locally (with keys as
env vars) or add a temporary step in the workflow to confirm the
Cloudflare/User-Agent fix actually works before running a real batch.

Usage:
  $env:GROQ_API_KEY_1="gsk_..."   (PowerShell)
  python content-engine/test_groq_connection.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from groq_client import GroqRotatingClient


def main():
    client = GroqRotatingClient()
    if not client.has_keys:
        print("FAIL: no GROQ_API_KEY_1..5 found in environment.")
        sys.exit(1)

    print(f"Found {len(client.keys)} key(s). Testing key rotation with a tiny request...")
    result = client.generate_json(
        system_prompt="Respond with ONLY a JSON object, no markdown, no commentary.",
        user_prompt='Write JSON: {"status": "ok", "message": "a 5 word test message"}',
        max_tokens=50,
    )

    if result:
        print("PASS - Groq responded correctly:")
        print(result)
    else:
        print("FAIL - every key was rejected or errored. Check the [groq] log lines above for the reason.")
        sys.exit(1)


if __name__ == "__main__":
    main()
