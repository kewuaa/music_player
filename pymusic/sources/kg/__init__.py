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

    def __init__(
        self,
        loop: asyncio.base_events.BaseEventLoop,
        *,
        browser: str = None,
    ) -> None:
        super().__init__(loop, path=__file__, browser=browser)
        self.__compile = compile(r'{.*}')
        self.__appid = self._loop.create_task(self.__init__appid())
        self._headers.update({
            'origin': 'https://www.kugou.com',
            'refer': 'https://www.kugou.com/',
        })

    async def _init_cookies(self) -> None:
        self.__init_mid()

    def __init_mid(self) -> None:
        """初始化kg_mid."""

        def e() -> str:
            random_num = int(65536 * (1 + random()))
            return hex(random_num)[3:]

        t = e() + e() + '-' + e() + '-' + e() + \
            '-' + e() + '-' + e() + e() + e()
        # n为随机值, 可取固定值
        n = md5(t.encode()).hexdigest()
        self._cookies.update({
            'kg_mid': n,
            'kg_dfid': '0R7uJo1fXgP43wvGER4dHu2X',
            'kg_dfid_collect': 'd41d8cd98f00b204e9800998ecf8427e',
        })

    async def __init__appid(self) -> str:
        sess: ClientSession = await self._sess
        pattenr = compile(r'appid=(\d*)')
        url = 'https://www.kugou.com/'
        res = await sess.get(url)
        source_page = await res.text()
        appid = pattenr.search(source_page).group(1)
        return appid

    def __parse_data(self, data: list) -> list:
        """解析data."""

        def parse(data: dict) -> SongInfo:
            song_name = data['SongName']
            singer_name = data['SingerName']
            album_name = data['AlbumName']
            album_id = data['AlbumID']
            album_audio_id = data['MixSongID']
            file_hash = data['FileHash']
            summary = [song_name, singer_name]
            if album_name:
                summary.append(album_name)
            summary = ' -> '.join(summary)
            source_id = album_id, album_audio_id, file_hash
            ext_name = data['ExtName']
            return SongInfo(
                summary=summary,
                id_=source_id,
                type_=ext_name,
                from_='kg',
            )

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
        key_str = self.KEY.join([
            '',
            ''.join(f'{k}={params[k]}' for k in sorted(params)),
            '',
        ])
        signature = md5(key_str.encode()).hexdigest()
        params['signature'] = signature
        sess: ClientSession = await self._sess
        res = await sess.get(self.SEARCH_URL, params=params)
        res_text = await res.text()
        res_text = self.__compile.findall(res_text)[0]
        res_dict = json.loads(res_text)
        if res_dict.get('error_msg', 1):
            raise RuntimeError(
                res_dict.get('error_msg') or f'\
                unknown error while searching {name}',
            )
        data = res_dict['data']['lists']
        return self.__parse_data(data)

    async def _get_source(self, source_id: tuple) -> str:
        album_id, album_audio_id, file_hash = source_id
        params = {
            'r': 'play/getdata',
            'callback': 'jQuery19108115856637359431_1660387571846',
            'hash': file_hash,
            'dfid': self._cookies['kg_dfid'],
            'appid': await self.__appid,
            'mid': self._cookies['kg_mid'],
            'platid': '4',
            '_': self._get_time_stamp(13),
        }
        if album_id:
            params['album_id'] = album_id
        if album_audio_id:
            params['album_audio_id'] = album_audio_id
        sess: ClientSession = await self._sess
        res = await sess.get(self.SOURCE_URL, params=params)
        res_str = await res.text()
        res_str = self.__compile.findall(res_str)[0]
        res_dict = json.loads(res_str)
        if res_dict.get('err_code', 1):
            err_code = res_dict.get('err_code', 'unknow')
            raise RuntimeError(
                f'while getting source error: {err_code}')
        data = res_dict['data']
        return data['play_url']
