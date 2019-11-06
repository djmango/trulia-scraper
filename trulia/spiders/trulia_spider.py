import logging
import re
import sys
from datetime import datetime
from math import ceil

import scrapy
from requests import get
from scrapy.linkextractors import LinkExtractor

from trulia.items import TruItem

logger = logging.getLogger('scrapy')
logger.setLevel(logging.INFO)


class TruliaSpider(scrapy.Spider):
    name = 'truliaspider'
    allowed_domains = ["trulia.com"]

    def __init__(self, STATE='TX', CITY='Arlington', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.STATE = STATE
        self.CITY = CITY
        self.start_urls = [
            'http://trulia.com/{STATE}/{CITY}'.format(STATE=STATE, CITY=CITY)]
        self.le = LinkExtractor(allow=r'^https://www.trulia.com/p/')

    def last_pagenumber_in_search(self, response):
        """ Returns the number of the last page on the CITY/locale page """
        resultsHtml = response.xpath('.//*/text()[contains(., " Results")]')
        try:
            logger.info(resultsHtml[0].root[:-8][8:] + " results to scrape..")
            number_of_results = int(resultsHtml[0].root[:-8][8:].replace(',', ''))
            # return ceil(number_of_results/30)
            # this works but for now we dont wanna trip things so low
            # TODO: remove this, its just debug
            return 1
        except:
            return 0
  

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

        item['scrape_time'] = str(datetime.now().strftime("%x %X"))
        
        # get city
        r = re.compile('[^,]+')
        e = r.findall(str(response.xpath('//span[@class="HomeSummaryShared__CityStateAddress-vqaylf-0 fyHNRA Text__TextBase-sc-1i9uasc-0 dGyGqt"]/text()').get()))
        item['city'] = e[0]
        
        # get state
        r = re.compile('[A-Z]{2}')
        e = r.findall(str(response.xpath('//span[@class="HomeSummaryShared__CityStateAddress-vqaylf-0 fyHNRA Text__TextBase-sc-1i9uasc-0 dGyGqt"]/text()').get()))
        item['state'] = e[0]

        # get address
        item['address'] = str(response.xpath('//span[@class="Text__TextBase-sc-1i9uasc-0 fxMXms"]/text()').get())
        item['url'] = str(response.url)
        item['listing_id'] = item['url']

        get('https://script.google.com/macros/s/AKfycbxG7CgR4ecvr5ZF025Q945KJEr1HcEJAQJ6o-kvK_Rb1Zop3TRw/exec',
            params={'scrape_date': item['scrape_time'], 'address': item['address']})
        yield item
