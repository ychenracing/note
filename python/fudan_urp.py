#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib


cookie_file = cookielib.MozillaCookieJar("/Users/racing/fudancookie")
handler = urllib2.HTTPCookieProcessor(cookie_file)
opener = urllib2.build_opener(handler)
page_header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36", "Referer": "http://www.portal.fudan.edu.cn/main/loginIndex.do?ltype=1"}

login_url = "http://www.portal.fudan.edu.cn/main/login.do?invitationCode="  # 登录的url
index_url = "http://www.portal.fudan.edu.cn/ehome/index.do"  # 登录之后要访问的url
post_data = urllib.urlencode({"email":"xxxxxxxxxxx", "password":"xxxxxxxxxxx"})
request = urllib2.Request(login_url, post_data, page_header)

if __name__ == '__main__':
    try:
        response = opener.open(request)
        cookie_file.save(ignore_discard=True, ignore_expires=True)
        # cookie保存到文件之后，可以使用下面这句从文件中读取cookie内容到变量
        #cookie.load("/Users/racing/fudancookie", ignore_discard=True, ignore_expires=True)
    except urllib2.HTTPError, e:
        print e.code
    except urllib2.URLError, e:
        print e.reason
    else:
        print "Login successfully!"

    request = urllib2.Request(index_url, headers=page_header)
    response = opener.open(request)
    print response.read()
