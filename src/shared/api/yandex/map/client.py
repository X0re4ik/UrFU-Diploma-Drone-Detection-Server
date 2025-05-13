from dataclasses import dataclass
from typing import List
import aiohttp
import asyncio

@dataclass
class YandexMapDistance:
    text: str
    value: float

@dataclass
class YandexMapResult:
    title: str
    subtitle: str
    distance: YandexMapDistance

class YandexMapClient:
    def __init__(self, *, api_key: str, base_url: str = "https://suggest-maps.yandex.ru/v1/suggest"):
        self._api_key = api_key
        self._base_url = base_url
        self._params = {
            "apikey": self._api_key,
        }

    def set_ll(self, lon: float, lat: float):
        self._params["ll"] = f"{lon},{lat}"
        return self

    def set_results(self, count: int):
        self._params["results"] = str(count)
        return self

    def set_attrs(self):
        self._params["attrs"] = "uri"
        return self

    async def send(self, text: str) -> List[YandexMapResult]:
        params = self._params.copy()
        params["text"] = text

        async with aiohttp.ClientSession() as session:
            async with session.get(self._base_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Request failed with status {response.status}")

                json_data = await response.json()
                results = json_data.get("results", [])

                return [
                    YandexMapResult(
                        title=item["title"]["text"],
                        subtitle=item["subtitle"]["text"],
                        distance=YandexMapDistance(
                            value=item["distance"]["value"],
                            text=item["distance"]["text"]
                        )
                    )
                    for item in results if "distance" in item
                ]

# Пример использованияw
async def main():
    client = YandexMapClient(api_key="de0a0eed-8f3e-4a79-89e5-9e47b7d2b164")
    results = await client.set_ll(60.591628, 56.805428).set_attrs().send("Производственное предприятие")

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
