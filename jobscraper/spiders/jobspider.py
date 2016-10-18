import scrapy
from scrapy import signals
from jobscraper.items import JobPosting
from datetime import date
import urlparse
import json

class JobSiteSpider(scrapy.Spider):
    name = "dummy"
    start_urls = []
    fieldNames = ['url', 'title', 'employer', 'description', 'location', 'salary', 'datePosted']
    
    def __init__(self, sitespec, maxDuplicates, *args, **kwargs) :
	super(JobSiteSpider, self).__init__(*args, **kwargs)	
	self.name = sitespec["name"]
	#self.maxPage = maxPage	
	#self.pageCount = 0
	#self.finished = False
	self.maxDuplicates = maxDuplicates
	self.sitespec = sitespec
	self.lastDateProcessed = date.today()
	self.dropRun = 0
	
	self.start_urls.append(sitespec["starturl"])

    def item_dropped(self) :
	self.dropRun = self.dropRun + 1

    def item_scraped(self) :
	self.dropRun = 0
	    
    def parse(self, response) :
	for itemSel in response.xpath(self.sitespec["xpath"]) :
	    item = JobPosting()
	    
	    for field in self.fieldNames :
	        if field in self.sitespec :
		    fieldFunc = getattr(self, self.sitespec[field][0]) 
		    fieldVal = fieldFunc(itemSel, self.sitespec[field][1])
		  
		    if fieldVal :
		        item[field] = fieldVal.strip()

	    item["website"] = self.name
	    if not item["url"].startswith("http://") :
		item["url"] =  response.urljoin(item["url"])
	    yield item
	    
	#self.pageCount = self.pageCount + 1
	
	if self.dropRun >= self.maxDuplicates :
	    return
	
	nextPage = response.xpath(self.sitespec['nextlink'])
		
	if nextPage and (date.today() - self.lastDateProcessed).days <= 28 :
	    url = response.urljoin(nextPage[0].extract())
	    yield scrapy.Request(url, self.parse)

    def xpath(self, selector, query) :
	value = selector.xpath(query)

	if value :
	    return value[0].extract() if value else None

    def json(self, selector, query) :
	print selector.extract()
	obj = json.loads(selector.extract())
	return eval(query)

'''
    def parseJSON(self, initem) :
	jsobj = josn.load(initem.xpath('./text()').extract())
	outitem = JobPosting()

	for field in self.fieldNames :
	    if field in self.sitespec :
		outitem[field] = self.jstostr(jsobj, self.sitespec[field])

    def jstostr(self, jsobj, spec) :
	slashIndex = spec.find("/")

	// Traverse dictionary i.e. "foo/bar" fetches jsobj["foo"]["bar"]
	if slashIndex == -1 :
	    obj = jsobj[spec]

	    if type(obj) == types.DictType :
	        values = []
		
		for key, val in obj.iter() :
		    if key.find('@') <> 0 :
			values.append(str(value).strip())
		return " ".join(values)
	    else :
		return str(obj).strip() 
	else :
	    return self.jstostr(jsobj[str[:i]], str[i+1:])
'''

	
			
		