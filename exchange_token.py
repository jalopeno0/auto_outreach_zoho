import argparse
import sys
import requests


def main():
    parser = argparse.ArgumentParser(description="Exchange Zoho GRANT TOKEN for access_token + refresh_token.")
    parser.add_argument("--client_id", required=True, help="Zoho OAuth Client ID")
    parser.add_argument("--client_secret", required=True, help="Zoho OAuth Client Secret")
    parser.add_argument("--grant_token", required=True, help="Zoho Grant Token (generated in API Console)")
    parser.add_argument(
        "--accounts_domain",
        default="https://accounts.zoho.com",
        help="Zoho accounts domain. Examples: https://accounts.zoho.com, https://accounts.zoho.eu, https://accounts.zoho.in",
    )
    args = parser.parse_args()

    url = f"{args.accounts_domain.rstrip('/')}/oauth/v2/token"

    data = {
        "grant_type": "authorization_code",
        "client_id": args.client_id.strip(),
        "client_secret": args.client_secret.strip(),
        "code": args.grant_token.strip(),
    }

    r = requests.post(url, data=data, timeout=30)
    print("Status:", r.status_code)
    print("Response:", r.text)

    if r.status_code != 200:
        sys.exit(1)

    try:
        j = r.json()
    except Exception:
        sys.exit(1)

    # Print copy/paste-ready lines for .env
    if "refresh_token" in j:
        print("\nCopy into your .env:")
        print(f"ZOHO_CLIENT_ID={args.client_id.strip()}")
        print(f"ZOHO_CLIENT_SECRET={args.client_secret.strip()}")
        print(f"ZOHO_REFRESH_TOKEN={j['refresh_token']}")
    else:
        print("\nNo refresh_token returned. This usually means:")
        print("- You reused a grant token, or it expired (grant tokens expire quickly)")
        print("- The client is not configured as a Self Client correctly")


if __name__ == "__main__":
    main()