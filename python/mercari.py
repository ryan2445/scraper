from scraper import Scraper
from zendriver.core.tab import Tab
from zendriver.core.element import Element
import os
from urllib.parse import quote
import logger


class MercariScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.search_terms = ["asus rog ally x", "steam deck oled"]
        logger.info(
            f"MercariScraper initialized with search terms: {self.search_terms}"
        )

    async def get_url(self, search_term: str) -> str:
        url = f"https://www.mercari.com/search/?keyword={quote(search_term)}"
        logger.info(f"Generated Mercari search URL: {url}")
        return url

    async def get_screenshot_dir(self) -> str:
        dir_path = os.path.join(os.path.dirname(__file__), "screenshots", "mercari")
        logger.info(f"Screenshot directory: {dir_path}")
        return dir_path

    async def get_data(self, search_term: str, tab: Tab) -> list[dict[str, any]]:
        logger.info(f"Extracting data for Mercari search: '{search_term}'")
        data = []

        logger.info("Waiting for items to appear on page...")
        await tab.wait_for(selector='div[data-itemstatus="on_sale"]')
        logger.info("Items found on page")

        logger.info("Selecting all 'on_sale' items...")
        items: list[Element] = await tab.query_selector_all(
            'div[data-itemstatus="on_sale"]'
        )
        logger.info(f"Found {len(items)} items for sale")

        for item in items:
            item_data = {}
            item_url = (await item.query_selector("a")).attrs.get("href")

            item_data["id"] = item.attrs.get("id")
            item_data["price"] = item.attrs.get("data-itemprice")
            item_data["url"] = item_url
            item_data["search_term"] = search_term
            item_data["search_url"] = tab.url

            data.append(item_data)

        logger.info(f"Extracted {len(data)} items from Mercari search")
        return data
