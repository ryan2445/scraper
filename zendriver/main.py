import asyncio
import zendriver as zd


async def main():
    browser = await zd.start()
    search_term = "asus rog ally x"
    page = await browser.get(f"https://www.mercari.com/search/?keyword={search_term}")
    await page.wait_for_ready_state(until="complete")
    await page.save_screenshot("screenshots/mercari.png")
    input("Press Enter to continue...")
    await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
