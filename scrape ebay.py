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
        logging.error(f'Error fetching URL {url}: {e}')
        return None

def extract_price(price_str):
    """Extracts a single price from a price string that may be a range."""
    try:
        prices = [float(p.strip().replace('$', '').replace(',', '')) for p in price_str.split('to')]
        return min(prices) if len(prices) > 1 else prices[0]
    except ValueError:
        return None

def scrape_ebay_data(url, headers, retries=3, timeout=60):
    """Scrapes item titles, prices, and saves the time and date to the CSV file."""
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
        logging.error(f'All attempts to fetch the URL {url} have failed.')
        return None

    soup = BeautifulSoup(text, 'html.parser')
    items = soup.select('.s-item')

    data = []
    if items:
        for item in items:
            title_element = item.select_one('.s-item__title')
            price_element = item.select_one('.s-item__price')
            if title_element and price_element:
                title = title_element.text.strip()
                price = extract_price(price_element.text.strip())
                if price is not None:  # Ensure price is valid before appending
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    data.append([title, price, timestamp])
                else:
                    logging.warning(f'Skipping item "{title}" on URL {url} due to invalid price')
            else:
                logging.warning(f'Skipping item on URL {url} due to missing data')
    else:
        logging.info(f'No items found on the page {url}.')

    # Sort data by price in descending order
    data.sort(key=lambda x: x[1] if x[1] is not None else float('inf'), reverse=True)
    
    return data

def save_data_to_csv(data, filename):
    """Appends item data to a CSV file."""
    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for row in data:
                if len(row) == 3:  # Ensure each row has title, price, and timestamp
                    writer.writerow(row)
                else:
                    logging.warning(f'Skipping invalid data: {row}')
        logging.info(f'Data appended to {filename}')
    except Exception as e:
        logging.error(f'Error appending to CSV: {e}')

def main():
    url = 'insert url here'
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    data = scrape_ebay_data(url, headers)

    if data:
        logging.info(f'Scraped {len(data)} items from eBay')
        save_data_to_csv(data, 'ebay_data_sorted.csv')
    else:
        logging.info('Could not find any items')

if __name__ == '__main__':
    main()
