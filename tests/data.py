# admin-path: /manager/

username = 'manager'
password = 'password'


# need tests: length required, bad request, tokens, upload

scenarios = (
    # request(url, method, headers, data) => response(request_handler, response_type, error_code)

    # (url, method, headers, data, request_handler, response_type, error_code)

    # 1. test minimal GET requests
    ('/', 'GET', {}, {}, 'index_page', 'html' , 0),
    ('/', 'GET', {'User-Agent': 'Test Agent'}, {}, 'index_page', 'html' , 0),
    ('/', 'GET', {}, {'data': 'test'}, 'index_page', 'html' , 0),

    # 4. test GET request with more than 1kb header size
    ('/', 'GET', {'User-Agent': ''.join('%s' % i for i in xrange(1000))}, {}, None, 'error', 413),

    # 5. test method other than GET or POST
    ('/', 'OPTIONS', {'User-Agent': 'Test Agent'}, {'data': 'test'}, None, 'error', 405),
    ('/', 'POST', {'User-Agent': 'Test Agent'}, {'data': 'test'}, None, 'error', 405),

    # 7. test theme static file request
    ('/static/style.css', 'GET', {}, {}, None, 'static', 0),

    # 8. test non-exist static files
    ('/static/../../../../../../../etc/passwd', 'GET', {}, {}, None, 'error', 404),
    ('/static/../../../etc/passwd.css', 'GET', {}, {}, None, 'error', 404),
    ('/static/secret.js', 'GET', {}, {}, None, 'error', 404),

    # 9. test POST restrictions
    ('/manager/login/', 'POST', {'User-Agent': 'Test Agent'}, 
        {'username': ''.join('%s' % i for i in xrange(1000)), 'password': 'test'}, None, 'error', 413),

    # 10. test requests for invalid paths
    ('/abcdef', 'GET', {}, {}, None, 'error', 404),
    ('/abcdef', 'POST', {}, {'data': 'test'}, None, 'error', 404),

    # 12. test unauth requests
    ('/manager/', 'GET', {}, {}, 'login_page', 'html', 0),
    ('/manager/settings/', 'POST', {}, {'data': 'test'}, 'login_page', 'html', 0),
    ('/manager/nav/', 'GET', {}, {}, 'login_page', 'html', 0),
    ('/manager/nav/', 'POST', {}, {'data': 'test'}, 'login_page', 'html', 0),
    ('/manager/static/manager.css', 'GET', {}, {}, None, 'static', 0),
    ('/manager/static/manager.css', 'POST', {}, {}, None, 'error', 405),

    # 19. login page
    ('/manager/login/', 'GET', {'User-Agent': 'Test Agent'}, {}, \
        'login_page', 'html', 0),
    ('/manager/login/', 'GET', {'User-Agent': 'Test Agent'}, {'username': 'test', 'password': 'test'}, \
        'login_page', 'html', 0),
    ('/manager/login/', 'GET', {'User-Agent': 'Test Agent'}, {'username': username, 'password': password}, \
        'login_page', 'html', 0),
    ('/manager/login/', 'POST', {'User-Agent': 'Test Agent'}, {'data': 'test'}, \
        None, 'error', 403),
    ('/manager/login/', 'POST', {'User-Agent': 'Test Agent'}, {'username': 'test', 'password': 'test'}, \
        None, 'error', 403),
    ('/manager/login/', 'POST', {'User-Agent': 'Test Agent'}, {'username': username, 'password': password}, \
        None, 'error', 403),

)