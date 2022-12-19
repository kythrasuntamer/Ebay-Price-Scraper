import time
import mysql.connector
import requests
from bs4 import BeautifulSoup

# Connect to the MySQL database
cnx = mysql.connector.connect(user='user', password='password', host='host', database='database')
cursor = cnx.cursor()

def scrape_ebay_prices(url):
    # Set the user agent string
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    # Send an HTTP request to the URL
    try:
        response = requests.get(url, headers=headers)
        # If the response is successful, no Exception will be raised
        response.raise_for_status()
    except Exception as e:
        # An exception is raised, return None
        print(f'There was a problem accessing the URL: {e}')
        return None
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all elements containing a price
    price_elements = soup.find_all('span', {'class': 's-item__price'})
    
    # Extract the price text from each element and return it in a list
    if price_elements:
        prices = [element.text for element in price_elements]
        return prices
    else:
        # Return an empty list if no elements were found
        return []

urls = ['https://www.ebay.com/itm/example1', 'https://www.ebay.com/itm/example2', ...]

# Set the rate limit to 1 request per second
rate_limit = 1

for url in urls:
    # Wait for the rate limit
    time.sleep(1 / rate_limit)
    
    # Scrape the prices
    prices = scrape_ebay_prices(url)
    
    if prices:
        # Insert the scraped data into the database
        query = 'INSERT INTO prices (url, price) VALUES (%s, %s)'
        values = [(url, price) for price in prices]
        cursor.executemany(query, values)
        cnx.commit()
        
        print(f'Scraped {len(prices)} prices from {url}')
    else:
        print(f'Could not find any prices on {url}')

# Close the database connection
cnx.close()
