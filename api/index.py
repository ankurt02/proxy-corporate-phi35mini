import json
import requests
from http.server import BaseHTTPRequestHandler

HF_SPACE_URL = "https://ankurt02-corporate-filter-phi35-mini-merged.hf.space/rewrite"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "message": "Proxy is live",
            "upstream": HF_SPACE_URL
        }).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body)
        except Exception:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return

        try:
            resp = requests.post(HF_SPACE_URL, json=payload, timeout=120)
            raw_text = resp.text

            try:
                data = resp.json()
            except Exception:
                data = {
                    "error": "HF Space did not return valid JSON",
                    "status_code": resp.status_code,
                    "raw_response": raw_text[:2000],
                    "upstream": HF_SPACE_URL
                }

        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e),
                "upstream": HF_SPACE_URL
            }).encode())
            return

        self.send_response(resp.status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())