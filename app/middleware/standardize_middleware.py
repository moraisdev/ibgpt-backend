from fastapi import FastAPI
import json

class StandardizeMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope, receive, send):
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
                    except:
                        # Se não for JSON, não faz nada
                        pass
                return message

            response_started = False
            response_headers = []
            response_status = 200
            response_body_chunks = []

            async def send_wrapper(message):
                nonlocal response_started, response_headers, response_status, response_body_chunks

                if message["type"] == "http.response.start":
                    response_started = True
                    response_status = message["status"]
                    response_headers = message.get("headers", [])

                elif message["type"] == "http.response.body":
                    body = message.get("body", b"")
                    response_body_chunks.append(body)

                    if not message.get("more_body", False):
                        final_body = b"".join(response_body_chunks)

                        if method == "GET":
                            try:
                                parsed_body = json.loads(final_body.decode("utf-8"))
                                parsed_body = self._uppercase_values(parsed_body)
                                final_body = json.dumps(parsed_body).encode("utf-8")
                            except:
                                pass

                        final_length = len(final_body)
                        new_headers = []
                        content_length_found = False
                        for (k, v) in response_headers:
                            if k.lower() == b"content-length":
                                new_headers.append((k, str(final_length).encode("latin1")))
                                content_length_found = True
                            else:
                                new_headers.append((k, v))
                        if not content_length_found:
                            new_headers.append((b"content-length", str(final_length).encode("latin1")))

                        start_message = {
                            "type": "http.response.start",
                            "status": response_status,
                            "headers": new_headers
                        }
                        await send(start_message)

                        await send({
                            "type": "http.response.body",
                            "body": final_body,
                            "more_body": False
                        })

                else:
                    await send(message)

            return await self.app(scope, receive_wrapper, send_wrapper)

        return await self.app(scope, receive, send)

    @staticmethod
    def _convert_to_lowercase(data):
        if isinstance(data, dict):
            return {k.lower(): StandardizeMiddleware._convert_to_lowercase(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [StandardizeMiddleware._convert_to_lowercase(item) for item in data]
        elif isinstance(data, str):
            return data.lower()
        return data

    @staticmethod
    def _uppercase_values(data):
        if isinstance(data, dict):
            new_data = {}
            for k, v in data.items():
                if k == "color" and isinstance(v, str):
                    new_data[k] = v.lower()
                else:
                    new_data[k] = StandardizeMiddleware._uppercase_values(v)
            return new_data
        elif isinstance(data, list):
            return [StandardizeMiddleware._uppercase_values(item) for item in data]
        elif isinstance(data, str):
            return data.upper()
        return data
