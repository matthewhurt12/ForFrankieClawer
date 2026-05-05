#!/usr/bin/env python3
"""
eBay OAuth Token Test - Application Access Token (Client Credentials)
Loads credentials from credentials/ebay-sandbox.json
Prints only: token received status, expires_in, scopes
"""

import json
import requests
import base64
from pathlib import Path


def load_credentials():
    """Load eBay credentials from JSON file."""
    creds_path = Path("credentials/ebay-sandbox.json")
    with open(creds_path) as f:
        return json.load(f)


def get_application_token(app_id, cert_id, environment="sandbox"):
    """
    Get application access token using client credentials flow.
    This token is for public API calls (Browse, etc.) without user context.
    """
    # Sandbox vs Production OAuth endpoints
    if environment == "sandbox":
        token_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
    else:
        token_url = "https://api.ebay.com/identity/v1/oauth2/token"
    
    # Basic auth header: base64(client_id:client_secret)
    credentials = f"{app_id}:{cert_id}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_credentials}"
    }
    
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()
    
    return response.json()


def main():
    print("eBay Application Token Test")
    print("=" * 50)
    
    # Load credentials
    creds = load_credentials()
    print(f"Environment: {creds['environment']}")
    print(f"App Name: {creds['app_name']}")
    print()
    
    # Get token
    try:
        token_response = get_application_token(
            creds['app_id'],
            creds['cert_id'],
            creds['environment']
        )
        
        print("✓ Token received successfully")
        print(f"Expires in: {token_response.get('expires_in')} seconds ({token_response.get('expires_in') // 3600} hours)")
        print(f"Token type: {token_response.get('token_type')}")
        
        # Don't print the actual token or scopes (might contain sensitive info)
        print()
        print("Token is ready for API calls.")
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ Failed to get token: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    main()
