import scrapy
from scrapy.http import HtmlResponse
import csv


class SpringerSpider(scrapy.Spider):
    name = "springer_spider"
    start_urls = [
        "https://link.springer.com/search?new-search=true&query=smart+contract&sortBy=newestFirst&page=1"
    ]
    paper_links = []

    custom_settings = {
        "DEPTH_LIMIT": 40000,
        "FEEDS": {
            "scrapped_links.csv": {  # Change the output filename to "scrapped_links.csv"
                "format": "csv",
                "overwrite": True,
                "store_empty": False,
                "fields": ["paper_link"],
            },
        },
    }

    def parse(self, response: HtmlResponse):
        # Extract paper links
        current_page_links = response.css(
            "h3.c-card-open__heading a::attr(href)"
        ).extract()
        self.paper_links.extend(current_page_links)

        # Follow pagination link if available
        next_page = response.css(
            'li.eds-c-pagination__item a[rel="next"]::attr(href)'
        ).extract_first()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)

    def closed(self, reason):
        # Store the links in a CSV file
        with open(
            "scrapped_links_2.csv", "w", newline=""
        ) as csvfile:  # Change the filename here too
            fieldnames = ["paper_link"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for link in self.paper_links:
                writer.writerow({"paper_link": link})
        print(f"The links have been stored in scrapped_links.csv file.")
