import scrapy
import mysql.connector

class EbayPriceSpider(scrapy.Spider):
    name = 'ebay_price'
    
    def __init__(self):
        # Connect to the MySQL database
        self.cnx = mysql.connector.connect(user='user', password='password', host='host', database='database')
        self.cursor = self.cnx.cursor()
        
    def start_requests(self):
        urls = ['https://www.ebay.com/itm/example1', 'https://www.ebay.com/itm/example2', ...]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all elements containing a price
        price_elements = soup.find_all('span', {'class': 's-item__price'})
        
        if price_elements:
            # Extract the price text from each element and yield it
            for element in price_elements:
                price = element.text
                yield {'price': price}
        else:
            # Handle the case where no price elements were found
            print(f'Could not find any prices on {response.url}')
            yield {}
