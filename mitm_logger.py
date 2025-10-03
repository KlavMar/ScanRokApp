# mitm_logger.py
# Usage: mitmdump -s mitm_logger.py -p 8080
from mitmproxy import http
from mitmproxy import ctx
import os
import json
import base64
import time
import re

OUTDIR = "logs"
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)

# mots-clés utiles à surveiller dans les URLs / endpoints
KEYWORDS = ["player", "profile", "governor", "ranking", "leaderboard", "getPlayer", "get_rank", "playerInfo", "alliance"]

def safe_filename(s: str) -> str:
    # créer un nom de fichier sûr
    return re.sub(r'[^0-9A-Za-z_.-]', '_', s)[:200]

def save_text(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)

def save_bytes(path, data: bytes):
    with open(path, "wb") as f:
        f.write(data)

def timestamp():
    return time.strftime("%Y%m%d_%H%M%S")

class LoggerAddon:
    def __init__(self):
        self.count = 0

    def request(self, flow: http.HTTPFlow) -> None:
        # optional: log request brief
        url = flow.request.pretty_url
        if any(k.lower() in url.lower() for k in KEYWORDS):
            ctx.log.info(f"[REQUEST KEYWORD] {url}")

    def response(self, flow: http.HTTPFlow) -> None:
        self.count += 1
        req = flow.request
        resp = flow.response

        # meta filename
        safe_url = safe_filename(req.pretty_url)
        base = f"{OUTDIR}/{timestamp()}_{self.count}_{safe_url}"

        # save request headers/body
        req_meta = {
            "method": req.method,
            "url": req.pretty_url,
            "host": req.host,
            "path": req.path,
            "headers": dict(req.headers),
        }
        try:
            req_body = req.get_text(strict=False)
        except Exception:
            req_body = None
        req_meta["body"] = req_body
        save_text(base + ".request.json", json.dumps(req_meta, ensure_ascii=False, indent=2))

        # save response headers
        resp_meta = {
            "status_code": resp.status_code,
            "reason": resp.reason,
            "headers": dict(resp.headers),
            "url": req.pretty_url
        }

        # try to detect JSON
        content_type = resp.headers.get("Content-Type", "")
        raw = resp.raw_content
        try:
            if "application/json" in content_type.lower():
                text = resp.get_text(strict=False)
                parsed = json.loads(text)
                save_text(base + ".response.json", json.dumps(parsed, ensure_ascii=False, indent=2))
                resp_meta["saved_as"] = base + ".response.json"
            elif "text/" in content_type.lower() or "application/" in content_type.lower():
                # try best-effort JSON detection
                text = resp.get_text(strict=False)
                try:
                    parsed = json.loads(text)
                    save_text(base + ".response.json", json.dumps(parsed, ensure_ascii=False, indent=2))
                    resp_meta["saved_as"] = base + ".response.json"
                except Exception:
                    # save raw text
                    save_text(base + ".response.txt", text)
                    resp_meta["saved_as"] = base + ".response.txt"
            else:
                # binary or unknown: save base64
                b64 = base64.b64encode(raw).decode("ascii")
                save_text(base + ".response.b64", b64)
                resp_meta["saved_as"] = base + ".response.b64"
        except Exception as e:
            # fallback binary
            b64 = base64.b64encode(raw).decode("ascii")
            save_text(base + ".response.b64", b64)
            resp_meta["saved_as"] = base + ".response.b64"
            ctx.log.warn(f"Erreur sauvegarde réponse: {e}")

        # save metadata
        save_text(base + ".meta.json", json.dumps(resp_meta, ensure_ascii=False, indent=2))

        # console highlight for suspicious URLs
        if any(k.lower() in req.pretty_url.lower() for k in KEYWORDS):
            ctx.log.info(f"[RESPONSE KEYWORD] {req.pretty_url} -> {resp_meta['saved_as']}")

addons = [
    LoggerAddon()
]
