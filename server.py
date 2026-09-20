import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


load_env_file()

HOST = "127.0.0.1"
PORT = 8000
OPENAI_URL = "https://api.openai.com/v1/responses"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TUTOR_INSTRUCTIONS = """You are a patient Precalculus Tutor.
Use a Socratic, hint-first teaching style. Never give the final answer or a complete worked solution in your first response, even when the student asks directly. Start with one useful observation, a question, or the smallest next step. Ask the student to try it. If they ask for the next hint, give exactly one more concrete step, still stopping before the final answer. Only provide a complete solution after the student has explicitly asked for the answer or shown substantial work, and explain the reasoning clearly. Check their work when they share it. Use plain text math that is easy to read in a chat. Do not pretend to have seen work that was not provided."""


def send_json(handler, status, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def response_text(payload):
    if payload.get("output_text"):
        return payload["output_text"]

    parts = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                parts.append(content.get("text", ""))
    return "\n".join(parts).strip()


class ProoflineHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/chat":
            send_json(self, 404, {"error": "Not found"})
            return

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            send_json(self, 500, {"error": "OPENAI_API_KEY is not configured on the server."})
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            request_data = json.loads(self.rfile.read(length))
            messages = request_data.get("messages", [])
            if not isinstance(messages, list) or not messages:
                raise ValueError("A non-empty messages list is required.")
            if len(messages) > 40:
                messages = messages[-40:]

            body = json.dumps({
                "model": MODEL,
                "instructions": TUTOR_INSTRUCTIONS,
                "input": messages,
                "temperature": 0.4,
            }).encode("utf-8")
            request = Request(
                OPENAI_URL,
                data=body,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))

            text = response_text(result)
            if not text:
                raise RuntimeError("OpenAI returned no text.")
            send_json(self, 200, {"text": text})
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(detail).get("error", {}).get("message", detail)
            except json.JSONDecodeError:
                pass
            send_json(self, error.code, {"error": detail})
        except (URLError, TimeoutError) as error:
            send_json(self, 502, {"error": f"Could not reach OpenAI: {error}"})
        except (ValueError, json.JSONDecodeError) as error:
            send_json(self, 400, {"error": str(error)})
        except Exception as error:
            send_json(self, 500, {"error": str(error)})

    def log_message(self, format, *args):
        if self.path.startswith("/api/"):
            super().log_message(format, *args)


if __name__ == "__main__":
    print(f"Precalculus Tutor running at http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), ProoflineHandler).serve_forever()