import asyncio
from mercari import MercariScraper
import zendriver
from scraper import Scraper

SCRAPERS: list[Scraper] = [MercariScraper()]


async def main():
    browser = None
    try:
        browser = await zendriver.start(headless=False)

        for scraper in SCRAPERS:
            _ = await scraper.start(browser)
    except Exception as e:
        print(f"main error: {e}")
    finally:
        if browser:
            try:
                await browser.stop()
            except Exception as e:
                print(f"error stopping browser: {e}")

        print("done")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(e.args)
