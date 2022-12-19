import requests
from bs4 import BeautifulSoup

# Specify the URL of the eBay page you want to scrape
url = 'https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw=gtx+4090&_sacat=0'

# Make a request to the page
page = requests.get(url)

# Create a BeautifulSoup object to parse the HTML of the page
soup = BeautifulSoup(page.content, 'html.parser')

# Find all the elements on the page with the class "s-item__price"
prices = soup.find_all(class_='s-item__price')

# Print the text content of each element
for price in prices:
  print(price.text)