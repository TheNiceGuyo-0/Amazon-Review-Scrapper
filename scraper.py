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
            # Check if redirected to login
            if "ap/signin" in self.driver.current_url:
                print("⚠️ Amazon login page detected. Please log in manually...")
                input("Press Enter after logging in to continue...")
                return True

            next_page_select = [
                '//*[@id="cr-pagination-footer-0"]/a',
                '//*[@id="cm_cr-pagination_bar"]/ul/li[2]/a'
            ]
            next_button = None
            for button in next_page_select: 
                try:
                    next_button = self.driver.find_element(By.XPATH, button)
                    if next_button:
                        next_button.click()
                    time.sleep(3)
                except:
                    continue

            # After clicking, check again for login redirect
            if "ap/signin" in self.driver.current_url:
                print("⚠️ Amazon login page detected. Please log in manually...")
                input("Press Enter after logging in to continue...")
                return True

            return True
        except NoSuchElementException:
            print("⚠️ No next page button found. Stopping...")
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
        try:
            self.driver.quit()
        except Exception:
            pass
        self.driver = None
