import pandas as pd
import argparse
import os
from openlocationcode import openlocationcode as olc
from geopy.geocoders import Nominatim
import time

def locations(file_path):
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)

    if 'plus_code' not in df.columns:
        print("Error: No 'plus_code' column in the file")
        return
#pluscode_decoder is just a name for the user agent to identify the application, could be any string
    geolocator = Nominatim(user_agent="pluscode_decoder")
    city_cache = {}  # Cache coordinates to avoid repeated geocoding

    for idx, row in df.iterrows():
        full_string = str(row['plus_code']).strip() 
        string_divided = full_string.split(maxsplit=1) #splitting the full string at the first space['75WG+R4', 'Tsim Sha Tsui, Hong Kong']
        short_code = string_divided[0].strip()
        location_str = string_divided[1].strip() if len(string_divided) > 1 else None #so string_divided is a list actually, and I am checking its length 

        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            continue  # skip the rest of the loop for this row and move to the next row

        try:
            if olc.isFull(short_code):
                area = olc.decode(short_code) #basically never working because the short code is never going to be be exhaustive
            elif olc.isShort(short_code):
                if not location_str:
                    raise ValueError("Short code requires a reference location")
                if location_str not in city_cache:         #if you already geocoded before 
                    location = geolocator.geocode(location_str)
                    if location is None:
                        raise ValueError(f"Could not geocode '{location_str}'")
                    ref_lat, ref_lng = location.latitude, location.longitude
                    city_cache[location_str] = (ref_lat, ref_lng)
                    time.sleep(1)  # Avoid hitting geocoder rate limits

                full_code = olc.recoverNearest(short_code, ref_lat, ref_lng)
                area = olc.decode(full_code)

            else:
                raise ValueError(f"Invalid plus code: {short_code}")

            df.loc[idx, 'latitude'] = area.latitudeCenter
            df.loc[idx, 'longitude'] = area.longitudeCenter
        except Exception as e:
            print(f"❌ Row {idx} failed: {e}")

    # Save updated file
    df.to_excel(file_path, index=False)
    csv_file_path = os.path.splitext(file_path)[0] + ".csv"
    df.to_csv(csv_file_path, index=False)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode Plus Codes automatically")
    parser.add_argument("-f", "--file", required=True, help="Path to the Excel file containing the plus codes")
    args = parser.parse_args()

    locations(args.file)
