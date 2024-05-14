import requests
from bs4 import BeautifulSoup

def scrape_ebay_prices(url):
try:
# Add a user agent to mimic a real browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
response = requests.get(url, headers=headers)
response.raise_for_status()
except Exception as e:
print(f'There was a problem accessing the URL: {e}')
return None

soup = BeautifulSoup(response.text, 'html.parser')

# Use a more specific CSS selector to target the price elements
price_elements = soup.select('li.s-item > div.s-item__info > div.s-item__price')

if price_elements:
    prices = [element.text.strip() for element in price_elements]
    return prices
else:
    return []

url = 'INSERT URL HERE'
prices = scrape_ebay_prices(url)

if prices:
print(f'The prices are {prices}')
else:
print('Could not find any prices')
