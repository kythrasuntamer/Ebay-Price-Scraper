Rudimentary eBay Price scraper. I've got plans to continue refining this into something much more useful. But it's free.

USAGE:
pip install -r requirements.txt

python eBay_scraper.py "Your Search Query" --output_file "output.db" --delay 1 --max_pages 2 -filter_keyword

Example:
python eBay.py "gaming laptop" --output_file "gaming_laptops.db" --min_price 150 --max_pages 5 --filter_keywords "used" "refurbished"
