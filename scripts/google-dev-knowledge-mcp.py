#!/usr/bin/env python
"""Wrapper: gera Bearer token do Service Account e inicia mcp-remote com --header."""
import json
import os
import sys
import time
import base64
import subprocess
import urllib.request
import urllib.parse

SA_FILE = os.path.expanduser("~/.credentials/google-service-account.json")


def get_access_token():
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    with open(SA_FILE) as f:
        sa = json.load(f)

    now = int(time.time())
    header = base64.urlsafe_b64encode(
        json.dumps({"alg": "RS256", "typ": "JWT"}).encode()
    ).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(
        json.dumps({
            "iss": sa["client_email"],
            "scope": "https://www.googleapis.com/auth/cloud-platform",
            "aud": "https://oauth2.googleapis.com/token",
            "iat": now,
            "exp": now + 3600,
        }).encode()
    ).rstrip(b"=").decode()

    key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    sig = base64.urlsafe_b64encode(
        key.sign(f"{header}.{payload}".encode(), padding.PKCS1v15(), hashes.SHA256())
    ).rstrip(b"=").decode()

    jwt = f"{header}.{payload}.{sig}"
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt,
    }).encode()
    resp = json.loads(urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    ).read())
    return resp["access_token"]


token = get_access_token()

cmd = [
    "npx", "-y", "mcp-remote",
    "https://developerknowledge.googleapis.com/mcp",
    "--header", f"Authorization: Bearer {token}",
]

# os.execvp não funciona corretamente no Windows (não substitui o processo).
# subprocess.run com shell=True resolve npx.cmd no Windows e propaga exit code.
result = subprocess.run(cmd, shell=(os.name == "nt"))
sys.exit(result.returncode)
