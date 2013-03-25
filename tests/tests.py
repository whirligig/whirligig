import sys
import os
import re
import requests
import time
import data

dirname = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(os.path.abspath(dirname))

import files
import functions
import http


host = 'localhost'
port = 10000


redirects = {
    '/manager/login/': functions.login_page
}


def send_request(method, url, headers, data):
    func = getattr(requests, method.lower())
    full_url = 'http://%s:%s%s' % (host, port, url)
    r = func(full_url, data=data, headers=headers, stream=True, allow_redirects=True)

    response = r.raw.read()
    sys.stdout.write("code: %s => " % r.status_code)

    temp_result = re.sub(r'<input.+?>', 'input', response)
    result = re.sub(r'<ul.+?class=[\'\"].+?menu.+?[\'\"]>.+?</ul>', 'menu', temp_result)

    return result


def calculate_response(response_type, request_handler, method, request_uri, headers, data, error_code):
    if response_type == 'html':

        request = {
            'method': method.upper(),
            'path': request_uri,
            'headers': headers,
            'variables': data
        }

        handler = getattr(functions, request_handler)
        response = handler(request).split('\r\n\r\n', 1)

        if response[0].startswith('HTTP/1.0 302 Moved Temporarily\r\nLocation: '):
            redirect = response[0].lower()[42:]
            if redirect in redirects:
                request['method'] = 'GET'
                text = redirects[redirect](request).split('\r\n\r\n', 1)[1]
            else:
                text = response[1]
        else:
            text = response[1]

        temp_result = re.sub(r'<input.+?>', 'input', text)
        result = re.sub(r'<ul.+?class=[\'\"].+?menu.+?[\'\"]>.+?</ul>', 'menu', temp_result)

        return result

    if response_type == 'static':
        root, filename = files.get_static_path(request_uri)
        return files.get_file(root, filename)

    if response_type == 'error':
        return http.error(error_code).split('\r\n\r\n', 1)[1]

    print "Invalid response type"
    exit(0)


def test_function(url, method, headers, data, request_handler, response_type, error_code):
    real_response = send_request(method, url, headers, data)
    calculated = calculate_response(response_type, request_handler, method, url, headers, data, error_code)
    if real_response != calculated:
        print "Test crashed!"

        with open('real_response.txt', 'w') as f:
            f.write(real_response)
        with open('calculated.txt', 'w') as f:
            f.write(calculated)

        exit(0)

    print "OK"

if __name__ == '__main__':
    i = 1
    for args in data.scenarios:
        sys.stdout.write("TEST #%s... " % i)
        test_function(*args)
        i = i + 1
        time.sleep(0.01)
    print "-------------------"
    print "All tests (%s) are passed" % (i-1)