import os
from abc import ABC, abstractmethod
from zendriver.core.browser import Browser
from zendriver.core.tab import Tab
from datetime import datetime
import asyncio
from urllib.parse import quote_plus
import logger


class Scraper(ABC):
    def __init__(self):
        self.search_terms = []
        logger.info(f"Initialized {self.__class__.__name__} scraper")

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
        logger.info(f"Saving screenshot for '{name}'...")
        screenshot_dir = await self.get_screenshot_dir()

        os.makedirs(screenshot_dir, exist_ok=True)

        file_name = f"{quote_plus(name)}-{datetime.now().isoformat()}.png"

        screenshot_path = os.path.join(screenshot_dir, file_name)

        await tab.save_screenshot(screenshot_path, format="png", full_page=False)
        logger.info(f"Screenshot saved to {screenshot_path}")

    async def handle_search_term(
        self, browser: Browser, search_term: str
    ) -> list[dict[str, any]]:
        logger.info(f"Processing search term: '{search_term}'")
        tab = None
        try:
            url = await self.get_url(search_term)
            logger.info(f"Opening URL: {url}")

            tab = await browser.get(url, new_tab=True)
            logger.info(f"Tab opened, waiting for page to load...")

            await tab.wait_for_ready_state(until="complete")
            logger.info(f"Page loaded completely")

            await asyncio.sleep(5)
            logger.info(f"Taking screenshot after 5 second delay")

            await self.save_screenshot(tab, search_term)

            logger.info(f"Extracting data from page...")
            data = await self.get_data(search_term, tab)
            logger.info(f"Found {len(data)} items for '{search_term}'")

            return data
        except Exception as e:
            logger.error(f"handle_search_term error: {e}")

            if tab:
                try:
                    logger.debug(f"Attempting to get page content for debugging...")
                    logger.debug(await tab.get_content())
                except Exception as e:
                    logger.error(f"error getting tab content: {e}")

            return []
        finally:
            if tab:
                try:
                    logger.info(f"Closing tab for '{search_term}'")
                    await tab.close()
                except Exception as e:
                    logger.error(f"error closing tab: {e}")

    async def start(self, browser: Browser) -> list[dict[str, any]]:
        logger.info(
            f"Starting {self.__class__.__name__} scraper with {len(self.search_terms)} search terms"
        )
        results: list[dict[str, any]] = []

        for i, search_term in enumerate(self.search_terms):
            logger.info(
                f"Processing search term {i+1}/{len(self.search_terms)}: '{search_term}'"
            )
            data = await self.handle_search_term(browser, search_term)
            logger.info(f"Data for '{search_term}'", {"data": data})

            results.extend(data)

            logger.info(f"Sleeping for 10 seconds before next search term...")
            await asyncio.sleep(10)

        logger.info(
            f"Completed {self.__class__.__name__} scraper with {len(results)} total results"
        )
        return results
