from urllib import request
from re import compile

from lxml.html import fromstring

url = 'https://music.migu.cn/v3'
res = request.urlopen(url)
text = res.read().decode()
tree = fromstring(text)
app_info = tree.xpath('//script[@type="text/javascript"]/text()')[0]
print(app_info)
app_info = compile(r'{([\s\S]+?)}').search(app_info).group(1)
a = [pair.split(':', 1) for pair in app_info.split('\n') if pair]
for b in a:
    print(b, type(b), len(b))
    k, v = b
    print(k, v)
print({
    k: v.strip().strip("'").strip('"')
    for k, v in [
      pair.split(':', 1)
      for pair in app_info.split('\n')
      if pair
    ]
})
