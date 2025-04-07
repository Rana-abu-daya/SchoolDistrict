# School District Voter Data Processing

## Overview
This Python script processes voter data to assign school districts and maintains source information for the assignments. The program uses asynchronous processing to handle the data efficiently.

## Features
- Asynchronous processing of school district assignments
- Processes voter data and assigns school districts
- Tracks sources for district assignments
- Saves results to CSV format

## Requirements
- Python 3.7+
- pandas
- asyncio

## Usage
1. Ensure you have the required voter data file
2. Make sure you add Archive.zip and Uncompress the zip file in the project dirct 
3. Run the script:
```python
python district2.py

The script generates a CSV file named "voter_data_with_school_districts_final1.csv" containing:
Original voter data
Assigned school districts
Source information


The code tried to get School district From Census API
if the API Failed, get the LAN and LAT of the address to get the school district using shp file 



use this link to download the zip file with shp file and the others
https://data-nces.opendata.arcgis.com/datasets/nces::school-district-boundaries-current/about
or use this link https://geo.wa.gov/datasets/WAOSPIGIS::washington-school-districts-2024/about
choose shapefile download option
Click Download button to view file formats
Look for the Shapefile and click Download
This will download a zip file containing the shapefile and associated files
Unzip the files into the repo directory
Rename the files to:
school_district_boundaries.cpg
school_district_boundaries.dbf
school_district_boundaries.prj
school_district_boundaries.shp
school_district_boundaries.shx
school_district_boundaries.xml



