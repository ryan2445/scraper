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
        print(
            f"[DEBUG] Initializing WebScraper - headless={headless}, screenshot_dir={screenshot_dir}"
        )
        self.headless = headless
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)
        print(f"[DEBUG] Screenshot directory ensured: {self.screenshot_dir}")

    def scrape(
        self, websites: List[str], search_terms: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        print(f"[DEBUG] Starting scrape operation for websites: {websites}")
        print(f"[DEBUG] Search terms to use: {search_terms}")
        all_results = {}
        with sync_playwright() as p:
            print(f"[DEBUG] Launching browser with headless={self.headless}")
            browser = p.chromium.launch(headless=self.headless)
            print(f"[DEBUG] Creating browser context with viewport 1280x800")
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
            )
            print(f"[DEBUG] Opening new page")
            page = context.new_page()

            try:
                for website in websites:
                    print(f"[DEBUG] Getting scraper for website: {website}")
                    scraper = get_scraper(website, self.screenshot_dir)
                    website_results = []
                    for term in search_terms:
                        print(
                            f"[DEBUG] Starting scrape for {website} with term: '{term}'"
                        )
                        results = scraper.scrape(page, term)
                        website_results.extend(results)
                        print(
                            f"[DEBUG] Completed scrape for '{term}' on {website}: {len(results)} results"
                        )
                    all_results[website] = website_results
                    print(
                        f"[DEBUG] All terms scraped for {website}, total results: {len(website_results)}"
                    )
            except Exception as e:
                screenshot_path = os.path.join(
                    self.screenshot_dir, f"error_{int(time.time())}.png"
                )
                print(f"[DEBUG] Taking error screenshot at: {screenshot_path}")
                page.screenshot(path=screenshot_path)
                print(f"[ERROR] General error during scraping: {e}")
                print(f"[DEBUG] Screenshot saved to {screenshot_path}")
            finally:
                print(f"[DEBUG] Closing browser")
                # browser.close()
                # wait for ctrl+c
                input("Press Ctrl+C to exit")

        print(
            f"[DEBUG] Scraping completed, returning results for {len(all_results)} websites"
        )
        return all_results


def main():
    print(f"[DEBUG] Starting main function")
    websites = ["mercari"]
    search_terms = ["asus rog ally x"]
    print(f"[DEBUG] Config - websites: {websites}, search terms: {search_terms}")

    print(f"[DEBUG] Creating WebScraper instance with headless=False")
    scraper = WebScraper(headless=False)
    print(f"[DEBUG] Calling scrape method")
    results = scraper.scrape(websites, search_terms)

    total_count = sum(len(site_results) for site_results in results.values())
    print(f"[DEBUG] Processing results - total count across all sites: {total_count}")
    print(f"\nScraping Summary:")
    print(f"Total listings found: {total_count}")

    for website, site_results in results.items():
        print(f"\n{website.capitalize()} results: {len(site_results)}")
        print(f"[DEBUG] Displaying up to 3 sample results for {website}")
        for i, result in enumerate(site_results[:3]):
            print(
                f"  {i+1}. ID: {result.get('id', 'N/A')}, Price: {result.get('price', 'N/A')}, Status: {result.get('status', 'N/A')}"
            )
            print(f"[DEBUG] Result details: {result}")

        if len(site_results) > 3:
            print(f"  ... and {len(site_results) - 3} more")

    print(f"[DEBUG] Main function completed")


if __name__ == "__main__":
    print(f"[DEBUG] Script started as main")
    main()
