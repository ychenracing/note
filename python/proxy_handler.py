#! -*- encoding:utf-8 -*-
import urllib2

handler = urllib2.ProxyHandler(proxies = {'http' : 'http://202.120.224.xx:xxxx/'})
opener = urllib2.build_opener(handler)
f = opener.open('http://www.baidu.com/')
print f.read()
