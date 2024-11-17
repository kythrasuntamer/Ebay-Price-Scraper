import time
import logging
import argparse
import random
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium_stealth import stealth
from datetime import datetime
import os

# Setup enhanced logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('scraper.log'), logging.StreamHandler()])

# User-Agent rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
]

# Function to ensure complete loading of dynamic content
def scroll_and_wait(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Function to scrape a single page using Selenium with enhanced waiting and scrolling
def scrape_page_with_selenium(driver, url):
    driver.get(url)
    time.sleep(5)  # Initial wait for page load

    # Scroll and wait for dynamic content
    scroll_and_wait(driver)

    # Save the page source for inspection
    script_directory = os.path.dirname(os.path.abspath(__file__))
    page_source_path = os.path.join(script_directory, "page_source.html")
    with open(page_source_path, "w", encoding="utf-8") as file:
        file.write(driver.page_source)
    logging.info(f"Page source saved to '{page_source_path}' for inspection.")

    try:
        # Wait for elements to load
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 's-item')))
    except Exception as e:
        logging.warning(f"Error waiting for page elements: {e}")

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    items = soup.find_all('li', class_='s-item')

    # Log the number of items found
    logging.info(f"Number of items found: {len(items)}")
    if not items:
        logging.warning("No items found on the page. The page structure may have changed.")
        return []

    # Extract item details with timestamp and URL
    page_results = []
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for item in items:
        title = item.find('div', class_='s-item__title')
        price = item.find('span', class_='s-item__price')
        shipping = item.find('span', class_='s-item__shipping')
        condition = item.find('span', class_='SECONDARY_INFO')
        listing_type = item.find('span', class_='s-item__purchase-options')
        item_link = item.find('a', class_='s-item__link')

        if title and hasattr(title, 'text') and price and hasattr(price, 'text') and item_link and 'href' in item_link.attrs:
            price_text = price.text.replace('$', '').replace(',', '').strip()
            price_value = float(price_text.split()[0]) if price_text.replace('.', '', 1).isdigit() else 0.0

            shipping_text = (shipping.text.replace('$', '').replace(',', '').strip()
                             if shipping else '0.00')
            shipping_value = (
                float(shipping_text.split()[0]) if 'Free' not in shipping_text and shipping_text.replace('.', '', 1).isdigit()
                else 0.0
            )

            total_cost = price_value + shipping_value

            page_results.append({
                'Title': title.text.strip() if title else 'N/A',
                'Price': f"${price_value:.2f}",
                'Shipping Cost': f"${shipping_value:.2f}",
                'Total Cost': f"${total_cost:.2f}",
                'Condition': condition.text.strip() if condition else 'N/A',
                'Listing Type': listing_type.text.strip() if listing_type else 'N/A',
                'URL': item_link['href'],
                'Timestamp': current_time
            })

    return page_results

# Function to save data to an SQLite database
def save_to_sqlite(database_name, table_name, data):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Create table if it doesn't exist (using double quotes to escape the table name)
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT,
            Price TEXT,
            Shipping_Cost TEXT,
            Total_Cost TEXT,
            Condition TEXT,
            Listing_Type TEXT,
            URL TEXT,
            Timestamp TEXT
        )
    ''')

    # Insert data into table
    for item in data:
        cursor.execute(f'''
            INSERT INTO "{table_name}" (Title, Price, Shipping_Cost, Total_Cost, Condition, Listing_Type, URL, Timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item['Title'], item['Price'], item['Shipping Cost'], item['Total Cost'], item['Condition'], item['Listing Type'], item['URL'], item['Timestamp']))

    conn.commit()
    conn.close()
    logging.info(f"Data has been saved to the '{table_name}' table in {database_name}.")

# Main function to search for an item, scrape eBay prices, and save to an SQL database
def scrape_ebay_prices_to_sqlite(search_query, database_name='ebay_prices.db', table_name='ebay_data', delay=1, max_pages=1, min_price=0, filter_keywords=[]):
    base_url = "https://www.ebay.com/sch/i.html?_nkw={}&_pgn={}"
    search_query_formatted = search_query.replace(' ', '+')

    # Setup Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")  # Rotate User-Agent

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Apply stealth settings to the driver
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    results = []
    for page in range(1, max_pages + 1):
        url = base_url.format(search_query_formatted, page)
        logging.info(f"Scraping page {page}...")
        page_results = scrape_page_with_selenium(driver, url)
        if page_results:
            results.extend(page_results)
        time.sleep(random.uniform(delay, delay + 5))  # Randomized delay

    driver.quit()

    # Filter out items with 'Total Cost' below the specified min_price
    results = [item for item in results if float(item['Total Cost'].replace('$', '').strip()) >= min_price]

    # Filter out items that contain any of the specified filter keywords in the title
    if filter_keywords:
        results = [item for item in results if not any(keyword.lower() in item['Title'].lower() for keyword in filter_keywords)]

    # Sort results by the 'Total Cost' field (convert to float for sorting)
    results.sort(key=lambda x: float(x['Total Cost'].replace('$', '').strip()))

    # Save the filtered and sorted results to the SQLite database
    if results:
        save_to_sqlite(database_name, table_name, results)
    else:
        logging.warning("No data to save after filtering. Check 'page_source.html' for the page structure or adjust the filter criteria.")

# Main block to handle command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search eBay for an item and save details to an SQLite database using Selenium with stealth integration.")
    parser.add_argument('search_query', type=str, help='The search query for the item on eBay')
    parser.add_argument('--database_name', type=str, default='ebay_prices.db', help='SQLite database file name (default: ebay_prices.db)')
    parser.add_argument('--table_name', type=str, default='ebay_data', help='Table name in the database (default: ebay_data)')
    parser.add_argument('--delay', type=float, default=1, help='Delay between requests in seconds (default: 1)')
    parser.add_argument('--max_pages', type=int, default=1, help='Number of pages to scrape (default: 1)')
    parser.add_argument('--min_price', type=float, default=0, help='Minimum price threshold to filter results (default: 0)')
    parser.add_argument('--filter_keywords', type=str, nargs='*', help='Keywords to filter out items by title (e.g., "used refurbished")', default=[])

    args = parser.parse_args()

    # Run the scraper with provided arguments
    scrape_ebay_prices_to_sqlite(args.search_query, args.database_name, args.table_name, args.delay, args.max_pages, args.min_price, args.filter_keywords)
