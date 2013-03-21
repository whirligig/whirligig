#    Copyright (C) 2013 Denis Glushkov <denis@signal-mechanisms.com>
#
#    This file is part of Whirliglg.
#
#    Whirliglg is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Whirliglg is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Whirliglg.  If not, see <http://www.gnu.org/licenses/>.

#
# flood protection tokens, authentication
#
import time
import random
import Cookie
import core

flood_protection_buffer = {}
flood_protection_buffer_size = 1000     # 1000 tokens
flood_protection_min_time = 5           # 5 sec
flood_protection_max_time = 120         # 120 sec


def random_token():
    return '%032x' % random.randrange(256**16)


def set_server_token():
    current = time.time()

    for token, created in flood_protection_buffer.items():
        if (current < created + flood_protection_min_time) or \
        (current > created + flood_protection_max_time):
            del flood_protection_buffer[token]

    print flood_protection_buffer.__len__(), flood_protection_buffer_size

    if flood_protection_buffer.__len__() > flood_protection_buffer_size:
        return None

    token = random_token()

    if token in flood_protection_buffer.iterkeys():
        return None

    flood_protection_buffer[token] = time.time()
    return token


def valid_client_token(client_token):
    current = time.time()

    for token, created in flood_protection_buffer.items():
        if client_token != token:
            continue

        if (current > created + flood_protection_min_time) and \
        (current < created + flood_protection_max_time):
            del flood_protection_buffer[token]
            return True

    return False


class CookieAuthenticator(object):

    def __init__(self):
        self.session_name = 'mid'
        self.salt = 'chJty_90$fgRR190qGk'


    # expires - 2 days
    def set_cookie(self, name, value, expires=2, max_age=2*24*3600):
        expires = time.strftime("%a, %d %b %Y %H:%M:%S GMT", \
            time.gmtime(time.time() + 2 * 24 * 3600))
        c = Cookie.SimpleCookie()
        c[name] = value
        c[name]['expires'] = expires
        c[name]['max-age'] = max_age
        c[name]['path'] = '/'
        return c.output()


    def get_cookie(self, headers, name):
        c = Cookie.SimpleCookie()
        for line in headers:
            if line.startswith('Cookie: '):
                c.load(line)
        if name not in c:
            return None
        result = c[name].value
        del c
        return result


    def clear_cookie(self, name):
        return self.set_cookie(name, '', \
            expires='Thu, 01 Jan 1970 00:00:10 GMT', max_age=0)


    def valid_auth(self, headers):
        session_value = self.get_cookie(headers, self.session_name)
        db = core.AuthManager()
        result = db.check_sid(session_value)
        db.done()
        return result


    def login(self, username, password):
        db = core.AuthManager()
        result = db.authorize(username, password)
        if result:
            return self.set_cookie(self.session_name, result)
        return None


    def logout(self, headers):
        db = core.AuthManager()
        if self.valid_auth(headers):
            return self.clear_cookie(self.session_name)
        return None