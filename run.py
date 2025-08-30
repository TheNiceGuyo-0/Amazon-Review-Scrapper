import sys
import time
from scraper import AmazonReviewScraper 


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <amazon_reviews_url> [output.csv]")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "amazon_reviews.csv"

    scraper = AmazonReviewScraper(headless=False)  # set to True if you want invisible browser

    try:
        scraper.open_product_reviews(url)
        scraper.scrape_all_pages(max_pages=3)  # adjust max_pages if needed
        scraper.save_to_csv(output_file)
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
