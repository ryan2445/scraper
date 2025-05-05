import os
import shutil
import time
import json
from typing import List, Dict, Any
from scraper import get_scraper
from playwright.sync_api import sync_playwright
import tempfile


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
        try:
            print("Initializing Playwright")
            with sync_playwright() as playwright:
                print("Launching browser")
                user_data_dir = tempfile.mkdtemp(prefix="uc_")
                browser_chrome = playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=self.headless,
                    executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    channel="chrome",
                    args=["--remote-debugging-port=9222"],
                )
                browser_cdp = playwright.chromium.connect_over_cdp(
                    endpoint_url="http://localhost:9222"
                )
                context = browser_cdp.new_context()
                page = context.new_page()

                print("Scraping websites")
                all_results = {}
                try:
                    for website in websites:
                        scraper = get_scraper(website, self.screenshot_dir)
                        website_results = []
                        for term in search_terms:
                            results = scraper.scrape(page, term)
                            website_results.extend(results)
                        all_results[website] = website_results
                except Exception as e:
                    print(f"[ERROR] General error during scraping: {e}")
                    screenshot_path = os.path.join(
                        self.screenshot_dir, f"error_{int(time.time())}.png"
                    )
                    page.screenshot(path=screenshot_path)
                finally:
                    with open("storage_state.json", "w") as storage_state:
                        storage_state.write(json.dumps(context.storage_state()))
                    input("Press Enter to continue...")
                    browser_cdp.close()
                    browser_chrome.close()
                    shutil.rmtree(user_data_dir)

                return all_results
        except Exception as e:
            print(f"General error during scraping: {e}")
            return {}


def main():
    websites = ["mercari"]
    search_terms = ["asus rog ally x"]
    scraper = WebScraper(headless=False)
    results = scraper.scrape(websites, search_terms)
    print(results)


if __name__ == "__main__":
    main()
