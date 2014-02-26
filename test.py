import lxml.etree as etree
import bs4
from bs4 import BeautifulSoup
import lxml.html.soupparser as soupparser
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import lxml

#class TitleTarget(object):
#    def __init__(self):
#        self.text = []
#    def start(self, tag, attrib):
#        self.is_title = True if tag == 'title' else False
#    def end(self, tag):
#        pass
#    def data(self, data):
#        if self.is_title:
#            self.text.append(data.encode('utf-8'))
#    def close(self):
#        return self.text

input = open("a")
#infile = 'a'
try:
	all_text = input.read()
	dom = soupparser.fromstring(all_text)
#	parser = etree.HTMLParser(target = TitleTarget())
#	results = etree.parse(all_text, parser)
#	print results
	
	#for child in dom.iter():
	#	print child.tag
	soup = BeautifulSoup(all_text)
	print soup.find('title').text
	#print dom.tostring.find('title')
#	title = dom[13]
#	print title.text
#	print dom.index(title)
#	print len(dom)
#	print dom[2].tag
finally:
	input.close()



#parser = etree.HTMLParser(target = TitleTarget())

# This and most other samples read in the Google copyright data
#infile = 'a'
#
#results = etree.parse(infile, parser)    
#print results[0].decode('utf-8')
#print lxml.html.tostring(results)
# When iterated over, 'results' will contain the output from 
# target parser's close() method

#out = open('titles.txt', 'w')
#out.write('\n'.join(results))
#out.close()










