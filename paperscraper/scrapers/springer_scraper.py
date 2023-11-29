from paperscraper.scrapers.base.base_scraper import BaseScraper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup


class Springer(BaseScraper):
    def __init__(self, driver):
        self.driver = driver
        self.website = ["link.springer.com"]

    def handle_cookie_consent(self):
        try:
            # Wait for the cookie banner to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cc-banner__content"))
            )

            # Accept all cookies by clicking the "Accept all cookies" button
            accept_button = self.driver.find_element(
                By.CLASS_NAME, "cc-banner__button-accept"
            )
            accept_button.click()

        except Exception as e:
            print(f"Error handling cookie consent: {e}")

    def get_authors(self, soup):
        authors_list = soup.findAll("meta", {"name": "citation_author"})

        # Check if any authors are found
        if authors_list:
            return [author.get("content") for author in authors_list]
        else:
            return None  # or an empty list, depending on your preference

    def get_abstract(self, soup):
        # Check for the cookie consent banner and handle it
        self.handle_cookie_consent()

        # Find the abstract section
        abstract_section = soup.find(
            "div", {"class": "c-article-section", "id": "Abs1-section"}
        )
        if abstract_section:
            abstract_content = abstract_section.find(
                "div", {"class": "c-article-section__content"}
            )
            if abstract_content:
                return abstract_content.find("p").get_text()

    def get_body(self, soup):
        # Check for the cookie consent banner and handle it
        self.handle_cookie_consent()

        # Find the body div
        body_div = soup.find("div", id="body")

        # Check if the body div is found
        if body_div:
            sections = OrderedDict()
            sections_markup = body_div.findAll("section", {"class": "Section1"})
            for section_markup in sections_markup:
                paragraphs = section_markup.div.findAll("p", {"class": "Para"})
                sections[section_markup.h2.getText()] = [
                    paragraph.getText() for paragraph in paragraphs
                ]
            return sections

        # Return None if body div is not founde
        return None

    def get_doi(self, soup):
        meta_tag = soup.find("meta", {"name": "citation_doi"})
        return meta_tag["content"] if meta_tag else None

    def get_keywords(self, soup):
        self.handle_cookie_consent()

        keywords_section = soup.find(
            "div", {"class": "c-article-section", "id": "Abs1-section"}
        )
        if keywords_section:
            keywords_list = keywords_section.find(
                "ul", {"class": "c-article-subject-list"}
            )
            if keywords_list:
                return [
                    li.get_text()
                    for li in keywords_list.find_all(
                        "li", {"class": "c-article-subject-list__subject"}
                    )
                ]

    def get_pdf_url(self, soup):
        meta_tag = soup.find("meta", {"name": "citation_pdf_url"})

        # Check if the meta tag is found
        if meta_tag:
            return meta_tag.get("content")
        else:
            return None

    def get_title(self, soup):
        meta_tag = soup.find("meta", {"name": "citation_title"})

        # Check if the meta tag is found
        if meta_tag:
            return meta_tag.get("content")
        else:
            return None

    def get_editors_and_affiliations(self, soup):
        # Find the editors and affiliations section
        editors_section = soup.find(
            "div",
            {"class": "c-article-section__content", "id": "editor-information-content"},
        )
        if editors_section:
            editors_list = editors_section.find(
                "ol", {"class": "c-article-author-affiliation__list"}
            )
            if editors_list:
                editors = []
                for editor_li in editors_list.find_all("li"):
                    editor_name = editor_li.find(
                        "p", {"class": "c-article-author-affiliation__authors-list"}
                    )
                    editor_affiliation = editor_li.find(
                        "p", {"class": "c-article-author-affiliation__address"}
                    )
                    if editor_name and editor_affiliation:
                        editors.append(
                            {
                                "name": editor_name.get_text(strip=True),
                                "affiliation": editor_affiliation.get_text(strip=True),
                            }
                        )
                return editors
