#!/usr/bin/env python3
"""
ONE-TIME script — run this on your own machine (not GitHub Actions).
Authorizes Pixelsprout's Pinterest app for your account and prints the
refresh token you need to save as a GitHub Actions secret.

Before running: fill in CLIENT_SECRET below with your Pinterest app secret.
"""

import base64
import http.server
import json
import urllib.parse
import urllib.request
import webbrowser

# ---- FILL THIS IN ----
CLIENT_ID = "1595676"
CLIENT_SECRET = "PASTE_YOUR_APP_SECRET_HERE"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "boards:read,pins:read,pins:write"

auth_code = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if "code" in params:
            auth_code = params["code"][0]
            self.wfile.write(b"<h1>Authorized. You can close this tab and check your terminal.</h1>")
        else:
            self.wfile.write(b"<h1>No code received - check your terminal for details.</h1>")

    def log_message(self, format, *args):
        pass


def main():
    if "PASTE_YOUR" in CLIENT_SECRET:
        print("ERROR: fill in CLIENT_SECRET at the top of this script first.")
        print("Find it on your Pinterest app's API keys page.")
        return

    auth_url = (
        "https://www.pinterest.com/oauth/"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
        "&response_type=code"
        f"&scope={urllib.parse.quote(SCOPES, safe=',')}"
    )

    print("Opening your browser to authorize the app...")
    print("If it doesn't open automatically, paste this URL into your browser:\n")
    print(auth_url)
    print()
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    server = http.server.HTTPServer(("localhost", 8080), CallbackHandler)
    print("Waiting for you to click 'Allow' in the browser...")
    server.handle_request()

    if not auth_code:
        print("ERROR: no authorization code received. Try running this again.")
        return

    print("Got authorization code. Exchanging for tokens...")

    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }).encode()

    req = urllib.request.Request(
        "https://api.pinterest.com/v5/oauth/token",
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())

    print()
    print("=" * 60)
    print("SUCCESS. Save this as a GitHub Actions secret:")
    print("=" * 60)
    print(f"PINTEREST_REFRESH_TOKEN = {result.get('refresh_token')}")
    print("=" * 60)
    print()
    print("Go to: your GitHub repo -> Settings -> Secrets and variables -> Actions")
    print("-> New repository secret -> name it PINTEREST_REFRESH_TOKEN, paste the value above.")
    print()
    print("Also add these two secrets (same page):")
    print(f"PINTEREST_APP_ID = {CLIENT_ID}")
    print("PINTEREST_APP_SECRET = (your app secret, same one you pasted above)")


if __name__ == "__main__":
    main()
