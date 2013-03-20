Small lightweight CMS written on Python.

It contains:
- one threaded server with non-blocking sockets (asyncore) with cache
- simple template engine with one default theme:
    - tags (loop, condition)
    - globals
    - filters
- flood protection tokens (for POST requests)
- updated sitemap

Whirligig allows manage static pages, create catalog of production/services,
recieve feedbacks.

For installation you need only Python 2.7 and PIL:

python install.py /secret-login/

You will get password (save it)

python server.py localhost 10000

Whirligig is:
- not WGSI application
- does not contains unicode strings
- untested!