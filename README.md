# Amazon Review Scraper

A Python web scraper that extracts product reviews from Amazon using Selenium and undetected-chromedriver.

## Features

- Extracts reviewer name, rating, title, date, and review text
- Handles CAPTCHA detection with manual intervention
- Pagination through multiple review pages
- Saves results to CSV format

## Requirements

- Python 3.x
- undetected-chromedriver
- selenium
- pandas

## Usage

1. Install dependencies: `pip install undetected-chromedriver selenium pandas`
2. Update the `PRODUCT_URL` variable with your target Amazon product URL
3. Run: `python scraper.py`

The script will generate `amazon_reviews.csv` with the scraped data.