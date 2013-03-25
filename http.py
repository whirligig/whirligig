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
# util methods
#
import urlparse
import re
import os
import json
import mmap
from output import html
import files


def response(code, message, headers=[], body=''):
    if headers:
        http_headers = '\r\n'.join(headers)
        return 'HTTP/1.0 %s %s\r\n%s\r\n\r\n%s' % (code, message, \
            http_headers, body)

    return 'HTTP/1.0 %s %s\r\n\r\n%s' % (code, message, body)


def error(code):
    if code == 400:
        message = "Bad Request"
    if code == 403:
        message = "Forbidden"
    if code == 404:
        message = "Not Found"
    if code == 405:
        message = "Method Not Allowed"
    if code == 411:
        message = "Length Required"
    if code == 413:
        message = "Request Entity Too Large"
    if code == 500:
        message = "Internal Error"

    body = error_page(code, message)
    headers = ['Content-Length: %s' % body.__len__()]
    return response(code, message, headers, body)


def redirect(uri, headers=[]):
    line = ['Location: %s' % uri]
    return response(302, 'Moved Temporarily', headers + line)


def html_page(path, variables, request=None):
    body = html.template(path, variables, request)
    headers = (
        'Content-Type: text/html',
        'Content-Length: %s' % body.__len__()
    )
    return response(200, "OK", headers, body)


def text_data(data):
    headers = (
        'Content-Type: text/plain',
        'Content-Length: %s' % data.__len__()
    )
    return response(200, "OK", headers, data)


def json_data(data):
    body = json.dumps(data)
    headers = (
        'Content-Type: application/json',
        'Content-Length: %s' % body.__len__()
    )
    return response(200, "OK", headers, body)


def error_page(code, message):

    context = {
        'code': code,
        'message': message
    }

    return html.template('error.tpl', context, None)


#
# get client ip address
#
def get_client_ip(request_headers):
    if not request_headers:
        return None

    for line in request_headers:
        if line.startswith('HTTP_CLIENT_IP: '):
            return line[16:]
        elif line.startswith('HTTP_X_FORWARDED_FOR: '):
            return line[22:]
        elif line.startswith('HTTP_X_FORWARDED: '):
            return line[18:]
        elif line.startswith('HTTP_X_CLUSTER_CLIENT_IP: '):
            return line[26:]
        elif line.startswith('HTTP_FORWARDED_FOR: '):
            return line[20:]
        elif line.startswith('HTTP_FORWARDED: '):
            return line[16:]
        elif line.startswith('REMOTE_ADDR: '):
            return line[13:]
    return None


#
# get header value
#
def get_header(headers, name):
    if not headers:
        return None

    for line in headers:
        if line.lower().startswith('%s: ' % name.lower()):
            return line[name.__len__() + 2:]
    return None


def parse_post_data(headers, data, max_memory):
    variables = {}
    content_type = get_header(headers, 'Content-Type')

    if not content_type:
        content_type = 'application/x-www-form-urlencoded'

    data.seek(0)

    m = re.match(r'''
            ^multipart/form-data;
            \s*boundary=[\"|\']?([^\"\']{1,70})[\"|\']?$
        ''', content_type, re.VERBOSE)

    if m:
        boundary = m.group(1)
        regexp = re.compile(r'''
            Content-Disposition:\sform-data;\s*
            name="(?P<name>\w+)"(;\s*filename="(?P<filename>.*?)")?
            .*?\r\n\r\n(.*?)\r\n--%s
        ''' % re.escape(boundary), (re.VERBOSE | re.MULTILINE | re.DOTALL))

        data.seek(0, 2)

        if data.tell() <= max_memory:
            data.seek(0)
            iterator = regexp.finditer(data.read())
            for i in iterator:
                g = i.groupdict()
                if g['filename']:
                    # save part data to file
                    path = files.get_available_name(g['filename'])
                    with open(path, 'w+b') as fd:
                        fd.write(i.group(4))
                        variables[g['name']] = os.path.basename(path)
                else:
                    variables[g['name']] = i.group(4)

        else:
            # large data
            data.seek(0)
            mp = mmap.mmap(data.fileno(), 0)
            iterator = regexp.finditer(mp)
            for i in iterator:
                g = i.groupdict()

                if g['filename']:
                    # save file and assign POST variable
                    start = i.start(4)
                    end = i.end(4)
                    size = end - start
                    parts = size // max_memory
                    rest = size % max_memory
                    data.seek(start, 0)

                    # save part data to file
                    path = files.get_available_name(g['filename'])
                    with open(path, 'wb') as fd:
                        for block in xrange(parts):
                            fd.write(data.read(max_memory))
                        fd.write(data.read(rest))
                        variables[g['name']] = os.path.basename(path)
                else:
                    start = i.start(4)
                    end = i.end(4)
                    variables[g['name']] = mp[start:end]
            mp.close()

    if content_type.startswith('application/x-www-form-urlencoded'):
        data.seek(0)
        variables = dict(urlparse.parse_qsl(data.read()))

    data.close()

    return variables