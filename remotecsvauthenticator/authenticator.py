import io
import csv
import hashlib
import binascii
from datetime import datetime

from jupyterhub.auth import Authenticator

from traitlets import Unicode, Int, observe

from tornado import gen
from tornado.httpclient import AsyncHTTPClient


class RemoteCSVAuthenticator(Authenticator):
    csv_url = Unicode(
        help='URL to hit to fetch CSV containing authentication info',
        config=True
    )

    cache_seconds = Int(
        default=300,
        help='Number of seconds to cache the CSV file before re-fetching',
        config=True
    )

    @gen.coroutine
    def get_remote_csv(self):
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(self.csv_url)
        reader = csv.DictReader(io.TextIOWrapper(response.buffer, encoding='utf-8'))
        return {
            r['username']: {'password_hash': r['password_hash']}
            for r in reader
        }

    @gen.coroutine
    def get_user_info(self):
        if hasattr(self, '_last_updated'):
            print(self.cache_seconds)
            print(self._last_updated - datetime.now())
            if (datetime.now() - self._last_updated).total_seconds() > self.cache_seconds:
                self.log.info('Invalidating cache!')
                del self._userinfo
        if not hasattr(self, '_userinfo'):
            self.log.info('Fetching CSV from URL')
            self._userinfo = yield self.get_remote_csv()
            self._last_updated = datetime.now()
        return self._userinfo

    @gen.coroutine
    def authenticate(self, handler, data):
        user_info = yield self.get_user_info()
        if data['username'] not in user_info:
            return None
        dk = hashlib.pbkdf2_hmac('sha256', data['password'].encode('utf-8'), data['username'].encode('utf-8'), 1000)
        self.log.error(binascii.hexlify(dk))
        if binascii.hexlify(dk).decode('utf-8') == user_info[data['username']]['password_hash']:
            return data['username']
        return None
