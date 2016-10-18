# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobPosting(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    employer = scrapy.Field()
    description = scrapy.Field()
    location = scrapy.Field()
    salary = scrapy.Field()
    datePosted = scrapy.Field()
    website = scrapy.Field()