# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TruItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    scrape_time = scrapy.Field()
    phone = scrapy.Field()
    email = scrapy.Field()
    name = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    address = scrapy.Field()
    house_type = scrapy.Field()
    listing_id = scrapy.Field()
    url = scrapy.Field()
