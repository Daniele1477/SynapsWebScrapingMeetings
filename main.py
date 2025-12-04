from playwright.sync_api import sync_playwright     #automatically controls the browser 
'''
def main():
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=False)
        # Note: Set headless=True for faster, background scraping
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(locale="en-GB")
        page.goto("https://www.google.com/maps", timeout=20000)
        search_for = 'Syria'
        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        
main()
'''
from playwright.sync_api import sync_playwright

def run_hover_test():
    # 1. Start the Playwright environment
    with sync_playwright() as p:
        # 2. Launch a Chromium browser instance
        browser = p.chromium.launch(headless=False)
        
        # 3. Open a new page (tab)
        page = browser.new_page()
        
        # 4. Go to a site with a common menu structure
        print("Navigating to the Playwright documentation...")
        page.goto("https://playwright.dev/")
        
        # --- Hover Action ---
        
        # 5. Locate the main 'Docs' link in the top navigation bar
        # This link usually triggers a visual change or sub-menu on hover
        docs_link_locator = page.locator('//a[text()="Docs"]')
        
        print("Hovering over the 'Docs' link...")
        # 6. Perform the hover action
        docs_link_locator.hover()
        
        # 7. Now, wait for an element that should only appear after the hover action
        # We'll wait for the 'Intro' link, which is often in the sub-menu
        intro_link_locator = page.locator('//a[text()="Intro"]')
        
        print("Waiting for 'Intro' link (in sub-menu) to become visible...")
        # wait_for_selector waits until the element is displayed on the page
        intro_link_locator.wait_for(state='visible', timeout=10000)
        
        # 8. Wait 3 seconds so you can visually confirm the menu is visible
        print("Sub-menu is visible. Waiting 3 seconds for inspection...")
        page.wait_for_timeout(3000)
        
        # 9. Close the browser
        print("Closing browser...")
        browser.close()

# Run the function
if __name__ == "__main__":
    run_hover_test()