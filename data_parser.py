import requests
from bs4 import BeautifulSoup
import time
import json

# URL to scrape
url = "http://www.ufcstats.com/statistics/events/completed?page=all"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code != 200:
   print(f"Failed to retrieve the page. Status code: {response.status_code}")
   
# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Extract all elements with the class 'b-statistics__table-row'
rows = soup.find_all(class_='b-statistics__table-row')

# Extract all hrefs from 'a' tags within the rows
hrefs = []
for row in rows:
    links = row.find_all('a', href=True)
    hrefs.extend([link['href'] for link in links])

# Remove duplicates while preserving order
unique_hrefs = list(dict.fromkeys(hrefs))[::-1]

# Display the number of hrefs found
print(f"Number of unique hrefs found: {len(unique_hrefs)}")


all_fights = []
drawCount = 0

# Loop through each event URL
for i, url in enumerate(unique_hrefs):
    print(f"Scraping URL {i+1}/{len(unique_hrefs)}: {url}")
    
    # Send an HTTP GET request to the URL
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract elements with all the specified classes
        fight_details = soup.find_all('tr', class_='b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click')
        fight_details = fight_details[::-1]
        
        # Loop through each fight detail and extract fighter names
        for detail in fight_details:

            isDraw = None == detail.find('a', 'b-flag b-flag_style_green')

            if isDraw:
                drawCount += 1
                continue

            method_column = detail.find_all('td', 'b-fight-details__table-col l-page_align_left')[2]
            method = method_column.find_all('p', 'b-fight-details__table-text')[0].get_text(strip=True)
            # print(method)



            fight_data = []
            fighters = detail.find_all('a', class_='b-link b-link_style_black')
            
            # Extract the names of the two fighters
            for fighter in fighters[:2]:  # There should be two fighter links per fight
                fighter_name = fighter.get_text(strip=True)
                fight_data.append(fighter_name)
            
            fight_data.append(method)
            
            if len(fight_data) == 3:
                all_fights.append(fight_data)
        
    else:
        print(f"Failed to retrieve the page at {url}. Status code: {response.status_code}")
    
    # Pause to avoid getting blocked
    # time.sleep(0.5)  # Wait 1 seconds between requests

# Convert the fight results to a list of dictionaries
fight_results = [{"winner": fight[0], "loser": fight[1], 'method': fight[2]} for fight in all_fights]

print(f"Draw count: {drawCount}")

# Save the results to a JSON file
output_file_path = './fight_results.json'
with open(output_file_path, 'w') as json_file:
    json.dump(fight_results, json_file, indent=4)