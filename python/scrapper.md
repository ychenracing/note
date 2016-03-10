## urllib ##
### urllib.urlopen(url[, data[, proxies]]) ###
作用：打开一个 url，返回一个类文件对象，然后可以进行类似文件对象的操作。

参数url是一个字符串，需要包含使用的协议，如http、ftp等；参数data如果不为空则表示以post方式提交到url的数据；参数proxies用于设置代理。

返回的类文件对象提供了如下方法：

- read()，readline()，readlines()，fileno()，close() ：这些方法的使用方式与文件对象完全一样；
- info()：返回一个httplib.HTTPMessage 对象，表示远程服务器返回的头信息；
- getcode()：返回Http状态码。如果是http请求，200表示请求成功完成；404表示网址未找到；
- geturl()：返回请求的url；

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib

google = urllib.urlopen("http://www.google.com.hk")
print "http header:", google.info()
print "http status:", google.getcode()
print "url:", google.geturl()
for line in google:
    print line,
google.close()
```

### urllib.urlretrieve(url[, filename[, reporthook[, data]]]) ###
作用：直接将远程数据下载到本地。参数filename指定了保存到本地的路径（如果未指定该参数，urllib会生成一个临时文件来保存数据）；参数reporthook是一个回调函数，当连接上服务器、以及相应的数据块传输完毕的时候会触发该回调。我们可以利用这个回调函数来显示当前的下载进度。参数data指post到服务器的数据。

该方法返回一个包含两个元素的元组(filename, headers)，filename表示保存到本地的路径，header表示服务器的响应头。

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import urllib
''' download file from url into local file.'''

path = os.path.normpath(os.getcwd())


def cbk(a, b, c):
    '''回调函数
    @a: 已经下载的数据块
    @b: 数据块的大小
    @c: 远程文件的大小
    '''
    per = 100.0 * a * b / c
    if per > 100:
        per = 100
    print '\r%.2f%%' % per,  # 格式化输出时，如果要输出百分号，需要两个百分号


def download_file(url, dest_file_path):
    if not os.path.exists(dest_file_path):
        try:
            urllib.urlretrieve(url, dest_file_path, cbk)
            os.system('gunzip ' + os.path.basename(dest_file_path))
        except Exception, ex:
            print '\tError retrieving the URL:', url
            print ex
    else:
        print os.path.basename(dest_file_path), 'already exists!'

if __name__ == '__main__':
    for num in xrange(22):
        num += 1
        link = 'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/chromosomes/chr' + str(num) + '.fa.gz'
        file_name = os.path.basename(line)
        dest_file_path = os.path.join(path, file_name)
        print 'downloading', file_name
        download_file(link, dest_file_path)
        print ''
```

### urllib.urlencode(query) ###
作用：将URL中的键值对以连接符&划分。这里可以与urlopen结合以实现post方法和get方法。

```python
import urllib

params = urllib.urlencode({'spam':1, 'eggs':2, 'bacon':0})  #params='eggs=2&bacon=0&spam=1'
f = urllib.urlopen("http://python.org/query?%s" % params)
print f.read()
```

```python
import urllib

parmas = urllib.urlencode({'spam':1, 'eggs':2, 'bacon':0})
f = urllib.urlopen("http://python.org/query", parmas)
print f.read()
```

### urllib其他方法 ###

- urllib.quote(string[, safe])：对字符串进行编码。参数safe指定了不需要编码的字符；
- urllib.unquote(string) ：对字符串进行解码；
- urllib.quote_plus(string[, safe]) ：与urllib.quote类似，但这个方法用'+'来替换空格，而quote用'%20'来代替空格；
- urllib.unquote_plus(string)：对字符串进行解码；
- urllib.urlencode(query[, doseq])：将dict或者包含两个元素的元组列表转换成url参数。例如 字典{'name': 'dark-bull', 'age': 200}将被转换为"name=dark-bull&age=200"；
- urllib.pathname2url(path)：将本地路径转换成url路径；
- urllib.url2pathname(path)：将url路径转换成本地路径。


```python
import urllib

data = "name = ~a+3"
 
data1 = urllib.quote(data)
print data1 # result: name%20%3D%20%7Ea%2B3
print urllib.unquote(data1) # result: name = ~a+3
 
data2 = urllib.quote_plus(data)
print data2 # result: name+%3D+%7Ea%2B3
print urllib.unquote_plus(data2)    # result: name = ~a+3
 
data3 = urllib.urlencode({ "name": "dark-bull", "age": 200 })
print data3 # result: age=200&amp;name=dark-bull
 
data4 = urllib.pathname2url(r"d:/a/b/c/23.php")
print data4 # result: d%3A/a/b/c/23.php
print urllib.url2pathname(data4)    # result: d:/a/b/c/23.php
```


## urllib2 ##
- urllib2可以接受一个Request类的实例来设置URL请求的headers，urllib仅可以接受URL。这意味着，你使用urllib不可以伪装你的User Agent字符串等。
- urllib提供urlencode方法用来产生查询字符串，而urllib2没有。这是为何urllib常和urllib2一起使用的原因。


### urllib2.urlopen(url[, data[, timeout[, cafile[, capath[, cadefault[, context]]]]]) ###
### urllib2.Request(url[, data][, headers][, origin\_req\_host][, unverifiable]) ###
urllib2.urlopen()方法参数可以用一个request的对象来代替URL，而且增加了一个URLError异常，对于HTTP协议的错误，增加了一个HTTPError的异常，其中这个HTTPError自动变成一个合法的response来返回。

```python
import urllib2  
  
url = "http://www.baidu.com/go"
try:
    response = urllib2.urlopen(url)
    print response.info()  # 输出响应HTTP header，此处上一句抛出HTTPError
    print response.read()  # 输出响应HTTP正文
except urllib2.HTTPError, e:
    print e.getcode()  # 404
    print e.reason  # Not Found
    print e.geturl()  # http://www.baidu.com/go
    print e.info()
    print e.read()
```

HTTP报文结构为

![HTTP报文](img/httpmessage.jpg)

```python
#!/usr/bin/env python
import urllib2

request = urllib2.Request(sys.argv[1])
response = urllib2.urlopen(request)
print "Retrieved", response.geturl()

info = response.info()
for key, value in info.items():
    print "%s = %s" % (key, value)

html = response.read()
print html
```

还可以使用request对象作为参数，不过首先我们得先创建一个request的对象，通过urllib2.Request类来完成，urllib2.Request类有很多不同的方法，比较常用的是add_header(self,key,val)方法，这个方法可以添加我们自己的HTTP header。

```python
import urllib2

request = urllib2.Request("http://www.qiushibaike.com/text/page/1")
request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36')
# user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36"
# page_header = {"User-Agent": user_agent}
# request = urllib2.Request("http://www.qiushibaike.com/text/page/1", headers=page_header)
try:
    response = urllib2.urlopen(request)
except urllib2.HTTPError, e:  # HTTPError是URLError的子类
    print e.code
except urllib2.URLError, e:  # 无网络连接或服务器不存在时会出现URLError
    print e.reason
else:
    print "OK"    

headers = response.info()
data = response.read()
```

其中，Request有几个常用的方法：

- request.add_data(data)：向请求添加数据。如果请求是HTTP请求，则方法改为“POST”。data是向指定url提交的数据，要注意该方法不会将data追加到之前已经设置的任何数据上，而是使用现在的data**替换**之前的。
- request.add_header(key, val)：往请求中添加header信息，key是报头名，val是报头值，如`{'User-Agent': 'xxx'}`，两个参数都是字符串。


### ProxyHandler ###
使用urllib2.ProxyHandler，使得通过代理访问url或者Request。

```python 
# -*- coding:utf-8 -*-
import urllib2

handler = urllib2.ProxyHandler(proxies = {'http' : 'http://202.120.224.90:8080/'})
opener = urllib2.build_opener(handler)
f = opener.open('http://www.baidu.com/')
print f.read()
```


### FTPHandler ###
使用urllib2.FTPHandler来访问ftp站点。

```python
# -*- coding:utf-8 -*-
import urllib2

handler = urllib2.FTPHandler()
request = urllib2.Request(url='ftp://ychen:ychen@10.20.2.166')  # ftp://用户名:密码@ftp地址
opener = urllib2.build_opener(handler)
f = opener.open(request)
print f.read()
```


## Cookie ##
### urllib2.opener ###
当使用urllib2.urlopen()时打开的类文件对象是opener(一个urllib2.OpenerDirector的实例)。一般使用的是默认的opener，即urlopen。它是一个特殊的opener，可以理解成opener的一个特殊实例，传入的参数仅仅是url，data。

如果用到Cookie，需要创建更一般的opener来实现对Cookie的设置。

### cookielib.CookieJar ###
可以利用本模块的CookieJar类的对象来捕获cookie并在后续连接请求时重新发送，比如可以实现模拟登录功能。该模块主要的对象有CookieJar、FileCookieJar、MozillaCookieJar、LWPCookieJar。

其中，CookieJar派生了FileCookieJar，FileCookieJar派生了MozillaCookieJar和LWPCookieJar。

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib


cookie_file = cookielib.MozillaCookieJar("/Users/racing/fudancookie")
handler = urllib2.HTTPCookieProcessor(cookie_file)
opener = urllib2.build_opener(handler)
page_header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36", 
                  "Referer": "http://www.portal.fudan.edu.cn/main/loginIndex.do?ltype=1"}

login_url = "http://www.portal.fudan.edu.cn/main/login.do?invitationCode="  # 登录的url
index_url = "http://www.portal.fudan.edu.cn/ehome/index.do"  # 登录之后要访问的url
post_data = urllib.urlencode({"email":"xxxxxxxxxxx", "password":"xxxxxxxxxxx"})
request = urllib2.Request(login_url, post_data, page_header)

if __name__ == '__main__':
    try:
        response = opener.open(request)
        cookie_file.save(ignore_discard=True, ignore_expires=True)
        # cookie保存到文件之后，可以使用下面这句从文件中读取cookie内容到变量
        # cookie.load("/Users/racing/fudancookie", ignore_discard=True, ignore_expires=True)
        # 安装opener，此后调用urllib2.urlopen()时都会使用安装过的opener对象
        # urllib2.install_opener(opener)
    except urllib2.HTTPError, e:
        print e.code
    except urllib2.URLError, e:
        print e.reason
    else:
        print "Login successfully!"

    request = urllib2.Request(index_url, headers=page_header)
    response = opener.open(request)
    print response.read()
```
### Cookie使用步骤 ###
1. 首先使用cookielib创建CookieJar。如`cookie=cookielib.MozillaCookieJar("cookie_file.txt")`
2. 根据cookie创建cookie handler。如`handler=urllib2.HTTPCookieProcessor(cookie)`
3. 根据handler创建opener。如`opener=urllib2.build_opener(handler)`
4. 有了opener之后就可以像urllib2.urlopen()一样打开url或者urllib2.Request了。如`response=opener.open(request)`


## BeautifulSoup ##
### bs.find_all(name, attrs, recursive, text, \*\*kwargs) ###
搜索当前tag的所有子tag节点，并判断是否符合过滤器的条件。以列表形式返回结果。


#### name参数 ####
1. 传入字符串，如`bs.find_all('a')`，查找所有的\<a\>标签。
2. 传入正则表达式，如`bs.find_all(re.compile('^b'))`，查找标签名以b开头的标签，如\<body\>、\<b\>等。
3. 传列表，如`bs.find_all(["a", "b"])`，查找所有\<a\>和\<b\>标签。
4. 传方法，如

```python
def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')

print bs.find_all(has_class_but_no_id)
# output:
# [<p class="title"><b>The Dormouse's story</b></p>,
#  <p class="story">Once upon a time there were...</p>,
#  <p class="story">...</p>]
```

#### attrs参数 ####
attrs是一个dict，输入标签属性的key-value形式即可，如

```python
bs.find_all(attrs={"data-foo": "value"})
# [<div data-foo="value">foo!</div>]
```

#### recursive参数 ####
recursive为False时，只搜索当前tag的直接子节点；为True时，搜索当前tag的所有子孙节点。


#### text参数 ####
通过text参数可以搜搜文档中的字符串内容.与name参数的可选值一样，text参数接受字符串、正则表达式、列表、True。

如

```python
bs.find_all(text="Elsie")
# [u'Elsie']

bs.find_all(text=["Tillie", "Elsie", "Lacie"])
# [u'Elsie', u'Lacie', u'Tillie']

bs.find_all(text=re.compile("Dormouse"))
[u"The Dormouse's story", u"The Dormouse's story"]
```


#### kwargs 参数 ####
传入标签属性的key-value即可。

1. `bs.find_all(id='link2')`，返回所有id为link2的标签。
2. `bs.find_all(href=re.compile("elsie"))`，返回所有href属性中匹配到了elsie的标签，如`<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>`也会被返回。
3. `bs.find_all("a", class_="sister")`，class是Python关键字，所以加上下划线，返回所有class="sister"的\<a\>标签。


#### limit参数 ####
限制搜索到的最大结果数量。

如

```python
bs.find_all("a", limit=2)
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>]
```


### bs.select() ###
CSS选择器，以列表形式返回结果。

1. `bs.select('title')`，按标签名查找，返回所有\<title\>标签。
2. `bs.select('.sister')`，按类名查找，返回所有class="sister"的标签。
3. `bs.select('#link1')`，按id查找，返回所有id="link1"的标签。
4. `bs.select('p #link1')`，组合查找，返回所有id="link1"的\<p\>标签。
5. `bs.select('a[class="sister"]')`，按属性查找，返回所有class="sister"的\<a\>标签。

## 爬取知乎动态 ##
### 登录知乎 ###

开启chrome开发者工具，勾选Preserve log，然后登录知乎，就能够看到左下角Name栏里有个email项，从该项得出知乎的登录提交的url为https://www.zhihu.com/login/email。从该项右侧能够看到提交的表单数据，从而可以使用Python来登录知乎。

![查看知乎登录的提交url](img/zhihu_login.jpg)

```python
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
        post_data = urllib.urlencode({
            "_xsrf": xsrf,
            "password": "xxxxxxxxx",
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

```



## Reference ##
1. [python urllib2模块学习](http://blog.csdn.net/youfuchen/article/details/19492821)
2. [Python爬虫入门五之URLError异常处理](http://cuiqingcai.com/961.html)
3. [Python爬虫入门六之Cookie的使用](http://cuiqingcai.com/968.html)
4. [Python爬虫入门八之Beautiful Soup的用法](http://cuiqingcai.com/1319.html)
5. [urllib2的一些常用方法介绍](http://www.nowamagic.net/academy/detail/1302871)