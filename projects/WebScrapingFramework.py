'''Web Scraping Framework

'''

'''

import datetime          #for date stamped folders  
from playwright.sync_api import sync_playwright     #automatically controls the browser 
from dataclasses import dataclass, asdict, field  #defines the objects 
import pandas as pd       
import argparse    #Command-line input refers to the additional pieces of information, called arguments, that you include after the script name to customize how the script runs. e.g.  python file_processor.py --input data.txt --output results.csv
import os  #operating system dependent functionality, create folders, check if files exist, checks working directory
import sys   #so sys is a library used to interact with the python program (the argument, the execution state, etc.)


# --- Helper Function to Load Existing Data ---
def load_existing_data(base_name: str, save_path: str) -> list['Business']:
    """Loads existing data from a CSV file into a list of Business objects."""
    filename = f"{base_name}.csv"            # ciao = 'hello'        print(f'{ciao}')
    file_path = os.path.join(save_path, filename) #hola = 'hola'       os.path.join(ciao,hola)

    if os.path.exists(file_path):
        try: #you don't know all the possible errors that might occur, so basically you are backing yourself up over a 'e' which is a set of error, rather than being explicit with the if logic
            # Note: We read the CSV because it is generally less complex than Excel
            df = pd.read_csv(file_path)
            
            # Drop unnecessary index columns that may appear during saving
            df = df.drop(columns=[c for c in df.columns if 'Unnamed:' in c], errors='ignore')

            # Convert each row back to a Business object, handling NaNs
            existing_businesses = []
            for _, row in df.iterrows():
                # Filter out NaN values before creating Business object
                # This ensures Business() is initialized with valid types/None
                valid_data = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
                existing_businesses.append(Business(**valid_data)) #so I am adding an instance of the Business object, which can be appended to a list
                
            print(f"Loaded {len(existing_businesses)} existing records for updating.")
            return existing_businesses
        except Exception as e:
            print(f"Warning: Could not load existing data from {file_path}. Starting fresh. Error: {e}")
            return []
    return [] #so basically instead of loading existing data is providing a list so that the program can run either way

# --- Data Classes ---

@dataclass
class Business:
    """holds business data"""     #beware that the type hints are just hints, they don't have much to do with execution
    name: str = None
    address: str = None
    domain: str = None
    website: str = None
    phone_number: str = None
    category: str = None
    location: str = None
    reviews_count: int = None
    reviews_average: float = None
    latitude: float = None
    longitude: float = None
    
    def __hash__(self):
        """Make Business hashable for duplicate detection."""
        hash_fields = [self.name]
        if self.domain:
            hash_fields.append(f"domain:{self.domain}")
        if self.website:
            hash_fields.append(f"website:{self.website}")
        if self.phone_number:
            hash_fields.append(f"phone:{self.phone_number}")
        return hash(tuple(hash_fields))

@dataclass
class BusinessList:
    """holds list of Business objects,
    and save to both excel and csv. Now supports pre-loading.
    """
    business_list: list[Business] = field(default_factory=list)
    _seen_businesses: set = field(default_factory=set, init=False)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    save_at = os.path.join('GMaps Data', today)
    os.makedirs(save_at, exist_ok=True)
###
    # NEW: Populate the seen set with any pre-loaded business_list
    def __post_init__(self):
        for business in self.business_list:
            self._seen_businesses.add(hash(business))

    def add_business(self, business: Business):
        """Add a business to the list if it's not a duplicate based on key attributes"""
        business_hash = hash(business)
        if business_hash not in self._seen_businesses:
            self.business_list.append(business)
            self._seen_businesses.add(business_hash)
            return True # Indicate that a new business was added
        return False # Indicate that a duplicate was found
    
    def dataframe(self):
        """transform business_list to pandas dataframe"""
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )


def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    """helper function to extract coordinates from url"""
    coordinates = url.split('/@')[-1].split('/')[0]
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])
#so here is basically splitting the url to get coordinates extract_coordinates_from_url('https://maps.example.com/place/Some+Location/@40.7128,-74.0060,15z/data=!3m1!4b1')
#(40.7128, -74.006)
#I must say though that coordinates in the url for some reason always differ from the real one, it's probably the view the browser would have portrayed if you gave him those coordinates 




# NOTE: The custom get_unique_filename function is removed
# to ensure the file path is predictable for loading/overwriting.

# --- Main Function ---
#this has nothing to do with classes, it's just a variable you are passing and applying methods on 
def main():
    parser = argparse.ArgumentParser() #this create a variable with the argparse method ArgumentParser() this way you can store values in it 
    parser.add_argument("-s", "--search", type=str) #adding options to parse values 
    parser.add_argument("-t", "--total", type=int)
    args = parser.parse_args()        #it's taking the search information from the parser (total, search) (parse the command-line arguments and store them in the 'args' variable)
    
    if args.search:
        search_list = [args.search]
        
    if args.total:
        total = args.total
    else:
        total = 1_000_000

    if not args.search:
        search_list = []
        input_file_name = 'input.txt'
        input_file_path = os.path.join(os.getcwd(), input_file_name)
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r') as file:
                search_list = file.readlines()
        if len(search_list) == 0:
            print('Error occurred: You must either pass the -s search argument, or add searches to input.txt')
            sys.exit() #this will stop the program right there with no further lines of code running 
#with is a context manager that ensures resources (like files) are properly cleaned up after you’re done, which prevents errors or memory leaks
    
    with sync_playwright() as p:
        #If headless=True, the browser runs in the background (faster for scraping)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(locale="en-GB")
        page.goto("https://www.google.com/maps", timeout=20000)
        
        for search_for_index, search_for in enumerate(search_list):    #this gets you access to the index of each element in a list for i, value in enumerate(my_list):
            search_for = search_for.strip() # Clean search term
            print(f"-----\n{search_for_index} - {search_for}")    #the n here is used to go to the next line 

            # Prepare the base filename from the search term
            base_filename = search_for.replace(' ', '_')         # 'trois et quatre' becomes trois_et_quatre

            # --- NEW: Load existing data and initialize BusinessList ---
            existing_records = load_existing_data(base_filename, BusinessList.save_at) #that save_at is the jointure of 'GMapsData, today', it is an attribute of the BusinessList
            initial_count = len(existing_records)
            business_list = BusinessList(business_list=existing_records)

            # Perform the search
            page.locator('//input[@id="searchboxinput"]').fill(search_for)
            page.wait_for_timeout(3000)
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)
            # scrolling
            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]') #move the mouse cursor over a web element to trigger its hover state (like revealing a dropdown menu or changing its color) without clicking it.

            previously_counted = 0
            while True:
                page.mouse.wheel(0, 10000) #literally scrolling the mouse wheel
                page.wait_for_timeout(3000)

                listings_count = page.locator(
                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                ).count()
                
                if listings_count >= total:
                    listings = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()[:total] #Playwright method takes the locator and immediately collects a list of all matching elements currently visible in the Document Object Model (DOM)
                    listings = [listing.locator("xpath=..") for listing in listings]
                    print(f"Total Scraped: {len(listings)}")
                    break
                else:
                    if listings_count == previously_counted:
                        listings = page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).all()
                        print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                        break
                    else:
                        previously_counted = listings_count
                        print(f"Currently Scraped: {listings_count}", end='\r')

            # NEW: Check if listings is defined and non-empty
            if 'listings' not in locals() or not listings:
                print(f"No listings found for {search_for}. Moving to next search.")
                continue #it basically skips a step of the loop when a condition is equal to the if clause and moves to the next one

            # scraping
            newly_added_count = 0
            for listing in listings:
                try:                        
                    listing.click()
                    page.wait_for_timeout(2000)

                    name_attribute = 'h1.DUwDvf'
                    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                    phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                    review_count_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//span'
                    reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'
                    business = Business()
                   
                    if name_value := page.locator(name_attribute).inner_text():       #this is the walrus operator, which at the same time sets the variable and returns the condition check to the if loop so that it can verify it and continue 
                        business.name = name_value.strip()
                    else:
                        business.name = None

                    if page.locator(address_xpath).count() > 0:
                        business.address = page.locator(address_xpath).all()[0].inner_text()
                    else:
                        business.address = None

                    if page.locator(website_xpath).count() > 0:
                        business.domain = page.locator(website_xpath).all()[0].inner_text()
                        business.website = f"https://www.{business.domain}"
                    else:
                        business.domain = None
                        business.website = None

                    if page.locator(phone_number_xpath).count() > 0:
                        # Clean up the phone number text to ensure hashing works correctly
                        business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text().strip()
                    else:
                        business.phone_number = None
                        
                    if page.locator(review_count_xpath).count() > 0:
                        # Attempt to parse integer, use None on failure
                        try:
                            text = page.locator(review_count_xpath).inner_text().split()[0].replace(',', '').strip()
                            business.reviews_count = int(text)
                        except:
                            business.reviews_count = None
                    else:
                        business.reviews_count = None
                        
                    if page.locator(reviews_average_xpath).count() > 0:
                        # Attempt to parse float, use None on failure
                        try:
                            text = page.locator(reviews_average_xpath).get_attribute('aria-label').split()[0].replace(',', '.').strip()
                            business.reviews_average = float(text)
                        except:
                            business.reviews_average = None
                    else:
                        business.reviews_average = None
                
                    #business.category = search_for.split(' in ')[0].strip() if ' in ' in search_for else search_for
                    #category_xpath = '//button[contains(@aria-label, "Category") or contains(@jsaction, "pane.rating.category") or contains(@data-item-id, "category")]//div'
                    category_xpath = '//button[contains(@jsaction, "pane.place.category")]//div[contains(@class, "fontBodyMedium")]'
                    
                    if page.locator(category_xpath).count() > 0:
                        # Use the text from the located element
                        business.category = page.locator(category_xpath).all()[0].inner_text().strip()
                    else:
                        # Fallback: Scrape the text from the top element after the name,
                        # which is often the category if the structured element isn't found.
                        fallback_category_xpath = '//div[@class="fontBodyMedium"]/span'
                        if page.locator(fallback_category_xpath).count() > 0:
                             business.category = page.locator(fallback_category_xpath).all()[0].inner_text().strip()
                        else:
                             # Use None if no official category could be found
                             business.category = None
                    business.location = search_for.split(' in ')[-1].strip() if ' in ' in search_for else None
                    business.latitude, business.longitude = extract_coordinates_from_url(page.url)

                    # NEW: Add business and track if it was new
                    if business_list.add_business(business):
                        newly_added_count += 1
                        
                except Exception as e:
                    print(f'Error occurred during scraping: {e}', end='\r')
            
            # --- Output (Modified to overwrite existing file with the complete list) ---
            final_excel_path = os.path.join(BusinessList.save_at, f"{base_filename}.xlsx")
            final_csv_path = os.path.join(BusinessList.save_at, f"{base_filename}.csv")

            # This will save the full list (old unique + new unique)
            business_list.dataframe().to_excel(final_excel_path, index=False)
            business_list.dataframe().to_csv(final_csv_path, index=False)

            print(f"\n--- Update Summary for '{search_for}' ---")
            print(f"Records previously saved: {initial_count}")
            print(f"New unique records added: {newly_added_count}")
            print(f"Total records in file: {len(business_list.business_list)}")
            print(f"File updated: {final_csv_path}")


        browser.close()



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f'Failed err: {e}')
        
'''



import datetime          #for date stamped folders  
from playwright.sync_api import sync_playwright     #automatically controls the browser 
from dataclasses import dataclass, asdict, field  #defines the objects 
import pandas as pd       
import argparse    #Command-line input refers to the additional pieces of information, called arguments, that you include after the script name to customize how the script runs. e.g.  python file_processor.py --input data.txt --output results.csv
import os  #operating system dependent functionality, create folders, check if files exist, checks working directory
import sys   #so sys is a library used to interact with the python program (the argument, the execution state, etc.)


# --- Helper Function to Load Existing Data ---
def load_existing_data(base_name: str, save_path: str) -> list['Business']:
    """Loads existing data from a CSV file into a list of Business objects."""
    filename = f"{base_name}.csv"            # ciao = 'hello'        print(f'{ciao}')
    file_path = os.path.join(save_path, filename) #hola = 'hola'       os.path.join(ciao,hola)

    if os.path.exists(file_path):
        try: #you don't know all the possible errors that might occur, so basically you are backing yourself up over a 'e' which is a set of error, rather than being explicit with the if logic
            # Note: We read the CSV because it is generally less complex than Excel
            df = pd.read_csv(file_path)
            
            # Drop unnecessary index columns that may appear during saving
            df = df.drop(columns=[c for c in df.columns if 'Unnamed:' in c], errors='ignore')

            # Convert each row back to a Business object, handling NaNs
            existing_businesses = []
            for _, row in df.iterrows():
                # Filter out NaN values before creating Business object
                # This ensures Business() is initialized with valid types/None
                valid_data = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
                existing_businesses.append(Business(**valid_data)) #so I am adding an instance of the Business object, which can be appended to a list
                
            print(f"Loaded {len(existing_businesses)} existing records for updating.")
            return existing_businesses
        except Exception as e:
            print(f"Warning: Could not load existing data from {file_path}. Starting fresh. Error: {e}")
            return []
    return [] #so basically instead of loading existing data is providing a list so that the program can run either way

# --- Data Classes ---

@dataclass
class Business:
    """holds business data"""     #beware that the type hints are just hints, they don't have much to do with execution
    name: str = None
    address: str = None
    domain: str = None
    website: str = None
    phone_number: str = None
    category: str = None
    location: str = None
    reviews_count: int = None
    reviews_average: float = None
    latitude: float = None
    longitude: float = None
    plus_code: str = None 
    def __hash__(self):
        """Make Business hashable for duplicate detection."""
        hash_fields = [self.name]
        if self.domain:
            hash_fields.append(f"domain:{self.domain}")
        if self.website:
            hash_fields.append(f"website:{self.website}")
        if self.phone_number:
            hash_fields.append(f"phone:{self.phone_number}")
        if self.plus_code:
            hash_fields.append(f"plus_code:{self.plus_code}")    
        return hash(tuple(hash_fields))
@dataclass
class BusinessList:
    """holds list of Business objects,
    and save to both excel and csv. Now supports pre-loading.
    """
    business_list: list[Business] = field(default_factory=list)
    _seen_businesses: set = field(default_factory=set, init=False)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    save_at = os.path.join('GMaps Data', today)
    os.makedirs(save_at, exist_ok=True)
###
    # NEW: Populate the seen set with any pre-loaded business_list
    def __post_init__(self):
        for business in self.business_list:
            self._seen_businesses.add(hash(business))

    def add_business(self, business: Business):
        """Add a business to the list if it's not a duplicate based on key attributes"""
        business_hash = hash(business)
        if business_hash not in self._seen_businesses:
            self.business_list.append(business)
            self._seen_businesses.add(business_hash)
            return True # Indicate that a new business was added
        return False # Indicate that a duplicate was found
    
    def dataframe(self):
        """transform business_list to pandas dataframe"""
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )

#this part is quite useless now that we have a program to compute the exact location
'''
def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    """helper function to extract coordinates from url"""
    coordinates = url.split('/@')[-1].split('/')[0]
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])'''
#so here is basically splitting the url to get coordinates extract_coordinates_from_url('https://maps.example.com/place/Some+Location/@40.7128,-74.0060,15z/data=!3m1!4b1')
#(40.7128, -74.006)
#I must say though that coordinates in the url for some reason always differ from the real one, it's probably the view the browser would have portrayed if you gave him those coordinates 




# NOTE: The custom get_unique_filename function is removed
# to ensure the file path is predictable for loading/overwriting.

# --- Main Function ---
#this has nothing to do with classes, it's just a variable you are passing and applying methods on 
def main():
    parser = argparse.ArgumentParser() #this create a variable with the argparse method ArgumentParser() this way you can store values in it 
    parser.add_argument("-s", "--search", type=str) #adding options to parse values 
    parser.add_argument("-t", "--total", type=int)
    args = parser.parse_args()        #it's taking the search information from the parser (total, search) (parse the command-line arguments and store them in the 'args' variable)
    
    if args.search:
        search_list = [args.search]
        
    if args.total:
        total = args.total
    else:
        total = 1_000_000

    if not args.search:
        search_list = []
        input_file_name = 'input.txt'
        input_file_path = os.path.join(os.getcwd(), input_file_name)
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r') as file:
                search_list = file.readlines()
        if len(search_list) == 0:
            print('Error occurred: You must either pass the -s search argument, or add searches to input.txt')
            sys.exit() #this will stop the program right there with no further lines of code running 
#with is a context manager that ensures resources (like files) are properly cleaned up after you’re done, which prevents errors or memory leaks
    
    with sync_playwright() as p:
        #If headless=True, the browser runs in the background (faster for scraping)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(locale="en-GB")
        page.goto("https://www.google.com/maps", timeout=20000)
        
        for search_for_index, search_for in enumerate(search_list):    #this gets you access to the index of each element in a list for i, value in enumerate(my_list):
            search_for = search_for.strip() # Clean search term
            print(f"-----\n{search_for_index} - {search_for}")    #the n here is used to go to the next line 

            # Prepare the base filename from the search term
            base_filename = search_for.replace(' ', '_')         # 'trois et quatre' becomes trois_et_quatre

            # --- NEW: Load existing data and initialize BusinessList ---
            existing_records = load_existing_data(base_filename, BusinessList.save_at) #that save_at is the jointure of 'GMapsData, today', it is an attribute of the BusinessList
            initial_count = len(existing_records)
            business_list = BusinessList(business_list=existing_records)

            # Perform the search
            page.locator('//input[@id="searchboxinput"]').fill(search_for)
            page.wait_for_timeout(3000)
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)
            # scrolling
            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]') #move the mouse cursor over a web element to trigger its hover state (like revealing a dropdown menu or changing its color) without clicking it.

            previously_counted = 0
            while True:
                page.mouse.wheel(0, 10000) #literally scrolling the mouse wheel
                page.wait_for_timeout(3000)

                listings_count = page.locator(
                    '//a[contains(@href, "https://www.google.com/maps/place")]'
                ).count()
                
                if listings_count >= total:
                    listings = page.locator(
                        '//a[contains(@href, "https://www.google.com/maps/place")]'
                    ).all()[:total] #Playwright method takes the locator and immediately collects a list of all matching elements currently visible in the Document Object Model (DOM)
                    listings = [listing.locator("xpath=..") for listing in listings]
                    print(f"Total Scraped: {len(listings)}")
                    break
                else:
                    if listings_count == previously_counted:
                        listings = page.locator(
                            '//a[contains(@href, "https://www.google.com/maps/place")]'
                        ).all()
                        print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                        break
                    else:
                        previously_counted = listings_count
                        print(f"Currently Scraped: {listings_count}", end='\r')

            # NEW: Check if listings is defined and non-empty
            if 'listings' not in locals() or not listings:
                print(f"No listings found for {search_for}. Moving to next search.")
                continue #it basically skips a step of the loop when a condition is equal to the if clause and moves to the next one

            # scraping
            newly_added_count = 0
            for listing in listings:
                try:                        
                    listing.click()
                    page.wait_for_timeout(2000)

                    name_attribute = 'h1.DUwDvf'
                    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                    website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                    phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                    review_count_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//span'
                    reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'
                    plus_code_xpath = '//button[@data-item-id="oloc"]//div[contains(@class, "fontBodyMedium")]'
                    business = Business()
                   
                    if name_value := page.locator(name_attribute).inner_text():       #this is the walrus operator, which at the same time sets the variable and returns the condition check to the if loop so that it can verify it and continue 
                        business.name = name_value.strip()
                    else:
                        business.name = None

                    if page.locator(address_xpath).count() > 0:
                        business.address = page.locator(address_xpath).all()[0].inner_text()
                    else:
                        business.address = None

                    if page.locator(website_xpath).count() > 0:
                        business.domain = page.locator(website_xpath).all()[0].inner_text()
                        business.website = f"https://www.{business.domain}"
                    else:
                        business.domain = None
                        business.website = None

                    if page.locator(phone_number_xpath).count() > 0:
                        # Clean up the phone number text to ensure hashing works correctly
                        business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text().strip()
                    else:
                        business.phone_number = None
                        
                    if page.locator(review_count_xpath).count() > 0:
                        # Attempt to parse integer, use None on failure
                        try:
                            text = page.locator(review_count_xpath).inner_text().split()[0].replace(',', '').strip()
                            business.reviews_count = int(text)
                        except:
                            business.reviews_count = None
                    else:
                        business.reviews_count = None
                        
                    if page.locator(reviews_average_xpath).count() > 0:
                        # Attempt to parse float, use None on failure
                        try:
                            text = page.locator(reviews_average_xpath).get_attribute('aria-label').split()[0].replace(',', '.').strip()
                            business.reviews_average = float(text)
                        except:
                            business.reviews_average = None
                    else:
                        business.reviews_average = None
                        
                    if page.locator(plus_code_xpath).count() > 0:
                        business.plus_code = page.locator(plus_code_xpath).all()[0].inner_text()
                    else:
                        business.plus_code = None
                
                    #business.category = search_for.split(' in ')[0].strip() if ' in ' in search_for else search_for
                    #category_xpath = '//button[contains(@aria-label, "Category") or contains(@jsaction, "pane.rating.category") or contains(@data-item-id, "category")]//div'
                    category_xpath = '//button[contains(@jsaction, "pane.place.category")]//div[contains(@class, "fontBodyMedium")]'
                    
                    if page.locator(category_xpath).count() > 0:
                        # Use the text from the located element
                        business.category = page.locator(category_xpath).all()[0].inner_text().strip()
                    else:
                        # Fallback: Scrape the text from the top element after the name,
                        # which is often the category if the structured element isn't found.
                        fallback_category_xpath = '//div[@class="fontBodyMedium"]/span'
                        if page.locator(fallback_category_xpath).count() > 0:
                             business.category = page.locator(fallback_category_xpath).all()[0].inner_text().strip()
                        else:
                             # Use None if no official category could be found
                             business.category = None
                    business.location = search_for.split(' in ')[-1].strip() if ' in ' in search_for else None
                    #business.latitude, business.longitude = extract_coordinates_from_url(page.url)

                    # NEW: Add business and track if it was new
                    if business_list.add_business(business):
                        newly_added_count += 1
                        
                except Exception as e:
                    print(f'Error occurred during scraping: {e}', end='\r')
            
            # --- Output (Modified to overwrite existing file with the complete list) ---
            final_excel_path = os.path.join(BusinessList.save_at, f"{base_filename}.xlsx")
            final_csv_path = os.path.join(BusinessList.save_at, f"{base_filename}.csv")

            # This will save the full list (old unique + new unique)
            business_list.dataframe().to_excel(final_excel_path, index=False)
            business_list.dataframe().to_csv(final_csv_path, index=False)

            print(f"\n--- Update Summary for '{search_for}' ---")
            print(f"Records previously saved: {initial_count}")
            print(f"New unique records added: {newly_added_count}")
            print(f"Total records in file: {len(business_list.business_list)}")
            print(f"File updated: {final_csv_path}")


        browser.close()



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f'Failed err: {e}')
        
        