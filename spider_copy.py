#coding:utf8
'''
Created on 2010-9-15

@author: chenggong
'''

import urllib2
import re
import socket


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
                print "["+level+"]"+info.decode('UTF-8').encode('GBK') 
            except:
                print "["+level+"]"+info.encode('GBK') 
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
class InfoGripper():
    pageGripper = PageGripper()
    
    def __init__(self):
        Tools.writelog('debug',"爬虫启动")
  
    #抓取标题
    def griptitle(self,data):
        title = Tools.getFromPatten(u'box2t sp"><h3>(.*?)</h3>', data, True)
        if title == "":
            title = Tools.getFromPatten(u'<title>(.*?)[-<]',data,True)
        return title.strip()
    
    #抓取频道
    def gripchannel(self,data):
        zone = Tools.getFromPatten(u'频道：(.*?)</span>',data,True)
        channel = Tools.getFromPatten(u'<a.*?>(.*?)</a>',zone,True)
        return channel
    
    #抓取标签
    def griptag(self,data):
        zone = Tools.getFromPatten(u'标签：(.*?)</[^a].*>',data,True);
        rst = Tools.getFromPatten(u'>(.*?)</a>',zone,False);
        return rst
    
    #抓取观看次数
    def gripviews(self,data):
        rst = Tools.getFromPatten(u'已经有<em class="hot" id="viewcount">(.*?)</em>次观看',data);
        return rst
    
    #抓取发布时间
    def griptime(self,data):
        rst = Tools.getFromPatten(u'在<em>(.*?)</em>发布',data,True)
        return rst
    
    #抓取发布者
    def gripuser(self,data):
        rst = Tools.getFromPatten(u'title="点击进入(.*?)的用户空间"',data,True)
        return rst
    
    #获取页面字符集
    def getPageCharset(self,data):
        charset = Tools.getFromPatten(u'charset=(.*?)"',data,True)
        
        if( charset == "utf8" ):
            charset = "utf-8"
        return charset
    
    #获取CC相关数据
    def getCCData(self,data):
        
        zone = Tools.getFromPatten(u'SWFObject(.*?)</script>',data,True)
        
        #判断是否使用bokecc播放
        isFromBokeCC = re.match('.*bokecc.com.*', zone)
        if( not isFromBokeCC ):
            return "",""
            
        ccSiteId = Tools.getFromPatten(u'siteid=(.*?)[&,"]',zone,True)
        ccVid = Tools.getFromPatten(u'vid=(.*?)[&,"]',zone,True)
        return ccSiteId,ccVid
    
    #获取站内vid
    def gripVideoId(self,data):
        vid = Tools.getFromPatten(u'var vid = "(.*?)"',data,True)
        return vid
    
    #获取点击量
    def gripViewsAjax(self,vid,url,basedir):
        host = Tools.getFromPatten(u'http://(.*?)/',url,True)
        ajaxAddr = "http://" + host + basedir + "/index.php/ajax/video_statistic/" + vid
        '''
        try:
            content = self.pageGripper.getPageInfo(ajaxAddr)
        except Exception,e:
            print e
            Tools.writelog ("error", ajaxAddr+u"抓取失败")
            return "error"
        '''
        Tools.writelog('debug', u"开始获取点击量,url="+ajaxAddr)
        while True:
            try:
                fp = urllib2.urlopen(ajaxAddr)
                break
            except urllib2.HTTPError,e: #状态错误
                Tools.writelog('error','HTTP状态错误 code='+"%d"%e.code)
                return ""
            except urllib2.URLError,e: #网络错误超时
                Tools.writelog('warn','页面访问超时,重试..')
                retry+=1
                if( retry > self.MAX_RETRY ):
                    Tools.writelog('warn','超过最大重试次数,放弃')
                    return ""
        content = fp.read()
        fp.close()
        views = Tools.getFromPatten(u'"viewcount":(.*?),',content,True)
        views = views.replace('"','')
        return views
    
    #从网页内容中爬取点击量 
    def gripViewsFromData(self,data):
        views = Tools.getFromPatten(u'已经有<.*?>(.*?)<.*?>次观看',data,True)
        return views

    def gripBaseDir(self,data):
        dir = Tools.getFromPatten(u"base_dir = '(.*?)'",data,True)
        return dir

    #抓取数据
    def gripinfo(self,url): 
        
        try:
            data = self.pageGripper.getPageInfo(url)
        except:
            Tools.writelog ("error", url+" 抓取失败")
            raise
        
        Tools.writelog('info','开始内容匹配')
        rst = {}
        rst['title'] = self.griptitle(data)
        rst['channel'] = self.gripchannel(data)
        rst['tag'] = self.griptag(data)
        rst['release'] = self.griptime(data)
        rst['user'] = self.gripuser(data)
        ccdata = self.getCCData(data)
        rst['ccsiteId'] = ccdata[0]
        rst['ccVid'] = ccdata[1]
        views = self.gripViewsFromData(data)
        if views =="" or not views:
            vid = self.gripVideoId(data)
            basedir = self.gripBaseDir(data)
            views = self.gripViewsAjax(vid,url,basedir)
            if( views == "" ):
                views = "error"
            if( views == "error"):
                Tools.writelog("error","获取观看次数失败")
        Tools.writelog("debug","点击量:"+views)
        rst['views'] = views
        Tools.writelog('debug','title=%s,channel=%s,tag=%s'%(rst['title'],rst['channel'],rst['tag']))
        return rst

'''
单元测试
'''
if __name__ == '__main__':
    list = [
            'http://008yx.com/xbsp/index.php/video/index/3138',
            'http://vblog.xwhb.com/index.php/video/index/4067',
            'http://demo.ccvms.bokecc.com/index.php/video/index/3968',
            'http://vlog.cnhubei.com/wuhan/20100912_56145.html',
            'http://vlog.cnhubei.com/html/js/30271.html',
            'http://www.ddvtv.com/index.php/video/index/15',
            'http://boke.2500sz.com/index.php/video/index/60605',
            'http://video.zgkqw.com/index.php/video/index/334',
            'http://yule.hitmv.com/html/joke/27041.html',
            'http://www.ddvtv.com/index.php/video/index/11',
            'http://www.zgnyyy.com/index.php/video/index/700',
            'http://www.kdianshi.com/index.php/video/index/5330',
            'http://www.aoyatv.com/index.php/video/index/127',
            'http://v.ourracing.com/html/channel2/64.html',
            'http://v.zheye.net/index.php/video/index/93',
            'http://vblog.thmz.com/index.php/video/index/7616',
            'http://kdianshi.com/index.php/video/index/5330',
            'http://tv.seeyoueveryday.com/index.php/video/index/95146',
            'http://sp.zgyangzhi.com/html/ji/2.html',
            'http://www.xjapan.cc/index.php/video/index/146',
            'http://www.jojy.cn/vod/index.php/video/index/399',
            'http://v.cyzone.cn/index.php/video/index/99',
            ]
    
    list1 = ['http://192.168.25.7:8079/vinfoant/versionasdfdf']

    infoGripper = InfoGripper()
    for url in list:
        infoGripper.gripinfo(url)
    del infoGripper
