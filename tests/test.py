import sys
import asyncio
sys.path.append('.')
import pymusic
from pymusic.sources.kg import kg


pymusic.run()
loop = asyncio.get_event_loop()
# _kg = kg.KgSource(loop=loop)
# info = loop.run_until_complete(_kg._get_info('刚刚好'))
# print(info)
# url = loop.run_until_complete(_kg._get_source(info[0].id))
# print(url)
