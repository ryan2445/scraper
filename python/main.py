import asyncio
from mercari import MercariScraper
import zendriver
from scraper import Scraper
import os
import logger

SCRAPERS: list[Scraper] = [MercariScraper()]


async def main():
    logger.info("Starting scraper application...")
    browser = None
    try:
        browser_args = []
        if os.getenv("HTTP_PROXY") and os.getenv("HTTPS_PROXY"):
            logger.info(f"Using proxy configuration")
            browser_args.append(
                f"--proxy-server=http={os.getenv('HTTP_PROXY')};https={os.getenv('HTTPS_PROXY')}"
            )

        logger.info("Initializing browser...")
        browser = await zendriver.start(
            headless=False,
            browser_args=browser_args,
        )
        logger.info("Browser started successfully")
        await asyncio.sleep(10)  # wait for browser to start/load

        for i, scraper in enumerate(SCRAPERS):
            logger.info(
                f"Running scraper {i+1}/{len(SCRAPERS)}: {scraper.__class__.__name__}"
            )
            _ = await scraper.start(browser)
            logger.info(f"Finished scraper: {scraper.__class__.__name__}")
    except Exception as e:
        logger.error(f"main error: {e}")
    finally:
        if browser:
            try:
                logger.info("Stopping browser...")
                await browser.stop()
                logger.info("Browser stopped successfully")
            except Exception as e:
                logger.error(f"error stopping browser: {e}")

        logger.info("Scraper application completed")


if __name__ == "__main__":
    try:
        logger.info("Starting main application")
        asyncio.run(main())
    except RuntimeError as e:
        logger.error(str(e))  # known error
