# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from scrapy.exceptions import DropItem
from urlparse import urlparse
import re
from datetime import datetime, date, timedelta		
from twisted.enterprise import adbapi
import MySQLdb as database
import logging
import settings
import string


class DatabasePipeline(object) :
    def __init__(self) :
	self.db = database.connect(host=settings.DB_HOST, 
				   user=settings.DB_USERNAME, 
				   passwd=settings.DB_PASSWORD, 
				   db=settings.DB_DATABASE,
				   use_unicode = True, charset = "utf8")

	try :
	    cursor = self.db.cursor()
	    cursor.execute("DELETE FROM listings WHERE" + 
			   " DATEDIFF(datePosted, SUBDATE(CURRENT_DATE, INTERVAL 60 DAY)) < 0")

	    self.db.commit()
	except database.DatabaseError as e:
	    self.db.rollback()
	    logging.error("Unable remove old entries: " + str(e))

	''' START COMMENT
	if not hasattr(DatabasePipeline, 'urls') :
	    DatabasePipeline.urls = []
	
	    query = self.dbpool.runQuery("SELECT url from listings")
	    query.addCallback(self.add_url)
	    query.addErrback(self.db_error)
	    
    def add_url(self, urls) :
	for url in urls :
	    self.urls.append(url[0])
	END_COMMENT ''' 
	    
    def process_item(self, item, spider) :
	site = item["website"]
	      
	values = []
	for key in item.keys() :
	    values.append("'" + item[key].replace("'", "\\'") + "'")
	    
	cmd = "INSERT INTO listings(%s) VALUES(%s)" % (string.join(item.keys(), ", "), string.join(values, ", "))		
	#logging.debug("Executing sql: " + cmd)
	try :
	    cursor = self.db.cursor()
	    
	    values = []
	    for key in item.keys() :
		values.append("'" + item[key].replace("'", "\\'") + "'")
	    
	    cmd = "INSERT INTO listings(%s) VALUES(%s)" % (string.join(item.keys(), ", "), string.join(values, ", "))		
	    #spider.logger.debug("Executing sql: " + cmd)
	    cursor.execute(cmd)	    
	    self.db.commit()
	except database.DatabaseError as e:
	    self.db.rollback()
	    spider.logger.error("Unable to insert into database: " + str(e))
	    raise DropItem("Unable to insert into database: " + str(e))

	spider.item_scraped()	     
	return item
	 
class DatePipeline(object) :
    def parseAbsDate(self, datestr) :
        datePatterns = [r"(?P<year>\d{4})[/.\s-](?P<month>\d\d?)[/.\s-](?P<day>\d\d?)",
	  	        r"(?P<day>\d\d?)[/.\s-](?P<month>\d\d?)(?:[/.\s-](?P<year>\d\d(?:\d\d)?))?"]
        months = [(r"Jan(uary)?", "1"), (r"Feb(uary)?", "2"), (r"Mar(ch)?", "3"), 
		  (r"Apr(il)?", "4"), (r"May", "5"), (r"June?", "6"), (r"July?", "7"), 
		  (r"Aug(ust)?", "8"), (r"Sept(ember)?", "9"), (r"Oct(ober)?", "10"), 
		  (r"Nov(ember)?", "11"), (r"Dec(ember)", "12")]
      
        for month in months :
	    datestr = re.sub(month[0], month[1], datestr)

	#logging.debug(datestr)

        for datePattern in datePatterns :
	    dateMatch = re.search(datePattern, datestr)
	  
	    if dateMatch <> None :
	        dateDict = dateMatch.groupdict()
	        #logging.debug(str(dateDict))
	        hasYear = "year" in dateDict and dateDict["year"]
	        retVal = date(int(dateDict["year"]) if hasYear else date.today().year, 
		  	      int(dateDict["month"]), int(dateDict["day"]))
		if (retVal.year < 100) :
		    retVal = retVal.replace(retVal.year + 2000)
		return retVal 
	  
	return None

    def parseRelDate(self, value) :
      	if re.search("(?i)today|minutes ago|just posted", value) != None :
	    return date.today()
	if re.search("(?i)yesterday", value) <> None :
	    return date.today() - timedelta(1)

	match = re.search("(?i) (\d?\d) hours? ago", value) 
	if match : 
	    time = datetime.now() - timedelta(hours=int(match.group(1)))
	    return date.fromordinal(time.toordinal())

	match = re.search("(?i)(\d) days? ago", value)	
	if match : 
	    return date.today() - timedelta(int(match.group(1)))
	match = re.search("(?i)([a\d]) weeks? ago", value)
	if match :
	    return date.today() - timedelta(int(match.group(1))*7)

	return None
	
    def process_item(self, item, spider) :	
	if not ("datePosted" in item) :
	    jobPostedDate = spider.lastDateProcessed
	else :
	    value = item["datePosted"]
	    reldate = self.parseRelDate(value)

	    if reldate <> None :
		jobPostedDate = reldate
	    else :
		absdate = self.parseAbsDate(value)
	      
		if absdate <> None :
		    jobPostedDate = absdate
		else :
		    jobPostedDate = spider.lastDateProcessed
		    spider.logger.warning("Unknown date: %s" % value)
		    
	    
	spider.lastDateProcessed = jobPostedDate
	item["datePosted"] = jobPostedDate.isoformat()
	
	return item
