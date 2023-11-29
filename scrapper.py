from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from paperscraper.scrapers.springer_scraper import Springer
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
import csv
import sys


# Function to handle cookie consent
def handle_cookie_consent(driver):
    try:
        # Check if the cookie consent has already been handled
        if not driver.get_cookie("cookie_consent_accepted"):
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cc-banner__content"))
            )

            accept_button = driver.find_element(
                By.CLASS_NAME, "cc-banner__button-accept"
            )
            accept_button.click()

            # Set a cookie to indicate that the consent has been handled
            driver.add_cookie({"name": "cookie_consent_accepted", "value": "true"})

    except NoSuchElementException:
        print("Cookie consent banner not found or already accepted.")
    except Exception as e:
        print(f"Error handling cookie consent: {e}")


# Function to perform scraping and store data in MongoDB
def scrape_and_store(link, scraper, db_collection):
    chrome_driver.get(link)
    soup = BeautifulSoup(chrome_driver.page_source, "html.parser")

    authors = scraper.get_authors(soup)
    abstract = scraper.get_abstract(soup)
    body = scraper.get_body(soup)
    doi = scraper.get_doi(soup)
    keywords = scraper.get_keywords(soup)
    pdf_url = scraper.get_pdf_url(soup)
    title = scraper.get_title(soup)
    editors_and_affiliations = scraper.get_editors_and_affiliations(soup)

    result_dict = {
        "Authors": authors,
        "Abstract": abstract,
        "Body": body,
        "DOI": doi,
        "Keywords": keywords,
        "PDF URL": pdf_url,
        "Title": title,
        "Editors and Affiliations": editors_and_affiliations,
    }

    # Store data in MongoDB
    db_collection.insert_one(result_dict)

    # Print the results
    for section_name, section_value in result_dict.items():
        print(f"{section_name}: {section_value}")


if __name__ == "__main__":
    # Initialize MongoDB client and database
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["papers"]
        collection = db["SpringerPapers"]
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        sys.exit(1)

    # Initialize WebDriver for Chrome
    chrome_driver_path = (
        "/Users/aminaterbachi/Desktop/chromedriver_mac_arm64/chromedriver"
    )
    chrome_options = webdriver.ChromeOptions()

    # Use Service to provide the path to the ChromeDriver executable
    chrome_service = Service(executable_path=chrome_driver_path)
    chrome_driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    # Handle cookie consent only if not handled before
    handle_cookie_consent(chrome_driver)

    # Instantiate the Springer scraper
    springer_scraper = Springer(chrome_driver)

    # Read links from CSV
    import csv

with open("scrapped_links2.csv", "r") as csvfile:
    links_reader = csv.reader(csvfile)
    condition_met_count = 0
    start_scraping = False

    for link in links_reader:
        # Check if the start link is reached
        if link[0] == "/article/10.1007/s11042-023-17104-z":
            start_scraping = True
            continue  # Skip this link, don't process it

        # Check the conditions for skipping links
        if not start_scraping or any(
            keyword in link[0] for keyword in ["book", "nature", "pdf"]
        ):
            continue

        condition_met_count += 1

        # Concatenate link with "https://link.springer.com/"
        full_link = "https://link.springer.com" + link[0]

        print(f"Attempting to access: {full_link}")

        # Scrap and store data for each link
        scrape_and_store(full_link, springer_scraper, collection)

    # Close WebDriver
    chrome_driver.quit()
