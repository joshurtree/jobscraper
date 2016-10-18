#!/usr/bin/python
#
# Main script required for running crawl

import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import scrapy.settings
import xml.sax
import xml.sax.handler
import logging
from jobscraper.spiders.jobspider import JobSiteSpider
import jobscraper.extensions
import argparse


class JobScraperFactory(xml.sax.handler.ContentHandler) :
    def __init__(self, process, site) :
	self.process = process
	self.site = site
	self.sitespec = None

    def startElement(self, name, attrs) :
	if (name == "jobsite" and (not self.site or self.site == attrs.getValue("name"))) :	    
 	    #sitekey = urlparse.urlparse(attrs.getValue("url")).netloc
	    self.sitespec = dict()

	    self.sitespec["xpath"] = attrs.getValue("xpath")
	    self.sitespec["name"] = attrs.getValue("name")
	    self.sitespec["starturl"] = attrs.getValue("url")
        elif (name == "field" and self.sitespec) :
	    for selType in ["xpath", "json", "css"] :
		if selType in attrs.getNames() :
	    	   self.sitespec[attrs.getValue("type")] = (selType, attrs.getValue(selType))
		   break
	elif (name == "nextlink" and self.sitespec) :
	    self.sitespec['nextlink'] = attrs.getValue("xpath")

    def endElement(self, name) :
	if (name == "jobsite" and self.sitespec) :
	    self.process.crawl(JobSiteSpider, sitespec = self.sitespec, maxDuplicates = args.maxduplicates)
	    self.sitespec = None


argparser = argparse.ArgumentParser()
argparser.add_argument("-e", "--email", help="E-mail summary of crawl", action="store_true") 
argparser.add_argument("-s", "--site", help="Website to crawl")
argparser.add_argument("-p", "--pages", type=int, help="Number of pages to retrieve from each site") 
argparser.add_argument("-d", "--maxduplicates", type=int, default=10, help="Number of consequtive duplicates before exiting spider")
args = argparser.parse_args()

settings = get_project_settings()
if args.pages :
    settings.set(scrapy.settings.CLOSESPIDER_PAGECOUNT, args.pages, 'cmdline') 

process = CrawlerProcess(settings)
xml.sax.parse("sitespec.xml", JobScraperFactory(process, args.site))
logger = logging.getLogger()
errorhandler = logging.FileHandler("errors.log", 'w')
errorhandler.setLevel(logging.ERROR)
logger.addHandler(errorhandler)
process.start()
jobscraper.extensions.process_stats(args.email)