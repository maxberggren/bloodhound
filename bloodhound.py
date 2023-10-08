"""Bloodhound scrapes websites for newly published articles and asks an LLM for their breaking news score"""
import re
import time
import scrapy
import scrapydo

from urllib.parse import urljoin
from scrapy import Request, signals
from scrapy.signalmanager import dispatcher
from config import BLACKLIST_PATTERN, CUSTOM_SETTINGS, HEADERS, TOKEN_COUNT_THRESHOLD
from utils import DomainLimitedDeque, ask_ai, count_tokens_normalized, get_domain, console

scrapydo.setup()

PROMPT = """
Rank the following headline with a breaking news score 1-10. Score according to how breaking the news are.

Return a JSON:
{"summary": "English summary of the notification on the form of a smashing headline", "score": 1}

ALWAYS answer in English only! Do not put timestamps in the summary! Do not put the article author in the summary!

Headline: 
"""

URLS_TO_MONITOR = [
    "https://www.nyt.com"
]

already_seen_urls = DomainLimitedDeque()

class Bloodhound(scrapy.Spider):
    name = 'HeadlineScraper'
    start_urls = URLS_TO_MONITOR
    custom_settings = CUSTOM_SETTINGS
    blacklist_pattern = BLACKLIST_PATTERN

    def __init__(self, *args, **kwargs):
        super(Bloodhound, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def start_requests(self):
        requests = []
        for item in self.start_urls:
            requests.append(Request(url=item, headers=HEADERS))
        return requests    

    def should_skip_based_on_url_length(self, url, domain):
        return len(url) - len(domain) - len("http://")  < 6

    def should_skip_based_on_token_count(self, text):
        return count_tokens_normalized(text) < TOKEN_COUNT_THRESHOLD

    def should_skip_based_on_blacklist(self, url):
        return any(re.search(pattern, url) for pattern in self.blacklist_pattern)

    def parse(self, response):
        """Find all links/headlines and their text"""
        new_articles_found = 0
        articles_found = 0
        domain = get_domain(response.url)
        links = response.xpath("//a")

        for link in links:

            text = link.xpath('.//text()').extract()
            text = ' '.join([t.strip() for t in text if t.strip()])
            url = urljoin(response.url, link.xpath('@href').extract_first())

            if any([
                self.should_skip_based_on_url_length(url, domain),
                self.should_skip_based_on_token_count(text),
                self.should_skip_based_on_blacklist(url)
            ]):
                continue
            
            if domain in url:
                articles_found += 1
                if url not in already_seen_urls:
                    if already_seen_urls.append(url):  # append returns True if no burst detected
                        if headline := ask_ai(text, url, domain, PROMPT):
                            console.log(headline)
                            if headline["score"] >= 9:
                                console.log(f"[bold red]{headline}")
                            else:
                                console.log(headline)
                            new_articles_found += 1

        if new_articles_found:
            console.log(f"[purple]Found: {new_articles_found} new articles on {domain}")
        else:
            console.log(f"[blue]Found: No new articles found on {domain}")

    def spider_closed(self, spider):
        pass


if __name__ == "__main__":
    while True:
        scrapydo.run_spider(Bloodhound)
        time.sleep(5)