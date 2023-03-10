import scrapy
import mysql.connector
import smtplib
from email.mime.text import MIMEText

class EbayPriceSpider(scrapy.Spider):
    name = 'ebay_price'
    
    def __init__(self, threshold=100, **kwargs):
        # Connect to the MySQL database
        self.cnx = mysql.connector.connect(user='user', password='password', host='host', database='database')
        self.cursor = self.cnx.cursor()
        
        # Set the price threshold
        self.threshold = threshold
        
        # Set the email server and sender/recipient information
        self.mail_server = 'smtp.gmail.com'
        self.mail_port = 587
        self.mail_username = 'user@example.com'
        self.mail_password = 'password'
        self.mail_sender = 'user@example.com'
        self.mail_recipient = 'recipient@example.com'
        
        super().__init__(**kwargs)
    
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
                
                # Check if the price is below the threshold
                if float(price) < self.threshold:
                    # Send an email notification
                    self.send_alert_email(price)
        else:
            # Handle the case where no price elements were found
            print(f'Could not find any prices on {response.url}')
            yield {}
    
    def send_alert_email(self, price):
        # Set the email subject and message
        subject = f'Price Alert: Item is now ${price}'
        message = f'The price of the item has fallen

