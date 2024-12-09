import json
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import Headers

class StandardizeMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

        self.exclude_keys = {
            "refresh_token",
            "access_token",
            "token_type",
            "email",
            "password",
            "current_password",
            "new_password",
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            content_type = headers.get("content-type", "")

            if "application/json" in content_type.lower():
                async def receive_wrapper():
                    message = await receive()
                    if message.get("type") == "http.request" and message.get("body"):
                        try:
                            original_body = message["body"].decode("utf-8")
                            parsed_body = json.loads(original_body)
                            lowercase_body = self._convert_to_lowercase(parsed_body)
                            new_body = json.dumps(lowercase_body).encode("utf-8")
                            message["body"] = new_body

                            new_length = len(new_body)

                            scope["headers"] = [
                                (k, v)
                                for (k, v) in scope["headers"]
                                if k.lower() != b"content-length"
                            ]
                            scope["headers"].append(
                                (b"content-length", str(new_length).encode("latin1"))
                            )
                        except json.JSONDecodeError:
                            pass
                    return message

                await self.app(scope, receive_wrapper, send)
            else:
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    def _convert_to_lowercase(self, data):
        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                if k.lower() in self.exclude_keys:
                    new_dict[k] = v
                else:
                    new_key = k.lower()
                    new_dict[new_key] = self._convert_to_lowercase(v)
            return new_dict
        elif isinstance(data, list):
            return [self._convert_to_lowercase(item) for item in data]
        elif isinstance(data, str):
            return data.lower()
        else:
            return data