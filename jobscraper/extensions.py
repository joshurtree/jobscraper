from scrapy import signals
from scrapy.statscollectors import MemoryStatsCollector
import settings
import logging
import smtplib

stats = {}

class StatsLogger :
    @classmethod
    def from_crawler(cls, crawler) :
    	ext = cls()
    	
    	crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
    	crawler.signals.connect(ext.item_dropped, signal=signals.item_dropped)
    	crawler.signals.connect(ext.spider_error, signal=signals.spider_error)
	crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
	#crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
    	#crawler.signals.connect(ext.engine_stopped, signal=signals.engine_stopped)
	ext.crawler = crawler

    	return ext 
    	
    def spider_opened(self, spider) :
    	stats[spider.name] = MemoryStatsCollector(self.crawler)
		
    def item_scraped(self, item, spider) :
    	stats[spider.name].inc_value('jobs added')
    	
    def item_dropped(self, item, spider) :
    	stats[spider.name].inc_value('duplicate jobs')
    	
    def spider_error(self, failure, response, spider) :
    	if (stats[spider.name].get_value('errors') == None) :
    	    stats[spider.name].set_value('first error', failure.getTraceback())
    	stats[spider.name].inc_value('errors')
    	
def process_stats(mail = False) :
    message = ""
    for name in stats :
	message += "==" + name + "==\n"
	message += "New jobs found: " + str(stats[name].get_value("jobs added", 0)) + "\n"
	message += "Duplicate jobs: " + str(stats[name].get_value("duplicate jobs", 0)) + "\n"
	message += "Errors: " + str(stats[name].get_value("errors", 0)) + "\n"
	
	error = stats[name].get_value("first error")
	if (error) :
	    message += "First error: " + error + "\n"
	
	message += "\n"

    if mail :
        mailer = smtplib.SMTP('localhost')
        header = "From: " + settings.MAIL_FROM + "\n"
        header += "To: " + settings.MAIL_TO + "\n"
        header += "Subject: Job scraper stats\n\n" 
     
        logging.debug("Sending message\n" + header + message)	    	    
        mailer.sendmail(settings.MAIL_FROM, settings.MAIL_TO, header + message)
    else :
	logging.debug("Summary\n" + message)