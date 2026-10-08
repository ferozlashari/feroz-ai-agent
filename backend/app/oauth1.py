"""OAuth 1.0a request signing (Twitter/X) - sirf Python stdlib se, koi extra library nahi chahiye."""
import base64
import hashlib
import hmac
import secrets
import time
import urllib.parse
from typing import Dict, Optional


def _quote(s: str) -> str:
    return urllib.parse.quote(str(s), safe="~")


def build_header(
    method: str,
    url: str,
    consumer_key: str,
    consumer_secret: str,
    token: str,
    token_secret: str,
    extra_params: Optional[Dict[str, str]] = None,
) -> str:
    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": token,
        "oauth_version": "1.0",
    }
    all_params = {**(extra_params or {}), **oauth_params}
    param_str = "&".join(f"{_quote(k)}={_quote(v)}" for k, v in sorted(all_params.items()))
    base_str = "&".join([method.upper(), _quote(url), _quote(param_str)])
    signing_key = f"{_quote(consumer_secret)}&{_quote(token_secret)}"
    signature = base64.b64encode(hmac.new(signing_key.encode(), base_str.encode(), hashlib.sha1).digest()).decode()
    oauth_params["oauth_signature"] = signature
    header = "OAuth " + ", ".join(f'{_quote(k)}="{_quote(v)}"' for k, v in sorted(oauth_params.items()))
    return header
