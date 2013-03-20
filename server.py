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
# simple single thread http-server with cache, flood protection
#
import socket
import asyncore
import sys, os, shutil
import tempfile
import random
import time
from urlparse import parse_qsl
import re
import core
import protection
import http
import files
import router

DEBUG = True

BAD_REQUEST = (400, 'Bad Request')
FORBIDDEN = (403, 'Forbidden')
NOT_FOUND = (404, 'Not Found')
NOT_ALLOWED = (405, 'Method Not Allowed')
LENGTH_REQUIRED = (411, 'Length Required')
ENTITY_TOO_LARGE = (413, 'Request Entity Too Large')
INTERNAL_ERROR = (500, 'Internal Error')


MANAGER_STATIC_PATH = '%s/manager/static/' % core.ROOT
THEME_STATIC_PATH = '%s/themes/%s/static/' % (core.ROOT, core.THEME)


ALLOWED_UPLOAD_URIS = (
    '%supload/' % core.MANAGER_URL,
    '%ssettings/' % core.MANAGER_URL,
    '%scatalog/upload/' % core.MANAGER_URL,
)

UPLOADS = {}

#
# client-server channel created by main server channel
#
class Connection(asyncore.dispatcher):

    # recieving chunk size (bytes)
    recv_block_size = 1024

    # sending chunk size (bytes)
    send_block_size = 1024

    # max.size http-headers (bytes)
    max_headers_size = 512

    # max.size http-data for unauth clients (bytes)
    max_unauth_data = 512

    # max.size http-data in memory (bytes)
    max_memory_data_size = 32768

    # request timeout = 30 sec
    timeout = 30

    cache = files.Cache()
    auth = protection.CookieAuthenticator()


    def __init__(self, conn_sock, router):
        asyncore.dispatcher.__init__(self, conn_sock)
        self.router = router
        self.incoming = ''
        self.http_headers_size = -1
        self.buffer_out = ''
        self.http_headers = None
        self.http_data = tempfile.SpooledTemporaryFile(max_size=\
            self.max_memory_data_size)

        self.http_data_size = -1
        self.temp_file = None
        # request_line - (method, uri, version)
        self.request_line = [None, None, None]


    #
    # get directory on local filesystem by request url
    #
    def get_static_path(self, uri):
        root = None
        filename = os.path.basename(uri)
        if uri == '/sitemap.xml' or uri == '/robots.txt':
            root = core.VAR_ROOT
        elif uri == '/static/commons.css':
            root = MANAGER_STATIC_PATH
        elif uri == '/static/core.js':
            root = MANAGER_STATIC_PATH
        elif uri.startswith('/static/pirobox/'):
            root = MANAGER_STATIC_PATH + 'pirobox/'
        elif uri.startswith(core.MANAGER_URL + 'static/'):
            root = MANAGER_STATIC_PATH
        elif uri.startswith('/static/'):
            root = THEME_STATIC_PATH
        elif uri.startswith('/uploads/'):
            root = files.UPLOAD_BASE_PATH
            filename = uri.split('/uploads/', 1)[1]
        elif root is None:
            return root, filename

        # security check
        path = '%s/%s' % (root, filename)
        if not os.path.abspath(path).replace('\\', '/').startswith(root):
            root = filename = None
        return root, filename


    #
    # get file content
    #
    def get_file(self, root, filename):
        content = None
        path = os.path.abspath('%s/%s' % (root, filename))
        try:
            f = open(path, 'r+b')
        except:
            return None

        content = f.read()
        return content


    #
    # create or renew file upload progress
    #
    def set_upload_progress(self, request_uri, variables, recieved, size):

        if request_uri not in ALLOWED_UPLOAD_URIS:
            return

        progress_id = variables.get('X-Progress-ID', None)
        if not progress_id:
            return

        UPLOADS[progress_id] = (recieved, size)
        return


    #
    # get file upload progress (progress_id - GET variable)
    #
    def get_upload_progress(self, variables):
        progress_id = variables.get('X-Progress-ID', None)
        if progress_id:
            result = UPLOADS.get(progress_id, None)
            if result:
                if result[0] == result[1]:
                    del UPLOADS[progress_id]
                return result
        return ('error', 'error')


    #
    # method collect bytes from client when http-headers are not complete
    #
    def _recv_headers(self, bytes):
        separator = bytes.find('\r\n\r\n')

        if separator > -1:
            # complete headers block
            headers = self.incoming + bytes[:separator]
            self.incoming = ''
            lines = headers.splitlines()
            raw_req_line = lines[0].split()
            if len(raw_req_line) != 3:
                self.buffer_out = http.error(*BAD_REQUEST)
                return 'error'

            self.request_line = tuple(raw_req_line)
            self.http_headers = tuple(filter(bool, lines[1:]))
            # first bytes of HTTP data
            self.http_data.write(bytes[separator + 4:])
            self.http_data_size = bytes[separator + 4:].__len__()
            return 'done'

        if self.http_headers_size > self.max_headers_size:
            self.buffer_out = http.error(*ENTITY_TOO_LARGE)
            return 'error'

        self.incoming = self.incoming + bytes
        self.http_headers_size = self.http_headers_size + bytes.__len__()
        return 'recv'


    def _recv_data(self, uri, variables, content_length):
        if self.http_data_size > content_length:
            self.http_data.truncate(content_length)
            self.set_upload_progress(uri, variables, content_length, \
                content_length)
            return False

        self.set_upload_progress(uri, variables, self.http_data_size, \
            content_length)

        if self.http_data_size == content_length:
            return False

        return True


    #
    # recieve bytes from client
    #
    def handle_read(self):
        bytes = self.recv(self.recv_block_size)
        if not bytes:
            return

        # get http-headers
        if not self.http_headers:
            result = self._recv_headers(bytes)
            if result == 'error':
                # error. send response to client
                self.buffer_out = result
                return
            if result == 'recv':
                # http headers are not recieved
                return
        else:
            # get http-data
            self.http_data.write(bytes)
            self.http_data_size = self.http_data_size + bytes.__len__()

        request_method = self.request_line[0]
        parts = self.request_line[1].split('?', 1)
        request_uri = parts[0]
        # GET variables are with unique names!
        variables = dict(parse_qsl(parts[1])) if parts.__len__() > 1 else {}

        if request_method not in ('GET', 'POST'):
            self.buffer_out = http.error(*NOT_ALLOWED)
            return

        headers = []

        # check for static (css|js|img) content
        static_exts = ('.css', '.jpg', '.png', '.gif', '.svg', '.xml', '.txt')
        if request_uri[-4:] in static_exts or \
           request_uri[-3:]  == '.js' or request_uri[-5:] == '.jpeg':

            root, filename = self.get_static_path(request_uri)
            if root is None:
                self.buffer_out = http.error(*NOT_FOUND)
                return

            content = self.get_file(root, filename)
            if content is None:
                self.buffer_out = http.error(*NOT_FOUND)
                return

            # add MIME type to headers
            if request_uri.endswith('.css'):
                headers.append('Content-Type: text/css',)

            if request_uri.endswith('.js'):
                headers.append('Content-Type: application/x-javascript',)

            if request_uri.endswith('.jpg') or request_uri.endswith('.jpeg'):
                headers.append('Content-Type: image/jpeg',)

            if request_uri.endswith('.png'):
                headers.append('Content-Type: image/png',)

            if request_uri.endswith('.gif'):
                headers.append('Content-Type: image/gif',)

            if request_uri.endswith('.svg'):
                headers.append('Content-Type: image/svg+xml',)

            self.buffer_out = http.response(200, "OK", headers, content)
            return

        if request_method == 'POST':
            try:
                content_length = int(http.get_header(self.http_headers, \
                    'Content-Length'))
            except (ValueError, TypeError):
                self.buffer_out = http.error(*LENGTH_REQUIRED)
                return

            # unauth zone request
            if not request_uri.startswith(core.MANAGER_URL) or \
            request_uri == '%slogin/' % core.MANAGER_URL:
                # check POST restrictions
                if content_length > self.max_unauth_data:
                    self.buffer_out = http.error(*ENTITY_TOO_LARGE)
                    return

            # recieve POST data
            if self._recv_data(request_uri, variables, content_length):
                return

            post = http.parse_post_data(self.http_headers, self.http_data, \
                self.max_memory_data_size)
            variables.update(post)

            if not request_uri.startswith(core.MANAGER_URL) or \
            request_uri == '%slogin/' % core.MANAGER_URL:
                # check valid token
                if 'token' not in variables.iterkeys() or \
                not protection.valid_client_token(variables['token']):
                    self.buffer_out = http.error(*FORBIDDEN)
                    return

        # check for upload file progress request
        if request_method == 'GET' and request_uri.endswith('/progress/') and \
        request_uri[:-9] in ALLOWED_UPLOAD_URIS:
            response = self.get_upload_progress(variables)
            self.buffer_out = http.json_data(response)
            return

        # get request line and search in router
        for line in self.router:

            uri = line[0]
            methods = line[1]
            function = line[2]
            response = ''

            m = re.match(uri, request_uri)

            if m and request_method in methods:

                # check cache for existing item
                if request_method != 'POST' and \
                not request_uri.startswith(core.MANAGER_URL) and \
                request_uri != '/connect/':
                    response = self.cache.get(request_uri)

                if not response:
                    # generate response by function
                    parameters = m.groups()

                    request = {
                        'method': request_method,
                        'path': request_uri,
                        'headers': self.http_headers,
                        'variables': variables,
                        'files': None
                    }

                    if DEBUG:
                        response = function(request, *parameters)
                    else:
                        try:
                            response = function(request, *parameters)
                        except:
                            self.buffer_out =  http.error(*INTERNAL_ERROR)
                            return

                    # add to cache
                    if request_method != 'POST' and \
                    not request_uri.startswith(core.MANAGER_URL) and \
                    request_uri != '/connect/':
                        self.cache.set(request_uri, response)

                # copy to buffer
                self.buffer_out = response
                return

        # send to client 404 error
        # (request uri is not found in router)
        self.buffer_out =  http.error(*NOT_FOUND)
        return


    def handle_write(self):
        sent = self.send(self.buffer_out[:self.send_block_size])
        self.buffer_out = self.buffer_out[sent:]
        if not self.buffer_out:
            self.handle_close()


    def handle_close(self):
        self.close()


    def writable(self):
        return (len(self.buffer_out) > 0)

#
# main channel for listening port
#
class WebServer(asyncore.dispatcher):

    handlerClass = Connection

    def __init__(self, router, host='localhost', port=10000):
        self.router = router
        self.host = host
        self.port = port
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        try:
            self.bind((self.host, self.port))
        except socket.error:
            print "Unable bind socket to host:port"
            exit(1)
        self.listen(500)


    def run(self, use_poll=True):
        print "Whirligig running on %s:%s..." % (self.host, self.port)
        asyncore.loop(use_poll=use_poll, timeout=0.1)


    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            conn_sock, client_address = pair
            self.handlerClass(conn_sock, self.router)


    def handle_close(self):
        self.close()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        host = '127.0.0.1'
        port = 10000

    ws = WebServer(router.router, host=host, port=port)
    ws.run(use_poll=True)