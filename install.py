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

import sys
import os
import datetime
from core import *

if len(sys.argv) != 2:
    print
    print "sintax: python install.py [manager-url]"
    print "example: python install.py /admin/"
    print
    exit(-1)

manager_url = sys.argv[1]
theme = 'default'

config = ConfigManager()
config.install()
config.set('sitename', 'Site name')

config.parse_theme(theme)

config.set('manager_url', manager_url)
MANAGER = config.get('manager_url')
print 'Manager url has been set as %s' % MANAGER
print 'Manager login url has been set as %slogin/' % MANAGER

config.set('translator_cid', '8f265b31-9f86-408f-9e66-986acb0b9d78')
config.set('translator_secret', 'ZZa2P1C6UoGci4ORZKIcKLKJYGzoNHvzpcugcLCg+Qw=')

config.set('install_date', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

config.done()

auth = AuthManager()
auth.install()
password = auth.create_auth(username=u'manager')
print 'Created auth. Password:', password
auth.done()

nav = NavigationManager()
nav.install()
nav.gather_menu_names()
nav.done()

page = PageManager()
page.install()
page.done()

catalog = CatalogManager()
catalog.install()
catalog.done()

uploaded = UploadedManager()
uploaded.install()
uploaded.done()

# check for requiring theme logo

# install paths in manager static files
dist_path = os.path.join(os.path.dirname(__file__), 'data', 'dist')
install_path = os.path.join(os.path.dirname(__file__), 'manager', 'static')

for filename in os.listdir(dist_path):

    if filename.endswith('.dist'):

        path1 = os.path.abspath(os.path.join(dist_path, filename))
        with open(path1, 'r+b') as source:
            content = source.read().replace('<<MANAGER_URL>>', MANAGER)

        path2 = os.path.abspath(os.path.join(install_path, filename[:-5]))
        with open(path2, 'w+b') as destination:
            destination.write(content)

# create default robots.txt file
try:
    f = open(os.path.join(VAR_ROOT, 'robots.txt'), 'w+b')
    f.write('User-agent: *\r\nAllow: /*\r\n')
    f.close()
except:
    print "warning: 'robots.txt' has not been created"

print
print 'For run whirligig: python server.py'