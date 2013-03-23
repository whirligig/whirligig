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

from signal import signal, SIGTERM

DEBUG = True

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
    # <= recv_block_size
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
        self.error = 0
        # request_line - (method, uri, version)
        self.request_line = [None, None, None]


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
                self.error = 400
                self.buffer_out = http.error(self.error)
                return 'error'

            self.request_line = tuple(raw_req_line)
            self.http_headers = tuple(filter(bool, lines[1:]))
            # first bytes of HTTP data
            self.http_data.write(bytes[separator + 4:])
            self.http_data_size = bytes[separator + 4:].__len__()
            return 'done'

        if self.http_headers_size > self.max_headers_size:
            self.error = 413
            self.buffer_out = http.error(self.error)
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
            if result != 'done':
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
            self.error = 405
            self.buffer_out = http.error(self.error)
            return

        headers = []

        # check for static (css|js|img) content
        static_exts = ('.css', '.jpg', '.png', '.gif', '.svg', '.xml', '.txt')
        if request_uri[-4:] in static_exts or \
           request_uri[-3:]  == '.js' or request_uri[-5:] == '.jpeg':

            if request_method == 'POST':
                self.error = 405
                self.buffer_out = http.error(self.error)
                return

            root, filename = files.get_static_path(request_uri)
            if root is None:
                self.error = 404
                self.buffer_out = http.error(self.error)
                return

            content = files.get_file(root, filename)
            if content is None:
                self.error = 404
                self.buffer_out = http.error(self.error)
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

        # check request url in router
        found = False
        for line in self.router:

            uri = line[0]
            functions = line[1]
            cachable = line[2]
            response = ''

            m = re.match(uri, request_uri)

            if m:
                if request_method == 'GET' and functions[0]:
                    found = True
                    function = functions[0]
                    break

                if request_method == 'POST' and functions[1]:
                    found = True
                    function = functions[1]
                    break

                self.error = 405
                self.buffer_out =  http.error(self.error)
                return

        if not found:
            self.error = 404
            self.buffer_out =  http.error(self.error)
            return

        # POST request
        if request_method == 'POST':
            try:
                content_length = int(http.get_header(self.http_headers, \
                    'Content-Length'))
            except (ValueError, TypeError):
                self.error = 411
                self.buffer_out = http.error(self.error)
                return

            # unauth zone request
            if not request_uri.startswith(core.MANAGER_URL) or \
            request_uri == '%slogin/' % core.MANAGER_URL:
                # check POST restrictions
                if content_length > self.max_unauth_data:
                    self.error = 413
                    self.buffer_out = http.error(self.error)
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
                    self.error = 403
                    self.buffer_out = http.error(self.error)
                    return

        # check for upload file progress request
        if request_method == 'GET' and request_uri.endswith('/progress/') and \
        request_uri[:-9] in ALLOWED_UPLOAD_URIS:
            response = self.get_upload_progress(variables)
            self.buffer_out = http.json_data(response)
            return

        need_generate_response = False
        need_cache = False

        # check cache for existing item
        if request_method == 'GET' and cachable:
            response = self.cache.get(request_uri)

            if not response:
                need_generate_response = True
                need_cache = True

        if request_method == 'GET' and not cachable:
            need_generate_response = True
            need_cache = False

        # POST requests are not cachable
        if request_method == 'POST':
            need_generate_response = True
            need_cache = False

        if need_generate_response:
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
                    self.error = 500
                    self.buffer_out =  http.error(self.error)
                    return

        if need_cache:
            # add to cache
            self.cache.set(request_uri, response)

        # copy to buffer
        self.buffer_out = response
        return


    def handle_write(self):
        sent = self.send(self.buffer_out[:self.send_block_size])
        self.buffer_out = self.buffer_out[sent:]
        if not self.buffer_out:
            self.handle_close()


    def handle_close(self):
        self.close()


    def readable(self):
        if self.error:
            return False
        return True


    def writable(self):
        return (len(self.buffer_out) > 0)

#
# main channel
#
class WebServer(asyncore.dispatcher):

    handlerClass = Connection

    def __init__(self, router, host, port):
        asyncore.dispatcher.__init__(self)
        self.router = router
        self.host = host
        self.port = port

        self.stdin = '/dev/null'
        self.stdout = os.path.join(core.ROOT, 'var/messages.log')
        self.stderr = os.path.join(core.ROOT, 'var/errors.log')
        self.pidfile = os.path.join(core.ROOT, 'var/whriligig.pid')

    def daemonize(self):

        def _clear(signum, stack_frame):
            #remove pidfile
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)

            sys.exit(0)

        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        signal(SIGTERM, _clear)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def start(self):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        try:
            self.bind((self.host, self.port))
        except socket.error:
            sys.stderr.write("Unable bind socket to %s:%s\n" % (self.host, self.port))
            sys.exit(1)

        self.listen(500)

        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        asyncore.loop(use_poll=True, timeout=0.1)

    def stop(self):
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            print "pidfile '%s' is not found. Daemon not running?" % self.pidfile
            return

        # Try killing the daemon process       
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") < 0:
                sys.stderr.write(str(err))
                sys.exit(1)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            conn_sock, client_address = pair
            self.handlerClass(conn_sock, self.router)

    def handle_close(self):
        self.close()


if __name__ == '__main__':

    syntax = "syntax: python server.py [start|stop] [host] [port]"

    args = len(sys.argv)

    if args < 2:
        print
        print syntax
        print
        exit(0)

    host = '127.0.0.1'
    port = 10000

    if args > 1:
        action = sys.argv[1]
    if args > 2:
        host = sys.argv[2]
    if args > 3:
        try:
            port = int(sys.argv[3])
        except ValueError:
            print 'Invalid argument "port"'
            exit(0)

    ws = WebServer(router.router, host, port)

    if action == 'start':
        ws.start()

    if action == 'stop':
        ws.stop()
