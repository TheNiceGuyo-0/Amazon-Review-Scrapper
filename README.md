# Amazon Review Scraper

A Python web scraper that extracts product reviews from Amazon using Selenium and undetected-chromedriver.

## ✨Features

- Extracts **reviewer name, rating, title, date, and review text**
- Handles **CAPTCHA detection** with manual intervention
- Detects and handles **Amazon login page redirects**
- **Pagination support** to scrape multiple review pages
- Saves results to **CSV format**
- Two run modes:
  - **`run.py`** → accepts URL & output filename as command-line arguments
  - **`runV2.py`** → interactive input prompts (URL, CSV filename, and number of pages)

## 🛠️Requirements

- Python 3.x
- undetected-chromedriver
- selenium
- pandas

## 🚀Usage

Run with command-line arguments (run.py): python run.py "<amazon_reviews_url>" output.csv

Example: 
```bash
python run.py "https://www.amazon.com/product-reviews/B06Y1YD5W7" reviews.csv

```
OR

Run with interactive input (runv2.py): 
```bash 
python runV2.py
```

You’ll be asked to enter:
- The Amazon product reviews URL
- The CSV filename (e.g. my_reviews.csv)
- The number of pages to scrape

## Notes

Amazon may occasionally show a CAPTCHA or redirect to login.
In such cases, the scraper will pause and ask you to solve/login manually, then continue scraping.

To avoid issues, scrape responsibly and don’t overload requests.

## Status

This project is actively being improved.
Next steps may include:
- Adding review filtering (by date range, rating, etc.)
- Parallel scraping for faster collection