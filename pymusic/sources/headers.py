from random import choice
from pathlib import Path
import json


class UA:
    """随机请求头"""

    def __init__(self) -> None:
        f = open(Path(__file__).parent / './headers.json', 'rb')
        self._uas = json.load(f)['browsers']
        f.close()

    def __getattribute__(self, name: str) -> None:
        uas = super().__getattribute__('_uas')
        ua = uas.get(name)
        if ua is not None:
            return {'user-agent': choice(ua)}
        else:
            raise AttributeError(name)


if __name__ == '__main__':
    ua = UA()
    print(ua.chrome)
    print(ua.firefox)
    print(eval('ua.firefox'))
