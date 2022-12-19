import requests
from bs4 import BeautifulSoup

def scrape_ebay_prices(url):
    # Send an HTTP request to the URL
    try:
        response = requests.get(url)
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

url = 'INSERT URL HERE' 
prices = scrape_ebay_prices(url)

if prices:
    print(f'The prices are {prices}')
else:
    print('Could not find any prices')
