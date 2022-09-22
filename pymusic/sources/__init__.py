from pymusic.lib import asynctk
from .model import set_stdout
from .model import SourceModel


SOURCE_OPTIONS = {
    'kg': '酷狗',
    'kw': '酷我',
    'mg': '咪咕',
    'qq': 'QQ',
    'qqjt': '千千静听',
    'wyy': '网易云',
}


def get(name: str) -> SourceModel:
    module = __import__(
        name,
        globals(),
        locals(),
        [],
        level=1,
    )
    source = module.Source(asynctk._callback_loop)
    asynctk.add_done_before_exit(source.exit)
    return source
