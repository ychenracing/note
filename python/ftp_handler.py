# -*- coding:utf-8 -*-
import urllib2

handler = urllib2.FTPHandler()
request = urllib2.Request(url='ftp://yongchen13:yongchen13@10.20.2.166')
opener = urllib2.build_opener(handler)
f = opener.open(request)
print f.read()
