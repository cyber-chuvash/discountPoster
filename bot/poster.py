import logging
import time

import requests
from vk_requests.api import API
from vk_requests.session import VKSession
from vk_requests.exceptions import VkAPIError

from bot.config import Config


class VKApi(API):
    API_CALL_INTERVAL = 0.35

    def __init__(self):
        super().__init__(
            VKSession(
                user_login=Config.vk_login,
                user_password=Config.vk_password,
                app_id=Config.app_id,
                scope='wall,photos,groups,offline',
                api_version='5.92'),
            http_params=None)
        self.last_api_call = 0

    def __getattr__(self, item):
        cur_time = time.time()
        if cur_time - self.last_api_call < self.API_CALL_INTERVAL:
            sleep_for = self.last_api_call + self.API_CALL_INTERVAL - cur_time
            logging.debug(f'Sleeping for {sleep_for}')
            time.sleep(sleep_for)
        attr = super().__getattr__(item)
        self.last_api_call = time.time()
        return attr


class Poster:
    def __init__(self):
        self.vk = VKApi()

    def upload_photo(self, url):
        try:
            photo = requests.get(url).content
            up_serv = self.vk.photos.getWallUploadServer(group_id=Config.group_id)
            upload_url, album_id, user_id = up_serv['upload_url'], up_serv['album_id'], up_serv['user_id']
            req = requests.post(upload_url, files={'photo': ('photo.png', photo)}).json()
            vk_photo = self.vk.photos.saveWallPhoto(
                group_id=Config.group_id,
                photo=req['photo'],
                server=req['server'],
                hash=req['hash']
            )[0]
            return f'photo{vk_photo["owner_id"]}_{vk_photo["id"]}'
        except Exception:
            logging.warning(f'Error while uploading photo from url {url} to VK:', exc_info=True)
            return ''

    def post(self, text, attachments=None):
        logging.debug(f'Attachments: {attachments}')
        if attachments and not isinstance(attachments, str):
            attachments = ','.join(attachments)
            logging.debug(f'Joined attachments: {attachments}')
        try:
            self.vk.wall.post(
                owner_id=f'-{Config.group_id}',
                from_group=1,
                message=text,
                attachments=attachments or '',
            )
        except VkAPIError:
            logging.warning(f'Error while making a post. Text:\n{text}\nAttachments: {attachments}', exc_info=True)

