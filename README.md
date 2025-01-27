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





