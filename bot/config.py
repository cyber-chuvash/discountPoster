import json
import os


class _Config:
    def __init__(self):
        self._conf = \
            json.loads(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.json'), 'r').read())

    def __getattr__(self, item):
        return self._conf[item]


Config = _Config()
