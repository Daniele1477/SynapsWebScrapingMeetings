# **Google Maps Scraper**<br/>

A customizable working Google Maps scraper that builds up from what the community had already published and adds a few tweaks to make 
it more suitable to research and maps visualizations. 


### **After having installed the dependencies:** <br/>
pip install playwright <br/>
pip install pandas <br/>
playwright install chromium  <br/>

The program it's either runnable by parsing the arguments within the terminal, where s stands for search and t is a limit to the maximum number of result <br/>
##Example:<br/>
python3 main.py -s="coffee shops in Boston" -t=50  <br/>

Or by adding one by line the queries to 'input.txt': <br/>
pharmacies in Amman
Hospital in Aqaba  

And then executing (with 't' of your choice): <br/>
python3 WebScrapingFramework.py -t=100 


The data will be saved in the GMaps Data in folders that follow the 'dd-mm-yyyy' format 

## Getting the POI real coordinates <br/>
**Getting the location was an issue because the coordinates Google provides in the URL come from it placing the item in the centre of the map, hence they don't reflect the actual geo spatial coordinates**

In order to get the location, a second program ('Location.py') decrypts the Plus Code scraped from Google Maps website. <br/>
Plus Codes are simple, open-source digital addresses (like "87G8+F2") that provide a universal addressing system for any location, especially useful where traditional street names and numbers don't exist, allowing for precise location sharing for deliveries, services, and navigation, by converting latitude/longitude into short alphanumeric codes. <br/>

### **To execute the program, run:** <br/>
python3 Location.py -f 'GMaps Data/2025-12-15/supermarkets_in_Milan.xlsx' <br/>
Make sure to write the right file path <br/>

## **Plotting a map** <br/>

SampleMap.ipynb is a simple jupyter notebook that takes the df that now has the right latitude and longitude, and converts them into 
numerical numbers (before they were strings) to parse to a new GeoDataFrame, that has been called gdf, that will encode them within the column 'Geometry', in order to plot them into a map (arbitrarily called m). All of this relies on the powerful Geopandas and Pandas libraries so make sure to have them installed them beforehand <br/>
pip install pandas <br/>
pip install geopandas  <br/>

Make sure to execute each cell in order and in the last one it will compile the html map locally ready for visualization 
