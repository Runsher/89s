#coding:utf8
'''
Created on 2010-9-15
@author: chenggong
'''

import urllib2
import re
import socket
import lxml.html.soupparser as soupparser
import bs4
from bs4 import BeautifulSoup
import os
import lxml
import MySQL
#import BeautifulSoup


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

DEBUG = 0

'''
工具类
'''
class Tools():
    #log函数
    @staticmethod
    def writelog(level,info,notify=False):
        if DEBUG == 0:
            try:
                print "["+level+"]"+info.decode('UTF-8').encode('UTF-8')
            except:
                print "["+level+"]"+info.encode('UTF-8')
        else:
            print "["+level+"]"+info
        #if notify:
        #    print "[notify]报告管理员!!"

    #转unicode
    @staticmethod
    def toUnicode(s,charset):
        if( charset == "" ):
            return s
        else:
            try:
                u = unicode( s, charset )
            except:
                u = ""
        return u

    #正则抓取
    #@param single 是否只抓取一个
    @staticmethod
    def getFromPatten(patten,src,single=False):
        rst = "";
        p = re.compile(patten,re.S)
        all = p.findall(src)
        for matcher in all:
            rst += matcher + " "
            if( single ):
                break
        return rst.strip()

'''
网页内容爬虫
'''
class PageGripper():
    URL_OPEN_TIMEOUT = 10 #网页超时时间
    MAX_RETRY = 3 #最大重试次数

    def __init__(self):
        socket.setdefaulttimeout(self.URL_OPEN_TIMEOUT)

    #获取字符集
    def getCharset(self,s):
        rst = Tools.getFromPatten(u'charset=(.*?)"',s,True)
        if rst != "":
            if rst == "utf8":
                rst = "utf-8"
        return rst

    #尝试获取页面
    def downloadUrl(self,url):
        charset = ""
        page = ""
        retry = 0
        while True:
            try:
                fp = urllib2.urlopen(url)
                break
            except urllib2.HTTPError,e: #状态错误
                Tools.writelog('error','HTTP状态错误 code='+e.code)
                raise urllib2.HTTPError
            except urllib2.URLError,e: #网络错误超时
                Tools.writelog('warn','页面访问超时,重试..')
                retry+=1
                if( retry > self.MAX_RETRY ):
                    Tools.writelog('warn','超过最大重试次数,放弃')
                    raise urllib2.URLError

        while True:
            line = fp.readline()
            if charset == "":
                charset = self.getCharset(line)
		print  charset
            if not line:
                break
            page += Tools.toUnicode(line,charset)
        fp.close()
        return page

    #获取页面
    def getPageInfo(self,url):
        Tools.writelog( "info","开始抓取网页,url= "+url)
        info = ""
        try:
            info = self.downloadUrl(url)
        except:
            raise
        Tools.writelog("debug","网页抓取成功")
        return info

'''
内容提取类
'''
#import lxml.html

if __name__ == '__main__':
	list = [
		'http://www.36kr.com',
		'http://www.chinanews.com',
		]
	t = PageGripper()
	for url in list:
		page = t.getPageInfo(url)
		dom = soupparser.fromstring(page)
		soup = BeautifulSoup(page)
		title =  soup.find('title').text.decode('utf-8')
		sql = 'insert into test.spider(Title) values("%s")' % title
		print sql
		MySQL.MysqlQuery().query('sql')
