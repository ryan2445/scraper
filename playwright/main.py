from playwright.sync_api import sync_playwright
import os
import time
from typing import List, Dict, Any
from scraper import get_scraper


class WebScraper:
    def __init__(
        self,
        headless: bool = True,
        screenshot_dir: str = "screenshots",
    ):
        self.headless = headless
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def scrape(
        self, websites: List[str], search_terms: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        all_results = {}
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()

            try:
                for website in websites:
                    scraper = get_scraper(website, self.screenshot_dir)
                    website_results = []
                    for term in search_terms:
                        print(f"Scraping {website} for search term: {term}")
                        results = scraper.scrape(page, term)
                        website_results.extend(results)
                        print(f"Found {len(results)} results for '{term}' on {website}")
                    all_results[website] = website_results
            except Exception as e:
                screenshot_path = os.path.join(
                    self.screenshot_dir, f"error_{int(time.time())}.png"
                )
                page.screenshot(path=screenshot_path)
                print(f"General error during scraping: {e}")
                print(f"Screenshot saved to {screenshot_path}")
            finally:
                browser.close()

        return all_results


def main():
    websites = ["mercari"]
    search_terms = ["asus rog ally x"]

    scraper = WebScraper(headless=False)
    results = scraper.scrape(websites, search_terms)

    total_count = sum(len(site_results) for site_results in results.values())
    print(f"\nScraping Summary:")
    print(f"Total listings found: {total_count}")

    for website, site_results in results.items():
        print(f"\n{website.capitalize()} results: {len(site_results)}")
        for i, result in enumerate(site_results[:3]):
            print(
                f"  {i+1}. ID: {result.get('id', 'N/A')}, Price: {result.get('price', 'N/A')}, Status: {result.get('status', 'N/A')}"
            )

        if len(site_results) > 3:
            print(f"  ... and {len(site_results) - 3} more")


if __name__ == "__main__":
    main()
