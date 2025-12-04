from playwright.sync_api import sync_playwright     #automatically controls the browser 


def main():
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=False)
        # Note: Set headless=True for faster, background scraping
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(locale="en-GB")
        page.goto("https://www.synaps.network/en", timeout=20000)
        
main()
