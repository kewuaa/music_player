from urllib import request
from re import compile

from lxml.html import fromstring

url = 'https://music.91q.com/search?word=%E5%88%9A%E5%88%9A%E5%A5%BD'
res = request.urlopen(url)
text = res.read().decode('gbk')
print(text)
