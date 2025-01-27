# from geopy.geocoders import Nominatim
# import pandas as pd
# import  ssl
# import time
# import geopandas as gpd
# from shapely.geometry import Point
#
# gdf = gpd.read_file('school_district_boundaries.shp')
# print("read school_district_boundaries data ")
#
#
# # Load voter data
# voter_data = pd.read_csv("failed_school_districts.csv")
# voter_data['Address'] = voter_data['Address'].str.strip()
# voter_data['City'] = voter_data['City'].str.strip()
# voter_data['Zip Code'] = voter_data['Zip Code'].astype(str).str.zfill(5)
# voter_data = voter_data[0:1000].copy()
# # Disable SSL verification (not secure)
# ssl_context = ssl.create_default_context()
# ssl_context.check_hostname = False
# ssl_context.verify_mode = ssl.CERT_NONE
#
# def find_school_district(lat: float, lon: float) -> str:
#     print("I am in finding school district")
#     """
#     Identifies the school district for a given latitude and longitude using a shapefile.
#
#     This function loads a shapefile containing school district boundaries, creates a point
#     from the provided latitude and longitude, and checks which school district polygon contains
#     the point. It returns the name of the school district if found.
#
#     Parameters:
#     - lat (float): The latitude of the address.
#     - lon (float): The longitude of the address.
#
#     Returns:
#     - str: The name of the school district the address belongs to, or "District not found" if not found.
#     """
#
#
#     # Create a Point object from the latitude and longitude
#     point = Point(lon, lat)
#
#     # Check which polygon from the shapefile contains the point
#     # The result is a GeoDataFrame with the rows that match the condition
#     containing_district = gdf[gdf.contains(point)]
#
#     if not containing_district.empty:
#         # Assuming the district name is in a column named 'NAME'
#         return containing_district.iloc[0]['NAME']
#     else:
#         return "District not found."
#
#
#
# def get_lat_lon(address):
#     geolocator = Nominatim(user_agent="geoapi", ssl_context=ssl_context)
#
#     try:
#         location = geolocator.geocode(address)
#         if location:
#             return location.latitude, location.longitude
#         else:
#             return None
#     except Exception as e:
#         return f"An error occurred: {e}"
#
#
# for _, row in voter_data.iterrows():
#     if not row['Address'] or not row['City']:
#         print("Invalid address:", row)
#         continue
#
#     address = f"{row['Address']}, {row['City']}, WA {row['Zip Code']}"
#     result = get_lat_lon(address)
#
#     if isinstance(result, tuple):
#         lat, lon = result
#         print(lat, lon , address)
#         print(find_school_district(lat,lon))
#     else:
#         address = f"{row['City']}, WA {row['Zip Code']}"
#         result = get_lat_lon(address)
#         print("Error with address:",address, " ", result)
#         lat, lon = result
#         print(find_school_district(lat, lon))
#
#     time.sleep(3)
#

import pandas as pd
import asyncio
import aiohttp
import time
from geopy.geocoders import Nominatim
import ssl
import geopandas as gpd
from shapely.geometry import Point

# Load shapefile for fallback district lookup
gdf = gpd.read_file('school_district_boundaries.shp')
print("Loaded school district boundaries.")

# Load voter data
voter_data = pd.read_csv("AMAC_Voters_Data_Religion_wise_bulk.csv")
voter_data['Address'] = voter_data['Address'].str.strip()
voter_data['City'] = voter_data['City'].str.strip()
voter_data['Zip Code'] = voter_data['Zip Code'].astype(str).str[:5].str.zfill(5)
#voter_data = voter_data[0:1000].copy()

# Disable SSL verification (not secure)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Fallback: Find district from lat/lon using the shapefile
def find_school_district(lat: float, lon: float) -> str:
    point = Point(lon, lat)
    containing_district = gdf[gdf.contains(point)]
    if not containing_district.empty:
        return containing_district.iloc[0]['NAME']
    return "District not found"

# Fallback: Get latitude and longitude using geopy
def get_lat_lon(address):
    geolocator = Nominatim(user_agent="geoapi", ssl_context=ssl_context)
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
    return None

# Primary: Fetch district using the Census API
async def get_school_district(session, address, city, zip_code, retries=3, delay=2):
    zip_code = str(zip_code).zfill(5)
    base_url = "https://geocoding.geo.census.gov/geocoder/geographies/address"
    params = {
        "street": address,
        "city": city,
        "zip": zip_code,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "format": "json",
        "layers": "14,16,18"
    }

    for attempt in range(retries):
        try:
            async with session.get(base_url, params=params, ssl=False) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('result') and result['result'].get('addressMatches'):
                        geographies = result['result']['addressMatches'][0]['geographies']
                        unified = geographies.get('Unified School Districts', [{}])
                        secondary = geographies.get('Secondary School Districts', [{}])
                        elementary = geographies.get('Elementary School Districts', [{}])

                        # Prioritize district types
                        if unified and unified[0].get('NAME'):
                            return unified[0]['NAME'], "API"
                        elif secondary and secondary[0].get('NAME'):
                            return secondary[0]['NAME'], "API"
                        elif elementary and elementary[0].get('NAME'):
                            return elementary[0]['NAME'], "API"
        except Exception as e:
            print(f"Error fetching district for {address}, {city}, {zip_code} on attempt {attempt + 1}: {e}")
        await asyncio.sleep(delay)

    return None, "API"

# Process voter data asynchronously
async def process_school_districts(voter_data):
    school_districts = []
    sources = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for _, row in voter_data.iterrows():
            task = get_school_district(session, row['Address'], row['City'], row['Zip Code'])
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, tuple) and result[0]:
                school_districts.append(result[0])
                sources.append(result[1])
            else:
                # Fallback to geopy + shapefile
                address = f"{voter_data.iloc[i]['Address']}, {voter_data.iloc[i]['City']}, WA {voter_data.iloc[i]['Zip Code'].zfill(5)}"
                lat_lon = get_lat_lon(address)
                if lat_lon:
                    lat, lon = lat_lon
                    district = find_school_district(lat, lon)
                    school_districts.append(district)
                    sources.append("LatLon")
                    print(f"Fallback success: {district} for {address} using Lat/Lon.")
                else:
                    address = f"{voter_data.iloc[i]['City']}, WA {voter_data.iloc[i]['Zip Code'].zfill(5)}"
                    lat_lon = get_lat_lon(address)
                    if lat_lon:
                        lat, lon = lat_lon
                        district = find_school_district(lat, lon)
                        school_districts.append(district)
                        sources.append("LatLon*")
                        print(f"Fallback success: {district} for {address} using Lat/Lon.")
                    else:
                        print(address, lat_lon,"HERE")
                        school_districts.append("District not found")
                        sources.append("Failed")
                        print(f"Fallback failed for {address}.")

    return school_districts, sources

# Run the async process
async def main():
    districts, sources = await process_school_districts(voter_data)
    voter_data['School District'] = districts
    voter_data['Source'] = sources

asyncio.run(main())

# Save the results
output_path = "voter_data_with_school_districts_final1.csv"
voter_data.to_csv(output_path, index=False)

print(f"School district mapping completed and saved to {output_path}")
# Final step: Create a file with district name and number of Muslims in each district
district_counts = voter_data.groupby('School District').size().reset_index(name='Muslim Count')
output_path_counts = "district_muslim_counts.csv"
district_counts.to_csv(output_path_counts, index=False)

print(f"District counts saved to {output_path_counts}")