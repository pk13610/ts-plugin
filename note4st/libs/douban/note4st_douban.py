# -*- coding: utf-8 -*-

import sys
# reload(sys)
# sys.setdefaultencoding('gbk')

from douban_client import DoubanClient
from douban_user import DoubanUser

KEY = '0a235fff9ef07b751e6a1ffedcd1725f'
SECRET = 'nonesense'
CALLBACK = 'http://127.0.0.1/note4st'
SCOPE = 'douban_basic_common,\
        community_basic_user,\
        community_basic_note,\
        community_basic_photo,\
        community_basic_online'


class Note4stDouban:
    def __init__(self, user_json_file=None):
        """douban client for note4st
              user_json_file - solved on register
        """
        self.client = None
        self.user = DoubanUser()
        self.is_login = False
        if user_json_file:
            self.user.load(open(user_json_file))

    def register(self, auth_code):
        """douban client for note4st
              user_json_file - solved on register
        """
        self.client = DoubanClient(KEY, SECRET, CALLBACK, SCOPE)
        self.client.auth_with_code(auth_code)
        self.user.registered(
            self.client.user.me,
            self.client.user.access_token.token,
            self.client.user.access_token.refresh_token,
            self.client.user.access_token.expires_in,
            self.client.user.access_token.expires_at,
        )
        self.user.save2file(self.user.name)
        self.is_login = True

    def login(self, email=None, password=None, token=None):
        if not self.client:
            self.client = DoubanClient(KEY, SECRET, CALLBACK, SCOPE)
        if token:
            self.client.auth_with_token(token)
            self.client.auth_with_token(token)
        else:
            self.client.auth_with_password(email, password)
            self.user.refresh_token = self.client.refresh_token_code
        self.user.uid = self.client.user.me['uid']
        self.is_login = True


if __name__ == "__main__":
    client = Note4stDouban("../../anonymous.json")
    client.login(None, None, client.user.token)
    res = client.client.note.list(client.user.uid)
    print res
