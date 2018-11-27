import json
import os


class _JsonConfig:
    def __init__(self):
        self._conf = \
            json.loads(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '../config.json'), 'r').read())

    def __getattr__(self, item):
        return self._conf[item]


class _EnvConfig:
    ENV_KEYS = {
        'vk_login': 'VK_LOGIN',
        'vk_password': 'VK_PASS',
        'app_id': 'VK_APP_ID',
        'group_id': 'VK_GROUP_ID',
        'mysql_host': 'MYSQL_HOST',
        'mysql_login': 'MYSQL_LOGIN',
        'mysql_password': 'MYSQL_PASS',
        'mysql_db': 'MYSQL_DB',
        'post_photo': 'POST_PHOTO',
        'job_interval_sec': 'JOB_INTERVAL_SEC'
    }

    def __getattr__(self, item):
        return os.environ[self.ENV_KEYS[item]]


try:
    Config = _JsonConfig()

except FileNotFoundError:
    Config = _EnvConfig()
