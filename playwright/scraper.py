import os
import time
import random
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

    def human_delay(self, min_seconds=1, max_seconds=3):
        print("human_delay")
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def human_scroll(
        self,
        page: Page,
        min_pixels=100,
        max_pixels=400,
        scrolls=random.randint(1, 5),
    ):
        print("human_scroll")
        for _ in range(scrolls):
            pixels = random.randint(min_pixels, max_pixels)
            page.mouse.wheel(0, pixels)
            self.human_delay(0.5, 2)


class MercariScraper(BaseScraper):
    def __init__(self, screenshot_dir: str = "screenshots"):
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def scrape(self, page: Page, search_term: str) -> List[Dict[str, Any]]:
        print("scrape")
        try:
            page.goto(
                f"https://mercari.com/search/?keyword={search_term}",
                wait_until="networkidle",
            )
            self.human_scroll(page)
            return self._extract_listings(page, search_term)
        except Exception as e:
            print(f"Error during Mercari scraping: {e}")
            filename = f"mercari_scrape_error_{int(time.time())}.png"
            self.take_screenshot(page, filename, self.screenshot_dir)
            return []

    def _extract_listings(self, page: Page, search_term: str) -> List[Dict[str, Any]]:
        print("extract_listings")
        try:
            page.wait_for_selector('div[data-itemstatus="on_sale"]')
            listings = page.query_selector_all('div[data-itemstatus="on_sale"]')
            results = []

            for i, listing in enumerate(listings[:30]):
                try:
                    item_id = listing.get_attribute("id")
                    item_price = listing.get_attribute("data-itemprice")
                    item_status = listing.get_attribute("data-itemstatus")
                    result = {
                        "id": item_id,
                        "price": item_price,
                        "status": item_status,
                        "search_term": search_term,
                        "source": page.url,
                    }
                    results.append(result)
                except Exception as e:
                    print(f"Error extracting data from listing {i+1}: {e}")
                    screenshot_name = f"mercari_listing_error_{int(time.time())}.png"
                    self.take_screenshot(
                        page,
                        screenshot_name,
                        self.screenshot_dir,
                    )
            return results
        except Exception as e:
            print(f"Error finding listings: {e}")
            screenshot_name = f"mercari_listings_error_{int(time.time())}.png"
            self.take_screenshot(page, screenshot_name, self.screenshot_dir)
            return []


def get_scraper(website: str, screenshot_dir: str = "screenshots") -> BaseScraper:
    print("get_scraper")
    scrapers = {"mercari": MercariScraper(screenshot_dir)}
    if website.lower() not in scrapers:
        raise ValueError(f"Unsupported website: {website}")
    return scrapers[website.lower()]
