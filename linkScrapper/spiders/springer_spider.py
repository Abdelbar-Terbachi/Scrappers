import scrapy
from scrapy.http import HtmlResponse


class SpringerSpider(scrapy.Spider):
    name = "springer_spider"
    custom_settings = {
        "DOWNLOAD_DELAY": 1,  # Set the delay in seconds
        "ROBOTSTXT_OBEY": False,
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    start_urls = [
        "https://link.springer.com/search?new-search=true&query=smart+contract&sortBy=newestFirst&page=1"
    ]
    paper_links = []

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
            # Ensure that the next_page URL is absolute
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def closed(self, reason):
        # Print or store the links after the spider is closed
        print(self.paper_links)
