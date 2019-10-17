import json
import logging
import math
import re
import sys
from datetime import datetime

import scrapy
from scrapy.linkextractors import LinkExtractor

from trulia.items import TruItem

logger = logging.getLogger('scrapy')
logger.setLevel(logging.INFO)


class TruliaSpider(scrapy.Spider):
    name = 'truliaspider'
    allowed_domains = ["trulia.com"]

    def __init__(self, state='TX', city='Arlington', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = state
        self.city = city
        self.start_urls = [
            'http://trulia.com/{state}/{city}'.format(state=state, city=city)]
        self.le = LinkExtractor(allow=r'^https://www.trulia.com/p/')

    def last_pagenumber_in_search(self, response):
        """ Returns the number of the last page on the city/locale page """
        resultsHtml = response.xpath('.//*/text()[contains(., " Results")]')
        logger.info(resultsHtml[0].root[:-8][8:] + " results to scrape..")
        number_of_results = int(resultsHtml[0].root[:-8][8:].replace(',', ''))
        # return math.ceil(number_of_results/30)
        # this works but for now we dont wanna trip things so low
        # TODO: remove this, its just debug
        return 1

    def parse(self, response):
        last_page_number = self.last_pagenumber_in_search(response)
        page_urls = []
        for pageNumber in range(1, last_page_number + 1):
            page_urls.append(response.url + str(pageNumber) + '_p/')
        for page_url in page_urls:
            yield scrapy.Request(page_url, callback=self.parse_listing_results_page)

    def parse_listing_results_page(self, response):
        for link in self.le.extract_links(response):
            logger.debug(link.url)
            yield scrapy.Request(url=link.url, callback=self.parse_listing_contents)

    def parse_listing_contents(self, response):
        item = TruItem()
        # SCRAPE_DATE PHONE EMAIL CONTACT NAME CITY STATE ADDRESS TYPE ID
        # 3/27/2019 0:00:00 3473274001 if@available.ok Jane Doe Brooklyn NY 1122 Mill Ave #1 single_family_home 81083cfa-e683-41cd-ae3e-83fcfb352bc0

        # TODO: okay so we got xpath working and simplified stuff, so now all we gotta do
        # is to make sure the phone number is there and then add the rest of the data
        # then figure out how to integrate into scrapinghub
        item['scrape_time'] = datetime.now().strftime("%x %X")
        # TODO:this isnt working in code for some reason, look into it, shell works
        item['phone'] = response.xpath('//div[@data-testid="agent-phone"]/text()').get() 
        item['address'] = response.xpath('//span[@class="Text__TextBase-sc-1i9uasc-0 fxMXms"]/text()').get()
        item['url'] = response.url

        # if there is no phone number, discard the entry
        if item['phone'] is None:
            yield None
        else:
            yield item
