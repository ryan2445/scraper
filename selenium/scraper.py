import os
import time
import random
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement


class BaseScraper(ABC):
    @abstractmethod
    def scrape(
        self, driver: webdriver.Chrome, search_term: str
    ) -> List[Dict[str, Any]]:
        pass

    def take_screenshot(
        self, driver: webdriver.Chrome, filename: str, screenshot_dir: str
    ) -> None:
        screenshot_path = os.path.join(screenshot_dir, filename)
        driver.save_screenshot(screenshot_path)

    def human_delay(self, min_seconds=1, max_seconds=3):
        print("human_delay")
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def human_type(
        self, element: WebElement, text: str, min_delay=0.05, max_delay=0.15
    ):
        print("human_type")
        element.click()
        for char in text:
            ActionChains(element.parent).send_keys(char).perform()
            time.sleep(random.uniform(min_delay, max_delay))

    def human_scroll(
        self,
        driver: webdriver.Chrome,
        min_pixels=100,
        max_pixels=400,
        scrolls=random.randint(1, 5),
    ):
        print("human_scroll")
        for _ in range(scrolls):
            pixels = random.randint(min_pixels, max_pixels)
            ActionChains(driver).scroll_by_amount(0, pixels).perform()
            self.human_delay(0.5, 2)


class MercariScraper(BaseScraper):
    def __init__(self, screenshot_dir: str = "screenshots"):
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def scrape(
        self, driver: webdriver.Chrome, search_term: str
    ) -> List[Dict[str, Any]]:
        print("scrape")
        try:
            driver.get("https://www.mercari.com/search/?keyword=asus%20rog%20ally%20x")
            WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, "body")
                )
            )

            wait = WebDriverWait(driver, 10)
            search_input = wait.until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, "#GlobalNavSearchInput")
                )
            )
            self.human_scroll(driver)
            ActionChains(driver).move_to_element(search_input).perform()
            self.human_delay(1, 2)
            search_input.click()
            self.human_type(search_input, search_term)
            self.human_delay(1, 2)
            ActionChains(driver).send_keys(Keys.ENTER).perform()
            WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, "body")
                )
            )
            return self._extract_listings(driver, search_term)
        except Exception as e:
            print(f"Error during Mercari scraping: {e}")
            filename = f"mercari_scrape_error_{int(time.time())}.png"
            self.take_screenshot(driver, filename, self.screenshot_dir)
            return []

    def _extract_listings(
        self, driver: webdriver.Chrome, search_term: str
    ) -> List[Dict[str, Any]]:
        print("extract_listings")
        try:
            WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div[data-itemstatus="on_sale"]')
                )
            )
            listings = driver.find_elements(
                By.CSS_SELECTOR, 'div[data-itemstatus="on_sale"]'
            )
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
                        "source": driver.current_url,
                    }
                    results.append(result)
                except Exception as e:
                    print(f"Error extracting data from listing {i+1}: {e}")
                    screenshot_name = f"mercari_listing_error_{int(time.time())}.png"
                    self.take_screenshot(
                        driver,
                        screenshot_name,
                        self.screenshot_dir,
                    )
            return results
        except Exception as e:
            print(f"Error finding listings: {e}")
            screenshot_name = f"mercari_listings_error_{int(time.time())}.png"
            self.take_screenshot(driver, screenshot_name, self.screenshot_dir)
            return []


def get_scraper(website: str, screenshot_dir: str = "screenshots") -> BaseScraper:
    print("get_scraper")
    scrapers = {"mercari": MercariScraper(screenshot_dir)}
    if website.lower() not in scrapers:
        raise ValueError(f"Unsupported website: {website}")
    return scrapers[website.lower()]
