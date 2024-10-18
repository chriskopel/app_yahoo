import requests
from bs4 import BeautifulSoup
import gspread
from datetime import datetime

### Scrape
## Config Details
app_url = 'https://finance.yahoo.com/quote/APP/holders/'
agent = 'Mozilla/5.0 (Windows NT 10.0; Windows; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'


## Scrape
response = requests.get(app_url, headers={'User-Agent': agent})
soup = BeautifulSoup(response.text, 'html.parser')

## Dissect
# Locate the section containing the "Major Holders" table by the section's `data-testid` attribute
section = soup.find('section', {'data-testid': 'holders-major-holders-table'})
# Find all 'td' elements within the section to extract the data
td_elements = section.find_all('td', class_='majorHolders')

## Load dict
# Initialize an empty dictionary
holders_dict = {}

# Iterate through the list in pairs (numeric value and its corresponding label)
for i in range(0, len(td_elements), 2):
    # Strip any extra characters and clean up the value
    value = td_elements[i].text.strip().replace('%', '')
    
    # Convert the value to float or integer as appropriate
    if '.' in value:
        value = float(value)
    else:
        value = int(value)
    
    # Get the corresponding key (label)
    label = td_elements[i+1].text.strip()
    
    # Update the dictionary
    holders_dict[label] = value


### Send to GSheet
## Config details
sa_path = r"C:\Users\Owner\AppData\Local\Programs\Python\Python310\Lib\site-packages\gspread\service_account.json"
gc = gspread.service_account(filename=sa_path)


## Open the sheet
sh = gc.open("APP Ownership")
worksheet = sh.worksheet("Data")  # Access the "Data" sheet


## Insert data
# Insert a new row at position 2 (shifts existing row 2 and below down)
worksheet.insert_row([], 2)

# Extract the values in the correct order (A, B, C, D, E)
values = [
    holders_dict["% of Shares Held by All Insider"],
    holders_dict["% of Shares Held by Institutions"],
    holders_dict["% of Float Held by Institutions"],
    holders_dict["Number of Institutions Holding Shares"],
    datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " MT"
]

# Update row 2 with the new data in columns A to E
worksheet.update('A2:E2', [values])