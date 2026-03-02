# zoho_mail.py
import os
import time
import requests
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

# Load .env from same directory
load_dotenv(Path(__file__).with_name(".env"))

TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
MAIL_BASE = "https://mail.zoho.com"


class ZohoMailClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        account_id: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.account_id = account_id

        self._access_token: Optional[str] = None
        self._access_token_expiry: float = 0.0
        self._drafts_folder_id_cache: Optional[str] = None

    # -----------------------------
    # Auth
    # -----------------------------
    def _refresh_access_token(self) -> str:
        if self._access_token and time.time() < self._access_token_expiry - 60:
            return self._access_token

        form = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = requests.post(TOKEN_URL, data=form, headers=headers, timeout=30)

        if r.status_code != 200:
            raise RuntimeError(f"Token refresh failed ({r.status_code}): {r.text}")

        data = r.json()
        if "access_token" not in data:
            raise RuntimeError(f"Failed to refresh access token: {data}")

        self._access_token = data["access_token"]
        self._access_token_expiry = time.time() + int(data.get("expires_in", 3600))
        return self._access_token

    def _headers_json(self) -> Dict[str, str]:
        token = self._refresh_access_token()
        return {
            "Authorization": f"Zoho-oauthtoken {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    # -----------------------------
    # HTTP helpers
    # -----------------------------
    def _post_json(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(url, headers=self._headers_json(), json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"Zoho API POST failed ({r.status_code}): {r.text}")
        try:
            return r.json()
        except Exception:
            return {"status_code": r.status_code, "text": r.text}

    def _get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        r = requests.get(url, headers=self._headers_json(), params=params, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"Zoho API GET failed ({r.status_code}): {r.text}")
        try:
            return r.json()
        except Exception:
            return {"status_code": r.status_code, "text": r.text}

    # -----------------------------
    # Send Immediately
    # -----------------------------
    def send_email(
        self,
        from_addr: str,
        to_addr: str,
        subject: str,
        content: str,
        mail_format: str = "plaintext",
    ) -> Dict[str, Any]:

        content_norm = str(content).replace("\r\n", "\n").replace("\n", "\r\n")

        url = f"{MAIL_BASE}/api/accounts/{self.account_id}/messages"
        payload = {
            "fromAddress": from_addr,
            "toAddress": to_addr,
            "subject": subject,
            "content": content_norm,
            "mailFormat": mail_format,
        }

        return self._post_json(url, payload)

    # -----------------------------
    # Create Draft
    # -----------------------------
    def create_draft(
        self,
        from_addr: str,
        to_addr: str,
        subject: str,
        content: str,
        mail_format: str = "plaintext",
    ) -> Dict[str, Any]:

        content_norm = str(content).replace("\r\n", "\n").replace("\n", "\r\n")

        url = f"{MAIL_BASE}/api/accounts/{self.account_id}/messages"
        payload = {
            "fromAddress": from_addr,
            "toAddress": to_addr,
            "subject": subject,
            "content": content_norm,
            "mode": "draft",
            "mailFormat": mail_format,
        }

        return self._post_json(url, payload)

    # -----------------------------
    # Send Draft (by message ID)
    # -----------------------------
    def send_draft(self, message_id: str) -> Dict[str, Any]:
        url = f"{MAIL_BASE}/api/accounts/{self.account_id}/messages/{message_id}/send"
        return self._post_json(url, payload={})


def from_env() -> ZohoMailClient:
    required = [
        "ZOHO_CLIENT_ID",
        "ZOHO_CLIENT_SECRET",
        "ZOHO_REFRESH_TOKEN",
        "ZOHO_ACCOUNT_ID",
    ]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"Missing env vars in .env: {missing}")

    return ZohoMailClient(
        client_id=os.environ["ZOHO_CLIENT_ID"].strip(),
        client_secret=os.environ["ZOHO_CLIENT_SECRET"].strip(),
        refresh_token=os.environ["ZOHO_REFRESH_TOKEN"].strip(),
        account_id=os.environ["ZOHO_ACCOUNT_ID"].strip(),
    )
