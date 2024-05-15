import requests
from bs4 import BeautifulSoup
import random
import csv
import time
import certifi
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'
]

def fetch_url(url, headers, timeout=60):
    """Fetches the content of a URL using requests."""
    try:
        with requests.Session() as session:
            session.headers.update(headers)
            response = session.get(url, timeout=timeout, verify=certifi.where())
            response.raise_for_status()
            return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching URL: {e}')
        return None

def scrape_ebay_prices(url, headers, retries=3, timeout=60):
    """Scrapes prices from eBay search results."""
    delay = 5
    for i in range(retries):
        text = fetch_url(url, headers, timeout)
        if text:
            break
        if i < retries - 1:
            logging.info(f'Waiting for {delay:.2f} seconds before retrying...')
            time.sleep(delay)
            delay *= 2
    else:
        logging.error('All attempts to fetch the URL have failed.')
        return None

    soup = BeautifulSoup(text, 'html.parser')
    price_elements = soup.select('.s-item .s-item__info .s-item__price')

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
    """Saves prices to a CSV file."""
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Price"])  # Write the header
            for price in prices:
                writer.writerow([price])
        logging.info(f'Data saved to {filename}')
    except Exception as e:
        logging.error(f'Error saving to CSV: {e}')

def main():
    url = 'insert URL here.'
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    data = scrape_ebay_prices(url, headers)

    if data:
        logging.info(f'Scraped {len(data)} prices from eBay')
        save_prices_to_csv(data, 'ebay_prices.csv')
    else:
        logging.info('Could not find any prices')

if __name__ == '__main__':
    main()
