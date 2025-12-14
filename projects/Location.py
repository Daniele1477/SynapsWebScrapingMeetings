'''from playwright.sync_api import sync_playwright
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
locations('GMaps Data/2025-12-12/supermarkets_in_Berlin.xlsx')'''

from playwright.sync_api import sync_playwright
import pandas as pd
import argparse
import os

def locations(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return

    df = pd.read_excel(file_path)
    if 'plus_code' not in df.columns:
        print("Error: No 'plus_code' column in the file")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://plus.codes/map")
#the logic to implement here is that after getting the first coordinate we loop through the rest of the plus codes by just typing them in the search box one by one
        for idx, search_for in enumerate(df['plus_code']):
            page.locator('//input[@id="search-input"]').fill(search_for)
            page.keyboard.press("Enter")
            page.click("div.expand.sprite-bg", timeout=5000)
            page.wait_for_timeout(2000)  # wait for coordinates to appear

            coordinates_selector = "div.detail.latlng.clipboard.vertical-center"
            coordinates_element = page.locator(coordinates_selector)
            raw_coordinates = coordinates_element.inner_text()
            lat_str, lon_str = map(str.strip, raw_coordinates.split(','))
            df.loc[idx, 'latitude'] = float(lat_str)
            df.loc[idx, 'longitude'] = float(lon_str)            
    df.to_excel(file_path, index=False)
    csv_file_path = os.path.splitext(file_path)[0] + ".csv"
    df.to_csv(csv_file_path, index=False)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get coordinates from an Excel file of plus codes.")
    parser.add_argument(
        "-f", "--file",
        required=True,
        help="Path to the Excel file containing the plus codes"
    )
    args = parser.parse_args()

    locations(args.file)



