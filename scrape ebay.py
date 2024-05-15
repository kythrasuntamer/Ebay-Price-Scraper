import requests
from bs4 import BeautifulSoup
import random
import csv
import time
import certifi
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List of user agents
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'
]

def scrape_ebay_prices(url, retries=3, timeout=60):
    delay = 5  # Initial delay in seconds
    for i in range(retries):
        try:
            # Randomly select a user agent
            headers = {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',  # Add a referer header
                'robots': 'noindex, nofollow'  # Ignore robots.txt
            }
            logging.info(f"Attempt {i + 1}: Fetching URL with headers: {headers}")
            response = requests.get(url, headers=headers, timeout=timeout, verify=certifi.where(), stream=True)
            response.raise_for_status()
            break  # Break if the request was successful
        except requests.exceptions.HTTPError as e:
            logging.error(f'Attempt {i + 1}: HTTP error: {e}')
        except requests.exceptions.RequestException as e:
            logging.error(f'Attempt {i + 1}: There was a problem accessing the URL: {e}')
        
        if i < retries - 1:  # If it's not the last retry, wait before retrying
            logging.info(f'Waiting for {delay:.2f} seconds before retrying...')
            time.sleep(delay)
            delay *= 2  # Exponential backoff
    else:
        # If the loop exits normally (without break), return None indicating failure
        logging.error('All attempts to fetch the URL have failed.')
        return None

    # Try decoding the response using multiple encodings
    encodings = ['utf-8', 'iso-8859-1']
    for encoding in encodings:
        try:
            text = ''
            for chunk in response.iter_content(chunk_size=1024):
                text += chunk.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        logging.error('Failed to decode the response using any of the specified encodings.')
        return None

    soup = BeautifulSoup(text, 'html.parser')

    # Use a more specific CSS selector to target the price elements
    price_elements = soup.select('li.s-item .s-item__price')

    prices = []
    if price_elements:
        for element in price_elements:
            price = element.text.strip()
            prices.append(price)
        return prices
    else:
        logging.info('No price elements found on the page.')
        return []

def save_prices_to_csv(prices, filename):
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Price", "Capture Date and Time"])  # Write the header
            for price in prices:
                writer.writerow([price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        logging.info(f'Prices saved to {filename}')
    except Exception as e:
        logging.error(f'Error saving to CSV: {e}')

def main():
    url = 'INSERT URL HERE'  # Replace with the actual eBay search URL
    prices = scrape_ebay_prices(url)

    if prices:
        logging.info(f'The prices are {prices}')
        save_prices_to_csv(prices, 'ebay_prices.csv')
    else:
        logging.info('Could not find any prices')

if __name__ == '__main__':
    main()
