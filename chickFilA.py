import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv

# Set up Selenium WebDriver using WebDriver Manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Define the base URL
base_url = "https://www.chick-fil-a.com/locations/browse"

# Use Selenium to open the website
driver.get(base_url)
time.sleep(5)  # Wait for the page to load completely

# Parse the page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, "html.parser")

# Find all the state links
state_links = soup.select("a[href*='/locations/browse/']")

# Initialize a list to hold all the state locations
all_locations = []

# Loop through all states
for state_link in state_links:
    state_name = state_link.text.strip()
    state_url = f"https://www.chick-fil-a.com{state_link['href']}"

    print(f"Fetching locations for {state_name} from {state_url}...")

    # Use Selenium to open the state-specific page
    driver.get(state_url)
    time.sleep(5)  # Wait for the page to load completely

    # Parse the state page with BeautifulSoup
    state_soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract the location details from 'div' elements with the class 'location'
    locations = state_soup.find_all("div", class_="location")
    if locations:
        for location in locations:
            city_name = location.find("h2").text.strip()
            address_details = location.find("p").text.strip()
            
            # Parse the address details using regex to separate the street, city/state/zip, and phone
            address_lines = address_details.split("\n")
            
            # Assume the last line is always the phone number, if it matches phone pattern
            phone_number = ""
            if re.match(r"\(\d{3}\) \d{3}-\d{4}", address_lines[-1]):
                phone_number = address_lines.pop()  # Remove phone number from the address
            
            # The last line should now be the City, State, ZIP code
            city_state_zip = address_lines.pop()
            
            # The remaining lines are the street address
            street_address = ", ".join(address_lines)
            
            # Append parsed data into the list
            all_locations.append([state_name, city_name, street_address, city_state_zip, phone_number])
    else:
        print(f"No location data found for {state_name}")

# Save the result to a CSV file
csv_filename = "chick-fil-a-locations-all-states.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["State", "City/Location Name", "Street Address", "City, State, ZIP", "Phone Number"])

    for location in all_locations:
        writer.writerow(location)

print(f"All states' data saved to {csv_filename}")

# Close the browser after scraping
driver.quit()
