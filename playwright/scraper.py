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
        print(f"[DEBUG] Taking screenshot '{filename}' in directory: {screenshot_dir}")
        screenshot_path = os.path.join(screenshot_dir, filename)
        page.screenshot(path=screenshot_path)
        print(f"[DEBUG] Screenshot saved to {screenshot_path}")


class MercariScraper(BaseScraper):
    def __init__(self, screenshot_dir: str = "screenshots"):
        print(
            f"[DEBUG] Initializing MercariScraper with screenshot_dir={screenshot_dir}"
        )
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)
        print(f"[DEBUG] Screenshot directory ensured: {self.screenshot_dir}")

    def scrape(self, page: Page, search_term: str) -> List[Dict[str, Any]]:
        try:
            print(f"[DEBUG] Starting Mercari scrape for term: '{search_term}'")
            print(f"[DEBUG] Navigating to https://mercari.com")
            page.goto("https://mercari.com")

            print(f"[DEBUG] Locating search input field")
            search_input = page.locator("#GlobalNavSearchInput")

            print(f"[DEBUG] Waiting for search input to be visible")
            search_input.wait_for(state="visible")
            print(f"[DEBUG] Clearing search input")
            search_input.fill("")
            print(f"[DEBUG] Filling search input with term: '{search_term}'")
            search_input.fill(search_term)
            print(f"[DEBUG] Pressing Enter to submit search")
            search_input.press("Enter")
            page.wait_for_load_state("networkidle")

            print(f"[DEBUG] Current URL after search: {page.url}")
            print(f"[DEBUG] Extracting listings from search results")
            return self._extract_listings(page, search_term)
        except Exception as e:
            print(f"[ERROR] Error during Mercari scraping: {e}")
            filename = f"mercari_error_{int(time.time())}.png"
            print(f"[DEBUG] Taking error screenshot: {filename}")
            self.take_screenshot(page, filename, self.screenshot_dir)
            return []

    def _extract_listings(self, page: Page, search_term: str) -> List[Dict[str, Any]]:
        try:
            print(f"[DEBUG] Looking for on_sale items on the page")
            listings = page.locator('div[data-itemstatus="on_sale"]')
            print(
                f"[DEBUG] Found {listings.count()} total listings with on_sale status"
            )

            print(f"[DEBUG] Limiting to first 64 listings")
            listings = listings[:64]

            results = []
            print(f"[DEBUG] Starting to extract data from {len(listings)} listings")
            for i, listing in enumerate(listings):
                try:
                    print(f"[DEBUG] Processing listing {i+1}/{len(listings)}")
                    item_id = listing.get_attribute("id")
                    print(f"[DEBUG] Found item ID: {item_id}")
                    item_price = listing.get_attribute("data-itemprice")
                    print(f"[DEBUG] Found item price: {item_price}")
                    item_status = listing.get_attribute("data-itemstatus")
                    print(f"[DEBUG] Found item status: {item_status}")

                    result = {
                        "id": item_id,
                        "price": item_price,
                        "status": item_status,
                        "search_term": search_term,
                        "source": page.url,
                    }
                    print(f"[DEBUG] Adding listing to results: {result}")
                    results.append(result)
                except Exception as e:
                    print(f"[ERROR] Error extracting data from listing {i+1}: {e}")
                    screenshot_name = f"listing_error_{int(time.time())}.png"
                    print(f"[DEBUG] Taking error screenshot: {screenshot_name}")
                    self.take_screenshot(
                        page,
                        screenshot_name,
                        self.screenshot_dir,
                    )

            print(f"[DEBUG] Extraction complete. Total results: {len(results)}")
            return results
        except Exception as e:
            print(f"[ERROR] Error finding listings: {e}")
            screenshot_name = f"listings_error_{int(time.time())}.png"
            print(f"[DEBUG] Taking error screenshot: {screenshot_name}")
            self.take_screenshot(page, screenshot_name, self.screenshot_dir)
            return []


def get_scraper(website: str, screenshot_dir: str = "screenshots") -> BaseScraper:
    print(
        f"[DEBUG] get_scraper called for website: {website}, screenshot_dir: {screenshot_dir}"
    )
    scrapers = {"mercari": MercariScraper(screenshot_dir)}
    print(f"[DEBUG] Available scrapers: {list(scrapers.keys())}")

    if website.lower() not in scrapers:
        print(f"[ERROR] Unsupported website requested: {website}")
        raise ValueError(f"Unsupported website: {website}")

    print(f"[DEBUG] Returning {website} scraper")
    return scrapers[website.lower()]
