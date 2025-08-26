import time
import csv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import os


class AmazonReviewScraper:
    def __init__(self, headless: bool = True):
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new") 
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        self.driver = uc.Chrome(options=options)
        self.reviews = []

    def check_for_captcha(self):
        try:
            captcha = self.driver.find_elements(By.CSS_SELECTOR, "form[action='/errors/validateCaptcha']")
            if captcha:
                print("⚠️ CAPTCHA detected! Please solve it manually...")
                input("Press Enter after solving CAPTCHA...")
                return True
        except:
            pass
        return False

    def open_product_reviews(self, url: str):
        print("Opening product reviews page")
        self.driver.get(url)
        time.sleep(5)
    
        if self.check_for_captcha():
            time.sleep(5)

    def scrape_current_page(self):
        print("Scraping reviews on current page...")
        time.sleep(3)
        
        selectors = [
            "div[data-hook='review']",
            ".review",
            ".a-section.review",
            "#cm_cr-review_list div.review",
            "div.a-section.celwidget"
        ]

        review_blocks = None
        for selector in selectors:
            try:
                review_blocks = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if review_blocks:
                    print(f"Found {len(review_blocks)} reviews using selector: {selector}")
                    break
            except:
                continue
        
        if not review_blocks:
            print("⚠️ No reviews found on this page with any selector.")
            
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("Saved page source to debug_page.html for inspection")
            return

        for block in review_blocks:
            try:
                reviewer = block.find_element(By.CSS_SELECTOR, ".a-profile-name, .author, .reviewer-name").text
            except NoSuchElementException:
                reviewer = "N/A"

            try:
                rating_element = block.find_element(By.CSS_SELECTOR, "i[data-hook='review-star-rating'], .a-icon-star, .review-rating")
                rating = rating_element.get_attribute("textContent") or rating_element.text
            except NoSuchElementException:
                rating = "N/A"

            try:
                title = block.find_element(By.CSS_SELECTOR, "a[data-hook='review-title'], .review-title, .a-text-bold").text
            except NoSuchElementException:
                title = "N/A"

            try:
                date = block.find_element(By.CSS_SELECTOR, "span[data-hook='review-date'], .review-date, .a-color-secondary").text
            except NoSuchElementException:
                date = "N/A"

            try:
                body = block.find_element(By.CSS_SELECTOR, "span[data-hook='review-body'], .review-text, .review-body").text
            except NoSuchElementException:
                body = "N/A"

            review = {
                "reviewer": reviewer,
                "rating": rating,
                "title": title,
                "date": date,
                "body": body
            }

            self.reviews.append(review)
            print(f"✓ Collected review from: {reviewer}")

    def go_to_next_page(self):
        try:
            next_button = self.driver.find_element(By.XPATH, '//*[@id="cr-pagination-footer-0"]/a')
            next_button.click()
            time.sleep(2)
            return True
        except NoSuchElementException:
            return False

    def scrape_all_pages(self, max_pages: int = 5):
        for page in range(max_pages):
            print(f"📄 Scraping page {page + 1}...")
            self.scrape_current_page()
            if not self.go_to_next_page():
                break

    def save_to_csv(self, filename: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, filename)
        if not self.reviews:
            print("⚠️ No reviews collected. Nothing to save.")
            return

        unique_reviews = [dict(t) for t in {tuple(d.items()) for d in self.reviews}]
        f_reviews = pd.DataFrame(unique_reviews)

        if len(f_reviews) == 0:
            print("⚠️ No reviews to save after deduplication.")
            return

        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=f_reviews.iloc[0].keys())
            writer.writeheader()
            for _, row in f_reviews.iterrows():
                writer.writerow(row.to_dict())

        print(f"✅ Saved {len(f_reviews)} unique reviews to {filename}")

    def close(self):
        """Close the browser."""
        self.driver.quit()



if __name__ == "__main__":
    PRODUCT_URL = "https://www.amazon.com/Instant-Pot-Duo-Mini-Programmable/dp/B06Y1YD5W7/ref=sr_1_3?_encoding=UTF8&content-id=amzn1.sym.8158743a-e3ec-4239-b3a8-31bfee7d4a15&dib=eyJ2IjoiMSJ9.h0NXGO4UwWV-XKN55HotZihM74HV6IHe6Uz31_prQbwTjRLxhmE7ST9iL_49jMPXNoTFNf2Y3PBzWoT7g-zdUIe_9R6x8dyfwoKEZa2iXpzwOA1GtV8PWBXyx3xgzjcvgZS4yEFnR0zcH4usaa_PJ6aXbSBFhNsCDRLheO9QgBswmbLD9C9h7ayusKgAS_JuapE8QZczV9D4UlnEUugRAsZ90IV9glp5BPt5vqFLgk8.DfWxAcaaJCR_G0CvQQsvhxqzXhGyVlPbpzO-O86DAN8&dib_tag=se&keywords=cooker&pd_rd_r=1e0c58c8-b35d-4348-8051-d4c44c7b76d1&pd_rd_w=5MVvD&pd_rd_wg=XtnWR&qid=1756060455&sr=8-3&th=1#customer-reviews_feature_div"

    scraper = AmazonReviewScraper(headless=False)

    try:
        scraper.open_product_reviews(PRODUCT_URL)
        
        # Check if we're actually on a product page with reviews
        if "customer-reviews" not in scraper.driver.current_url:
            print("⚠️ Not on reviews page. Redirected to:", scraper.driver.current_url)
            # Try to navigate directly to the reviews section
            reviews_url = PRODUCT_URL.replace("#customer-reviews_feature_div", "")
            reviews_url += "#customerReviews"
            print("Trying alternative URL:", reviews_url)
            scraper.driver.get(reviews_url)
            time.sleep(5)
        
        scraper.scrape_all_pages(max_pages=3)
        
        # Save to the script's directory
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "amazon_reviews.csv")
        scraper.save_to_csv(csv_path)
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        # Save what we have anyway
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(script_dir, "amazon_reviews_partial.csv")
        scraper.save_to_csv(csv_path)
    # finally:
    #     scraper.close()