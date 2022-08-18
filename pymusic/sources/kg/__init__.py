from random import random
from hashlib import md5
from re import compile
import asyncio
import json

from aiohttp import ClientSession

from ..model import SourceModel
from ..model import SongInfo


class Source(SourceModel):
    """酷狗"""

    KEY = 'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt'
    SEARCH_URL = 'https://complexsearch.kugou.com/v2/search/song'
    SOURCE_URL = 'https://wwwapi.kugou.com/yy/index.php'

    def __init__(self, loop: asyncio.base_events.BaseEventLoop,
                 *, browser: str = None) -> None:
        super().__init__(loop, path=__file__, browser=browser)
        self._compile = compile(r'{.*}')
        self._init_mid()
        self._headers.update({
            'origin': 'https://www.kugou.com',
            'refer': 'https://www.kugou.com/',
        })

    def _init_mid(self) -> None:
        """初始化kg_mid."""

        def e() -> str:
            random_num = int(65536 * (1 + random()))
            return hex(random_num)[3:]

        t = e() + e() + '-' + e() + '-' + e() + \
            '-' + e() + '-' + e() + e() + e()
        n = md5(t.encode()).hexdigest()
        self._cookies['kg_mid'] = n
        self._cookies.update({
            'kg_mid': n,
            'kg_dfid': '4XSVnN1pTe8A2jz9zb4UyqVS',
            'kg_dfid_collect': 'd41d8cd98f00b204e9800998ecf8427e',
        })

    def _parse_data(self, data: list) -> list:
        """解析data."""

        def parse(data: dict) -> SongInfo:
            song_name = data['SongName']
            singer_name = data['SingerName']
            album_name = data['AlbumName']
            album_id = data['AlbumID']
            file_hash = data['FileHash']
            summary = f'{song_name} -> {singer_name}'
            if album_name:
                summary += f' -> 《{album_name}》'
            source_id = album_id, file_hash
            ext_name = data['ExtName']
            info = SongInfo(summary=summary, id_=source_id, type_=ext_name, from_='kg')
            return info

        return [parse(item) for item in data]

    async def _get_info(self, name: str) -> list:
        time_stamp = self._get_time_stamp(13)
        params = {
            'callback': 'callback123',
            'keyword': name,
            'page': '1',
            'pagesize': '30',
            'bitrate': '0',
            'isfuzzy': '0',
            'inputtype': '0',
            'platform': 'WebFilter',
            'userid': '0',
            'clientver': '2000',
            'iscorrection': '1',
            'privilege_filter': '0',
            'filter': '10',
            'token': '',
            'srcappid': '2919',
            'clienttime': time_stamp,
            'mid': time_stamp,
            'uuid': time_stamp,
            'dfid': '-',
        }
        key_str = self.KEY + \
            ''.join(f'{k}={params[k]}' for k in sorted(params)) + \
            self.KEY
        signature = md5(key_str.encode()).hexdigest()
        params['signature'] = signature
        sess: ClientSession = await self._sess
        res = await sess.get(self.SEARCH_URL, params=params)
        res_text = await res.text()
        res_text = self._compile.findall(res_text)[0]
        res_dict = json.loads(res_text)
        if res_dict.get('error_msg', 1):
            raise RuntimeError(
                res_dict.get(
                    'error_msg') or f'unknown error while searching {name}')
        data = res_dict['data']['lists']
        return self._parse_data(data)

    async def _get_source(self, source_id: tuple) -> str:
        album_id, file_hash = source_id
        params = {
            'r': 'play/getdata',
            'callback': 'jQuery19108115856637359431_1660387571846',
            'hash': file_hash,
            'dfid': self._cookies['kg_dfid'],
            'appid': '1014',
            'mid': self._cookies['kg_mid'],
            'platid': '4',
            '_': self._get_time_stamp(13),
        }
        if album_id:
            params['album_id'] = album_id
        sess: ClientSession = await self._sess
        res = await sess.get(self.SOURCE_URL, params=params)
        res_str = await res.text()
        res_str = self._compile.findall(res_str)[0]
        res_dict = json.loads(res_str)
        if res_dict.get('err_code', 1):
            err_code = res_dict.get('err_code', 'unknow')
            raise RuntimeError(
                f'while getting source error: {err_code}')
        data = res_dict['data']
        return data['play_url']
