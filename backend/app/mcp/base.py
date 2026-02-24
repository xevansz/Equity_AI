import httpx


class BaseMCP:
  """Base MCP Connector"""

  def __init__(self, base_url: str, api_key: str = None):
    self.base_url = base_url.rstrip("/")
    self.api_key = api_key
    self.client = httpx.AsyncClient(timeout=30.0)

  async def __aenter__(self):
    return self

  async def __aexit__(self, exc_type, exc, tb):
    await self.client.aclose()

  async def close(self):
    await self.client.aclose()

  async def get(self, endpoint: str, params: dict | None = None):
    url = f"{self.base_url}/{endpoint.lstrip('/')}"
    params = params.copy() if params else {}

    if self.api_key:
      params["apikey"] = self.api_key

    response = await self.client.get(url, params=params)
    response.raise_for_status()
    return response.json()
