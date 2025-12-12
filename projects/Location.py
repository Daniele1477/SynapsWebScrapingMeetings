from playwright.sync_api import sync_playwright
import pandas as pd 

def locations(file_path):
    df = pd.read_excel(file_path)
    with sync_playwright() as p:
        # Launch the Chromium browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://plus.codes/map")
        search_for = df['plus_code'].iloc[0]
        page.locator('//input[@id="search-input"]').fill(search_for)
        page.keyboard.press("Enter")
        page.click("div.expand.sprite-bg", timeout=5000)
        coordinates_selector = "div.detail.latlng.clipboard.vertical-center"
        coordinates_element = page.locator(coordinates_selector) # Finds the actual HTML element
        raw_coordinates = coordinates_element.inner_text()
        page.wait_for_timeout(6000)
        print(f"Coordinates found: {raw_coordinates}")
locations('GMaps Data/2025-12-12/supermarkets_in_Berlin.xlsx')


