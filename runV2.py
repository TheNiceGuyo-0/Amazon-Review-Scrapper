from scraper import AmazonReviewScraper 

def main():
    url = input("Enter the Amazon product reviews URL: ").strip()
    if not url:
        print("❌ URL cannot be empty.")
        return

    filename = input("Enter the CSV filename to save reviews (e.g. reviews.csv): ").strip()
    if not filename.endswith(".csv"):
        filename += ".csv"
    
    no_pages = int(input('Enter the number of pages to scrape:'))

    # Initialize scraper
    scraper = AmazonReviewScraper(headless=False)  # set to True if you want headless

    try:
        scraper.open_product_reviews(url)
        scraper.scrape_all_pages(max_pages=no_pages)
        scraper.save_to_csv(filename)
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
