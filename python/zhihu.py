#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
from bs4 import BeautifulSoup


index_page_url = "https://www.zhihu.com"
login_url = "https://www.zhihu.com/login/email"

cookie = cookielib.MozillaCookieJar()
cookie_handler = urllib2.HTTPCookieProcessor(cookie)
zhihu_opener = urllib2.build_opener(cookie_handler)

page_headers = {
    "host": "www.zhihu.com",
    "origin": "https://www.zhihu.com",
    "referer": "https://www.zhihu.com",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
}

xsrf_req = urllib2.Request(index_page_url, headers=page_headers)
xsrf_res = urllib2.urlopen(xsrf_req)
xsrf_html = xsrf_res.read()
soup = BeautifulSoup(xsrf_html, "lxml")
xsrf = soup.find("input", {"name": "_xsrf", "type": "hidden"}).get("value")


if __name__ == '__main__':
    try:

        # 可以请求http://www.zhihu.com/captcha.gif获取验证码
        post_data = urllib.urlencode({
            "_xsrf": xsrf,
            "password": "xxxxxxxxxx",
            "remember_me": "true",
            "email": "ychenracing@gmail.com"
        })
        request = urllib2.Request(login_url, post_data, page_headers)
        response = zhihu_opener.open(request)
    except urllib2.URLError, e:
        if hasattr(e, "code"):
            print e.code
        if hasattr(e, "reason"):
            print e.reason
    else:
        print "Login zhihu successfully!"

    index_request = urllib2.Request(index_page_url, headers=page_headers)
    index_response = zhihu_opener.open(index_request)
    print index_response.read()
