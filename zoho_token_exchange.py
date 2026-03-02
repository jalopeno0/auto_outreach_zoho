import requests

CLIENT_ID = "1000.6D1CMNEQ1PYR90V05EV0Z23XGI7ZRJ"
CLIENT_SECRET = "f8cbc683f5682cf2ba3c9e8491a874d3ca5066bee2"
GRANT_TOKEN = "1000.ab6d1079b7c3e693685b36d6cca67754.c4059877b81e60771d995bd63548b0ef"

url = "https://accounts.zoho.com/oauth/v2/token"  # change if not US region

params = {
    "grant_type": "authorization_code",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "code": GRANT_TOKEN,
}

r = requests.post(url, params=params, timeout=30)
print(r.status_code)
print(r.json())
