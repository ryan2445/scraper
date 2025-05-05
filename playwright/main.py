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
                browser = playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=self.headless,
                    executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    channel="chrome",
                    ignore_default_args=["--enable-automation"],
                    java_script_enabled=True,
                    bypass_csp=True,
                    chromium_sandbox=True,
                )
                page = browser.pages[0]

                input("Press Enter to continue...")

                all_results = {}
                try:
                    print("Scraping websites")
                    # for website in websites:
                    #     scraper = get_scraper(website, self.screenshot_dir)
                    #     website_results = []
                    #     for term in search_terms:
                    #         results = scraper.scrape(page, term)
                    #         website_results.extend(results)
                    #     all_results[website] = website_results
                except Exception as e:
                    print(f"[ERROR] General error during scraping: {e}")
                    screenshot_path = os.path.join(
                        self.screenshot_dir, f"error_{int(time.time())}.png"
                    )
                    page.screenshot(path=screenshot_path)
                finally:
                    browser.close()
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
