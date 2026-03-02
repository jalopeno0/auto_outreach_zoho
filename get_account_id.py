import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"

# Refresh access token
form = {
    "refresh_token": os.environ["ZOHO_REFRESH_TOKEN"],
    "client_id": os.environ["ZOHO_CLIENT_ID"],
    "client_secret": os.environ["ZOHO_CLIENT_SECRET"],
    "grant_type": "refresh_token",
}
headers = {"Content-Type": "application/x-www-form-urlencoded"}
r = requests.post(TOKEN_URL, data=form, headers=headers, timeout=30)
print("Token status:", r.status_code)
print("Token resp:", r.text)

access_token = r.json()["access_token"]

# Call Accounts API
url = "https://mail.zoho.com/api/accounts"
headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
r = requests.get(url, headers=headers, timeout=30)
print("Accounts status:", r.status_code)
print("Accounts resp:", r.text)
