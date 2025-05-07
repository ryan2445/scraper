import asyncio
from mercari import MercariScraper
import zendriver
from scraper import Scraper
import os

SCRAPERS: list[Scraper] = [MercariScraper()]


async def main():
    browser = None
    try:
        browser_args = []
        if os.getenv("HTTP_PROXY") and os.getenv("HTTPS_PROXY"):
            browser_args.append(
                f"--proxy-server=http={os.getenv('HTTP_PROXY')};https={os.getenv('HTTPS_PROXY')}"
            )

        browser = await zendriver.start(
            headless=False,
            browser_args=browser_args,
        )
        await asyncio.sleep(10)  # wait for browser to start/load

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
        print(e)  # known error
