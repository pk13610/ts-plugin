# coding=utf-8


import json

class DoubanUser:
    def __init__(self, email=None, password=None):
            self.email = email
            self.password = password
            self.body = ""

    def load(self,fp):
        self.loads(fp.read())

    def loads(self, s):
        self.body = s
        self.jd = json.loads(s,"utf-8")
        self.name = self.jd["name"]
        self.uid = self.jd["uid"]
        self.token = self.jd["token"]
        self.refresh_token = self.jd["refresh_token"]
        self.expires_in = self.jd["expires_in"]
        self.expires_at = self.jd["expires_at"]

    def registered(self, js, token, refresh_token, expires_in, expires_at):
        self.jd['token']         = token
        self.jd["refresh_token"] = refresh_token
        self.jd["expires_in"]    = expires_in
        self.jd["expires_at"]    = expires_at

    def save2file(self, name):
        open('%s.json' % name, 'w').write(json.dumps(self.jd))

