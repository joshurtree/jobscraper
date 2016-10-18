import unittest
from datetime import datetime, date, timedelta
import jobscraper.pipelines
import logging

class DatePipelineTest(unittest.TestCase) :
    def __init__(self, methodName = "runTest") :
	super(DatePipelineTest, self).__init__(methodName)
	self.addTypeEqualityFunc(date, self.assertDateEqual)
	
    def setUp(self) :
	logging.basicConfig(level=logging.DEBUG)
	self.testClass = jobscraper.pipelines.DatePipeline()

    def test_parseRelDate(self) :
	now = datetime.now()
	today = date.today()

	self.assertDateEqual(self.testClass.parseRelDate("posted today by"), today)
	self.assertDateEqual(self.testClass.parseRelDate("posted yesterday by"), today - timedelta(1))
	self.assertDateEqual(self.testClass.parseRelDate("posted 14 hours ago by"), date.fromordinal((now - timedelta(hours=14)).toordinal()))
	self.assertDateEqual(self.testClass.parseRelDate("posted 1 week ago by"), today - timedelta(7))
	self.assertDateEqual(self.testClass.parseRelDate("posted 5 days ago by"), today - timedelta(5))

	self.assertEqual(self.testClass.parseRelDate("posted 1 August by"), None)
	
    def test_parseAbsDate(self) :
	testdate1 = date(date.today().year, 8, 1)
	testdate2 = date(2016, 8, 1)
	
	self.assertDateEqual(self.testClass.parseAbsDate("posted 1 August by"), testdate1)
	self.assertDateEqual(self.testClass.parseAbsDate("posted 1/8 by"), testdate1)
	
	self.assertDateEqual(self.testClass.parseAbsDate("posted 1/8/16 by"), testdate2)
	self.assertDateEqual(self.testClass.parseAbsDate("posted 1 August 2016 by"), testdate2)
	self.assertDateEqual(self.testClass.parseAbsDate("posted 1-8-2016 by"), testdate2)

    def assertDateEqual(self, date1, date2, msg=None) :
	if date1 <> date2 :
	    if type(date1) <> date :
		raise self.failureException("Not a date")
	    else :
		raise self.failureException("Date is %d days out" % (date1 - date2).days)
	
	return True