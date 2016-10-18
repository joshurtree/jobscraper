 
from scrapy.exporters import XmlItemExporter
from jobscraper.items import JobPosting

class JobXmlExporter(XmlItemExporter):
    def serialize_field(self, field, name, value):
        if field == 'description':
            value = '<![CDATA[ %s ]]>' % str(value)
        return super(XmlItemExporter, self).serialize_field(field, name, value)