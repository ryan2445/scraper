from scraper import Scraper
from zendriver.core.tab import Tab
from zendriver.core.element import Element
import os
from urllib.parse import quote


class MercariScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.search_terms = ["asus rog ally x", "steam deck oled"]

    async def get_url(self, search_term: str) -> str:
        return f"https://www.mercari.com/search/?keyword={quote(search_term)}"

    async def get_screenshot_dir(self) -> str:
        return os.path.join(os.path.dirname(__file__), "screenshots", "mercari")

    async def get_data(self, search_term: str, tab: Tab) -> list[dict[str, any]]:
        data = []

        await tab.wait_for(selector='div[data-itemstatus="on_sale"]')

        items: list[Element] = await tab.query_selector_all(
            'div[data-itemstatus="on_sale"]'
        )

        for item in items:
            item_data = {}
            item_url = (await item.query_selector("a")).attrs.get("href")

            item_data["id"] = item.attrs.get("id")
            item_data["price"] = item.attrs.get("data-itemprice")
            item_data["url"] = item_url
            item_data["search_term"] = search_term
            item_data["search_url"] = tab.url

            data.append(item_data)

        return data
