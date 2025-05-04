import os
import time
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from playwright.sync_api import Page


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, page: Page, search_term: str) -> List[Dict[str, Any]]:
        pass

    def take_screenshot(self, page: Page, filename: str, screenshot_dir: str) -> None:
        screenshot_path = os.path.join(screenshot_dir, filename)
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")


class MercariScraper(BaseScraper):
    def __init__(self, screenshot_dir: str = "screenshots"):
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def scrape(self, page: Page, search_term: str) -> List[Dict[str, Any]]:
        try:
            page.goto("https://mercari.com")

            search_input = page.locator("#GlobalNavSearchInput")

            search_input.wait_for(state="visible")

            search_input.fill("")
            search_input.fill(search_term)

            search_input.press("Enter")

            return self._extract_listings(page, search_term)
        except Exception as e:
            self.take_screenshot(
                page, f"mercari_error_{int(time.time())}.png", self.screenshot_dir
            )
            print(f"Error during Mercari scraping: {e}")
            return []

    def _extract_listings(self, page: Page, search_term: str) -> List[Dict[str, Any]]:
        try:
            listings = page.locator('div[data-itemstatus="on_sale"]').all()

            listings = listings[:64]

            results = []
            for listing in listings:
                try:
                    item_id = listing.get_attribute("id")
                    item_price = listing.get_attribute("data-itemprice")
                    item_status = listing.get_attribute("data-itemstatus")

                    results.append(
                        {
                            "id": item_id,
                            "price": item_price,
                            "status": item_status,
                            "search_term": search_term,
                            "source": page.url,
                        }
                    )
                except Exception as e:
                    print(f"Error extracting data from listing: {e}")
                    self.take_screenshot(
                        page,
                        f"listing_error_{int(time.time())}.png",
                        self.screenshot_dir,
                    )

            return results
        except Exception as e:
            print(f"Error finding listings: {e}")
            self.take_screenshot(
                page, f"listings_error_{int(time.time())}.png", self.screenshot_dir
            )
            return []


def get_scraper(website: str, screenshot_dir: str = "screenshots") -> BaseScraper:
    scrapers = {"mercari": MercariScraper(screenshot_dir)}

    if website.lower() not in scrapers:
        raise ValueError(f"Unsupported website: {website}")

    return scrapers[website.lower()]
