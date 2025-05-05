import os
import time
from typing import List, Dict, Any
from scraper import get_scraper
import undetected_chromedriver as uc
from stealth import stealth


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
        print("Creating Chrome driver")
        driver = uc.Chrome(headless=self.headless, use_subprocess=False)
        stealth(driver)

        print("Scraping websites")
        all_results = {}
        try:
            for website in websites:
                scraper = get_scraper(website, self.screenshot_dir)
                website_results = []
                for term in search_terms:
                    results = scraper.scrape(driver, term)
                    website_results.extend(results)
                all_results[website] = website_results
        except Exception as e:
            print(f"[ERROR] General error during scraping: {e}")
            screenshot_path = os.path.join(
                self.screenshot_dir, f"error_{int(time.time())}.png"
            )
            driver.save_screenshot(screenshot_path)
        finally:
            input("Press Enter to quit")
            driver.quit()

        return all_results


def main():
    websites = ["mercari"]
    search_terms = ["asus rog ally x"]
    scraper = WebScraper(headless=False)
    results = scraper.scrape(websites, search_terms)
    print(results)


if __name__ == "__main__":
    main()
