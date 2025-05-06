import os
from abc import ABC, abstractmethod
from zendriver.core.browser import Browser
from zendriver.core.tab import Tab
from datetime import datetime
import asyncio
from urllib.parse import quote_plus


class Scraper(ABC):
    def __init__(self):
        self.search_terms = []

    @abstractmethod
    async def get_url(self, search_term: str) -> str:
        pass

    @abstractmethod
    async def get_screenshot_dir(self) -> str:
        pass

    @abstractmethod
    async def get_data(self, search_term: str, tab: Tab) -> list[dict[str, any]]:
        pass

    async def save_screenshot(self, tab: Tab, name: str) -> None:
        screenshot_dir = await self.get_screenshot_dir()

        os.makedirs(screenshot_dir, exist_ok=True)

        file_name = f"{quote_plus(name)}-{datetime.timestamp(datetime.now())}.png"

        screenshot_path = os.path.join(screenshot_dir, file_name)

        await tab.save_screenshot(screenshot_path, format="png", full_page=False)

    async def handle_search_term(
        self, browser: Browser, search_term: str
    ) -> list[dict[str, any]]:
        tab = None
        try:
            url = await self.get_url(search_term)

            tab = await browser.get(url, new_tab=True)

            await tab.wait_for_ready_state(until="complete")

            await asyncio.sleep(5)

            await self.save_screenshot(tab, search_term)

            data = await self.get_data(search_term, tab)

            return data
        except Exception as e:
            print(f"handle_search_term error: {e}")

            return []
        finally:
            if tab:
                try:
                    await tab.close()
                except Exception as e:
                    print(f"error closing tab: {e}")

    async def start(self, browser: Browser) -> list[dict[str, any]]:
        results: list[dict[str, any]] = []

        for search_term in self.search_terms:
            data = await self.handle_search_term(browser, search_term)
            print(data)
            print("\n\n")

            results.extend(data)

            await asyncio.sleep(10)

        return results
