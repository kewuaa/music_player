from random import choice
from pathlib import Path
import json


class UA:
    """随机请求头"""

    with open(Path(__file__).parent / './headers.json', 'rb') as f:
        RANDOM_UAS = json.load(f)['browsers']

    @classmethod
    def get(cls, browser: str) -> dict:
        return {
            'user-agent': choice(cls.RANDOM_UAS.get(browser))
        }


if __name__ == '__main__':
    print(UA.get('firefox'))
