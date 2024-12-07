import json
from starlette.types import ASGIApp, Receive, Scope, Send

class StandardizeMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            method = scope["method"].upper()

            async def receive_wrapper():
                message = await receive()
                if message.get("type") == "http.request" and message.get("body"):
                    original_body = message["body"].decode("utf-8")
                    try:
                        parsed_body = json.loads(original_body)
                        lowercase_body = self._convert_to_lowercase(parsed_body)
                        new_body = json.dumps(lowercase_body).encode("utf-8")
                        message["body"] = new_body
                        if "content-length" in dict(scope["headers"]).get(b"content-length", b"").decode("utf-8"):
                            new_length = len(new_body)
                            scope["headers"] = [
                                (k, v) for (k, v) in scope["headers"]
                                if k.lower() != b"content-length"
                            ]
                            scope["headers"].append((b"content-length", str(new_length).encode("latin1")))
                    except json.JSONDecodeError:
                        pass
                return message

            await self.app(scope, receive_wrapper, send)
        else:
            await self.app(scope, receive, send)

    @staticmethod
    def _convert_to_lowercase(data):
        if isinstance(data, dict):
            return {k.lower(): StandardizeMiddleware._convert_to_lowercase(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [StandardizeMiddleware._convert_to_lowercase(item) for item in data]
        elif isinstance(data, str):
            return data.lower()
        return data