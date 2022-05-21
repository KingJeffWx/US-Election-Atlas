import requests
from bs4 import BeautifulSoup
import json
import csv
import time
 
election_data = dict()
counties = dict()

# GET FIPS codes
url = 'https://www.nrcs.usda.gov/wps/portal/nrcs/detail/national/home/?cid=nrcs143_013697'
r = requests.get(url)

soup = BeautifulSoup(r.content, 'html.parser')
table = soup.find('table', class_='data')
county_list = table.text.split('\n')
county_list.remove('FIPS')
county_list.remove('Name')
county_list.remove('State')
i = 0
while i < len(county_list):
    if county_list[i] == '':
        i += 1
    elif county_list[i] != '':
        counties[county_list[i]] = (county_list[i+1], county_list[i+2])
        i += 3
print('Done reading FIPS codes')

# GET US Elections Atlas
start = time.time()
count = 0
limit = 99999
year = 2012
for fips in counties.keys():
    if count < limit:
        url = 'https://uselectionatlas.org/RESULTS/statesub.php?year=' + str(year) + '&fips=' + str(fips) + '&f=1&off=0&elect=0'
        r = requests.get(url)
    
        # Parsing the HTML
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', class_='result')
        
        table_text = table.text.split('\n')
        dem_percent = 0.0
        rep_percent = 0.0
        for i in range(len(table_text)):
            if 'Democratic' in table_text[i]:
                dem_percent = float(table_text[i+2][:-1])
            if 'Republican' in table_text[i]:
                rep_percent = float(table_text[i+2][:-1])

        election_data[fips] = (dem_percent, rep_percent)
        count += 1
end = time.time()
print('Done reading from US Election Atlas, took', end - start, 'sec')

# Output to CSV
header = ['County', 'State', 'Dem', 'Rep']
data = list()
for fips in election_data:
    county = counties[fips][0]
    state = counties[fips][1]
    dem = election_data[fips][0]
    rep = election_data[fips][1]
    data.append([county, state, dem, rep])

filename = str(year) + 'electiondata.csv'
with open(filename, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write multiple rows
    writer.writerows(data)
print('Done outputting to CSV')