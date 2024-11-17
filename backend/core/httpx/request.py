from httpx import AsyncClient


async def send_request(url, *args, **kwargs):
    async with AsyncClient() as client:
        response = await client.get(url, *args, **kwargs)

        return response.json(), response.status_code
