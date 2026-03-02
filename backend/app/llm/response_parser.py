"""Response Parser"""


class ResponseParser:
    @staticmethod
    def parse_response(response: str) -> dict:
        return {"text": response, "sections": response.split("\n\n")}


response_parser = ResponseParser()
