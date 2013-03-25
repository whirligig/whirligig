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

from abc import ABCMeta
from random import choice
import urllib
import urllib2
import time
import json
import hashlib
import re
import os
import uuid
import sqlite3

ROOT = os.path.dirname(__file__)
VAR_ROOT = os.path.join(ROOT, 'var/')


class SqliteManager(object):

    __metaclass__ = ABCMeta
    __slots__ = ('datafile', 'connection', 'cursor', 'items_per_page')

    def __init__(self, *args, **kwargs):
        super(SqliteManager, self).__init__(*args, **kwargs)
        self.datafile = os.path.dirname(__file__) + '/data/database.sqlite'
        self.connection = sqlite3.Connection(self.datafile, detect_types=sqlite3.PARSE_DECLTYPES)

        self.connection.text_factory = str
        self.cursor = self.connection.cursor()
        self.cursor.executescript('''
            pragma foreign_keys = ON;
            pragma count_changes = OFF;
        ''')
        self.items_per_page = 20


    def valid_tuple(self, table, t):
        if not isinstance(t, (tuple, list)):
            return False

        self.cursor.execute('pragma table_info({0})'.format(table))
        field_names = map(lambda x: x[1], self.cursor.fetchall())
        field_names.remove('id')

        for name, _ in t:
            if name not in field_names:
                return False

        return True


    def done(self):
        self.cursor.close()
        self.connection.close()


class ConfigManager(SqliteManager):

    def __init__(self, *args, **kwargs):
        super(ConfigManager, self).__init__(*args, **kwargs)


    def exists(self):
        query = 'select * from config'
        try:
            self.cursor.execute(query)
        except sqlite3.OperationalError:
            return False

        return True


    def install(self):
        query = 'drop table if exists config;'
        query += '''create table config (
            prop varchar(25) not null primary key,
            value varchar(75) not null
        );'''
        self.cursor.executescript(query)


    def set(self, prop, value):
        query = 'insert or replace into config(prop, value) values(?, ?)'
        self.cursor.execute(query, (prop, value))
        self.connection.commit()
        return True


    def get(self, prop, empty=None):
        query = 'select value from config where prop=?'
        self.cursor.execute(query, (prop,))
        row = list(self.cursor)
        if not row:
            return empty

        return row[0][0]


class AuthManager(SqliteManager):

    def __init__(self, *args, **kwargs):
        super(AuthManager, self).__init__(*args, **kwargs)
        self.salt = 'Wrtu_6r42QDnkl58)80_v'


    def install(self):
        query = 'drop table if exists auth;'
        query += '''create table auth (
            id integer not null primary key,
            username varchar(30) not null unique on conflict abort,
            password varchar(128) not null,
            first_name varchar(30),
            last_name varchar(30),
            sid varchar(32)
        );'''
        self.cursor.executescript(query)


    def generate_password(self):
        chars = "234679ADEFGHJKLMNPRTUWabdefghijkmnpqrstuwy_"
        length = 12
        password = ''.join([choice(chars) for i in xrange(length)])
        return password


    def encrypt_password(self, password):
        m = hashlib.sha224(self.salt)
        m.update(password)
        return m.hexdigest()


    def create_auth(self, username, first_name=None, last_name=None):
        password = self.generate_password()
        _password = self.encrypt_password(password)
        query = 'insert into auth(username, password, first_name, password) values(?, ?, ?, ?)'
        try:
            self.cursor.execute(query, (username, _password, first_name, last_name))
            self.connection.commit()
        except:
            return None

        return password


    def remove_auth(self, username):
        query = 'delete from auth where username=?'
        self.cursor.execute(query, (username,))
        self.connection.commit()
        return True


    def authorize(self, username, password):
        password = self.encrypt_password(password)
        query = 'select id from auth where username=? and password=?'
        self.cursor.execute(query, (username, password))
        manager = list(self.cursor)
        if not manager:
            return None

        query = 'update auth set sid=? where id=?'
        sid = self.generate_sid()
        self.cursor.execute(query, (sid, manager[0][0]))
        self.connection.commit()
        return sid


    def generate_sid(self):
        return uuid.uuid4().hex


    def check_sid(self, sid):
        if not sid:
            return False

        query = 'select username from auth where sid=?'
        self.cursor.execute(query, (sid,))
        rows = list(self.cursor)
        if not rows:
            return False

        return True

class NavigationManager(SqliteManager):

    def __init__(self, *args, **kwargs):
        super(NavigationManager, self).__init__(*args, **kwargs)


    def install(self):
        query = '''
        drop table if exists navigation_menus;

        create table navigation_menus (
            id integer not null primary key,
            name varchar(15) not null
        );

        drop table if exists navigation_items;

        create table navigation_items (
            id integer not null primary key,
            menu integer not null,
            title text not null,
            url varchar(255) not null,
            order_num integer default 0,
            foreign key(menu) references navigation_menus(id) 
            on delete cascade on update cascade
        );

        create index navigation_menuindex ON navigation_items(menu);
        '''
        self.cursor.executescript(query)


    def gather_menu_names(self):
        config_manager = ConfigManager()
        nav_config = config_manager.get(u'theme_navigation')
        config_manager.done()

        result = map(lambda x: x.strip(), nav_config.split(','))

        result = tuple(set(result))
        result = map(lambda x: (x,), result)
        if result:
            self.cursor.execute(u'delete from navigation_menus')
            self.connection.commit()
            query = u'insert into navigation_menus(name) values(?)'
            self.cursor.executemany(query, result)
            self.connection.commit()
        return True


    def get_all_menu_names(self):
        query = 'select * from navigation_menus order by id'
        self.cursor.execute(query)
        rows = list(self.cursor)
        if rows:
            return rows

        return []


    def add_item(self, menu_id, title, url, order_num):
        if not isinstance(order_num, (int, long)):
            return False

        query = 'insert into navigation_items(menu, title, url, order_num) \
        values ((select id from navigation_menus where id=?), ?, ?, ?)'
        try:
            self.cursor.execute(query, (menu_id, title, url, order_num))
            self.connection.commit()
        except:
            return False

        return True


    def remove_item(self, item_id):
        if not isinstance(item_id, (int, long)):
            return False

        query = 'delete from navigation_items where id=?'
        self.cursor.execute(query, (item_id,))
        self.connection.commit()
        return True


    def edit_item(self, item_id, item):
        '''
        item - tuple (title, url, order_num)
        '''
        if not isinstance(item_id, (long, int)):
            return False

        if not isinstance(item, tuple):
            return False

        if item.__len__() != 4:
            return False

        query = 'update navigation_items set menu=?, title=?, url=?, order_num=? where id=?'
        try:
            self.cursor.execute(query, item + (item_id,))
            self.connection.commit()
        except:
            return False

        return True


    def update_item(self, item_id, menu_id, order_num):
        if not isinstance(item_id, (int, long)):
            return False

        query = 'update navigation_items set menu=(select id from \
            navigation_menus where name=?), order_num=? where id=?'
        try:
            self.cursor.execute(query, (menu_id, order_num, item_id))
            self.connection.commit()
        except:
            return False

        return True


    def get_menu(self, menu_name):
        query = 'select * from navigation_items where menu=(select id from \
            navigation_menus where name=?) order by order_num'
        self.cursor.execute(query, (menu_name,))
        return list(self.cursor)


    def check_item_id(self, item_id):
        if not isinstance(item_id, (int, long)):
            return False

        query = 'select id from navigation_items where id=?'
        self.cursor.execute(query, (item_id,))
        result = list(self.cursor)
        if result:
            return result[0][0]

        return None


    def get_items(self):
        self.cursor.execute('select i.id, m.name, i.title, i.url, \
            i.order_num, m.id from navigation_items i inner join \
            navigation_menus m on i.menu=m.id order by i.menu, i.order_num')
        return list(self.cursor)

class Translator(object):

    def __init__(self, *args, **kwargs):
        super(Translator, self).__init__(*args, **kwargs)
        self.grant_type ='client_credentials'
        self.scope = 'http://api.microsofttranslator.com'
        self.auth = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'
        self.gate_url = ''
        self.access_token = None
        self.auth_header = None


    def get_auth_key(self, client_id, client_secret):
        auth_params = urllib.urlencode({
            'grant_type': self.grant_type,
            'scope': self.scope,
            'client_id' : client_id,
            'client_secret' : client_secret
        })
        try:
            resp = urllib2.urlopen(self.auth, auth_params)
            resp_json = json.loads(resp.read())
        except:
            return False

        self.access_token = resp_json['access_token']
        self.auth_header = {
            "Authorization": "Bearer %s" % self.access_token,
            'Content-Type' : 'text/plain'
        }
        return True


    def translate(self, cid, client_secret, text, from_lang='', to_lang='en'):
        if not self.get_auth_key(cid, client_secret):
            return None

        translate_params = urllib.urlencode({
            'text': text,
            'from': from_lang,
            'to': to_lang
        })
        url = 'http://api.microsofttranslator.com/V2/Http.svc/Translate?%s' 
        req = urllib2.Request(url % translate_params, None, self.auth_header)

        try:
            rep = urllib2.urlopen(req)
            response_text = rep.read()
        except:
            return None

        return response_text[68:-9]

class PageManager(SqliteManager):

    def __init__(self, *args, **kwargs):
        super(PageManager, self).__init__(*args, **kwargs)
        self.extention = '.html'


    def install(self):
        query = '''
        drop table if exists pages;

        create table pages (
            id integer not null primary key,
            name varchar(75) not null,
            title varchar(125) not null,
            content text not null,
            created_on datetime null,
            updated_on datetime,
            status varchar(3) default 'off' not null
        );

        create trigger pages_created_trigger after insert on pages
        begin
            update pages set created_on = datetime('now')  where id = new.id;
        end;

        create trigger pages_updated_trigger after update on pages
        begin
            update pages set updated_on = datetime('now') where id = old.id;
        end;
        '''
        self.cursor.executescript(query)


    def create(self, page):
        '''
        page - tuple of tuples (field, value)
        '''
        if not self.valid_tuple('pages', page):
            return None

        column_names = ', '.join(['"{0}"'.format(name) for name, _ in page])
        holders = ', '.join(['?' for i in xrange(page.__len__())])
        values = map(lambda x: x[1], page)

        query = 'insert into pages(%s) values(%s)' % (column_names, holders)

        self.cursor.execute(query, values)
        self.connection.commit()
        result = self.cursor.lastrowid

        filtered = filter(lambda x:x[0] == 'name' , page)
        if filtered.__len__() > 0 and filtered[0][1]:
            return result

        else:
            query = 'update pages set name=? where id=?'
            name = 'page-{0}'.format(result)
            self.cursor.execute(query, (name, result))
            self.connection.commit()
            return result


    def edit(self, page_id, page):
        if not isinstance(page_id, (int, long)):
            return False

        if not self.valid_tuple('pages', page):
            return False

        holders = ', '.join(['"%s"=?' % name for name, _ in page])
        values = map(lambda x: x[1], page)
        values.append(page_id)

        query = 'update pages set %s where id=?' % holders
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
        except:
            return False

        filtered = filter(lambda x:x[0] == 'name' , page)
        if filtered.__len__() == 0 or not filtered[0][1]:
            query = 'update pages set name=? where id=?'
            name = 'page-%s' % page_id
            self.cursor.execute(query, (name, page_id))
            self.connection.commit()
        return True


    def remove(self, page_id):
        if not isinstance(page_id, (int, long)):
            return False

        query = 'delete from pages where id=?'
        self.cursor.execute(query, (page_id,))
        self.connection.commit()
        return True


    def get(self, page_id):
        if not isinstance(page_id, (int, long)):
            return False
        query = 'select * from pages where id=?'
        self.cursor.execute(query, (page_id,))
        result = list(self.cursor)
        if result:
            return result[0]

        return None


    def list(self, page=1, active_only=False):
        if page == 0:
            offset = 0
            limit = 100
        else:
            offset = (page - 1) * self.items_per_page
            limit = self.items_per_page

        if active_only:
            query = 'select * from pages where status="on" limit ? offset ?'
        else:
            query = 'select * from pages limit ? offset ?'
        self.cursor.execute(query, (limit, offset))
        return list(self.cursor)


    def show(self, name):
        query = 'select * from pages where name=? and status="on"'
        self.cursor.execute(query, (name,))
        result = list(self.cursor)
        if result:
            return result[0]

        return None


class CatalogManager(SqliteManager):

    def __init__(self, *args, **kwargs):
        super(CatalogManager, self).__init__(*args, **kwargs)


    def install(self):
        query = '''
        drop table if exists catalog_items;

        drop table if exists catalog_categories;

        create table catalog_categories(
            id integer not null primary key,
            name varchar(35) not null unique on conflict ignore,
            amount integer not null default 0,
            created_on datetime,
            updated_on datetime
        );

        create trigger category_crt_trigger after insert on catalog_categories
        begin
            update catalog_categories set created_on = datetime('now') where id = new.id;
        end;

        create trigger category_upd_trigger after update on catalog_categories
        begin
            update catalog_categories set updated_on = datetime('now') where id = old.id;
        end;
        '''
        self.cursor.executescript(query)



    def exist(self):
        result = 0
        q = "select name from sqlite_master where name='catalog_items'"
        self.cursor.execute(q)
        if list(self.cursor):
            result += 1

        q = "select name from sqlite_master where name='catalog_categories'"
        self.cursor.execute(q)
        if list(self.cursor):
            result += 1

        if result == 2:
            return True

        return False


    def empty(self):
        self.cursor.execute("select * from catalog_categories limit 1")
        if list(self.cursor):
            return False
        self.cursor.execute("select * from catalog_items limit 1")
        if list(self.cursor):
            return False
        return True


    def create_items_table(self, schema):
        '''
        schema - set of tuples (field_name, field_type)
        schema don't include: id, images, category, active
        field_type = [S|M|B] (single line or multiple lines or choiche field)
        '''
        if not isinstance(schema, (tuple, list)):
            return None

        query = 'drop table if exists catalog_items;'

        query += 'create table catalog_items \
        (id integer not null primary key, category integer, images text, '

        for field_name, field_type in schema:
            check = re.match(r'[\w\d\s-]{1,75}', field_name, re.UNICODE)
            if not check:
                return None

            if field_type == 'S':
                query += '"%s" %s, ' % (field_name, 'varchar(75)')
            if field_type == 'M':
                query += '"%s" %s, ' % (field_name, 'text')
            if field_type == 'B':
                query += '"%s" %s, ' % (field_name, 'integer')

        query += 'active integer default 1,'
        query += 'created_on datetime, updated_on datetime,'
        query += "foreign key(category) references catalog_categories(id) \
        on delete cascade on update cascade);"
        self.cursor.executescript(query)

        query = '''
        create index catalog_categoryindex on catalog_items(category);

        create trigger catalog_items_ins_trigger after insert on catalog_items
        begin
            update catalog_categories set amount = amount + 1 where id = new.category;
            update catalog_items set created_on = datetime('now') where id = new.id;
        end;

        create trigger catalog_items_upd_trigger after update of category \
        on catalog_items begin
            update catalog_categories set amount = amount + 1 where id = new.category;
            update catalog_categories set amount = amount - 1 where id = old.category;
            update catalog_items set updated_on = datetime('now') where id = old.id;
        end;

        create trigger catalog_items_del_trigger after delete on catalog_items
        begin
            update catalog_categories set amount = amount - 1 where id = old.category;
        end;
        '''
        self.cursor.executescript(query)


    def item_fields(self):
        self.cursor.execute('pragma table_info(catalog_items)')
        return list(self.cursor)


    def add_item(self, item):
        '''
        item - set of tuples (field, value)
        '''
        if not self.valid_tuple('catalog_items', item):
            return None

        column_names = ', '.join(['"{0}"'.format(name) for name, _ in item])
        holders = ', '.join(['?' for i in xrange(item.__len__())])
        values = map(lambda x: x[1], item)

        query = 'insert into catalog_items(%s) values(%s)'

        self.cursor.execute(query % (column_names, holders), values)
        self.connection.commit()
        return self.cursor.lastrowid


    def edit_item(self, item_id, item):
        '''
        item - set of tuples (field, value)
        '''
        if not isinstance(item_id, (int, long)):
            return False

        if not self.valid_tuple('catalog_items', item):
            return False

        holders = ', '.join(['"{0}"=?'.format(name) for name, _ in item])
        values = map(lambda x: x[1], item)
        values.append(item_id)

        query = 'update catalog_items set ' + holders + ' where id=?'
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
        except:
            return False
        return True


    def get_item(self, item_id, field_name=None):
        '''
        field_name - optional field name of item (will be return)
        '''
        if not isinstance(item_id, (int, long)):
            return False

        if field_name:
            self.cursor.execute('pragma table_info(catalog_items)')
            columns = self.cursor.fetchall()
            field_names = map(lambda x: x[1], columns)
            field_names.remove('id')

            if field_name not in field_names:
                return False

            holder = '"%s"' % field_name
        else:
            holder = '*'

        query = 'select %s from catalog_items where id=?' % holder
        self.cursor.execute(query, (item_id,))

        desc = self.cursor.description
        query_result = list(self.cursor)
        result = []
        if not query_result:
            return False

        for i, column_desc in enumerate(desc):
            column_name = column_desc[0]
            value = query_result[0][i]

            if column_name == 'category':
                category = self.get_category(value)
                if category:
                    value = category[1]
                else:
                    value = None

            elif column_name == 'images':
                value = json.loads(value)

            elif column_name == 'active':
                value = True if value else False

            result.append((column_name, value))
        return result


    def get_item_images(self, item_id):
        if not isinstance(item_id, (int, long)):
            return False

        query = 'select images from catalog_items where id=?'
        self.cursor.execute(query, (item_id,))
        result = list(self.cursor)
        if result:
            return result[0]

        return None


    def acvivate_item(self, item_id, activate = True):
        if not isinstance(item_id, (int, long)):
            return False

        if activate:
            query = 'update catalog_items set active=1 where id=?'
        else:
            query = 'update catalog_items set active=0 where id=?'
        self.cursor.execute(query, (item_id,))
        self.connection.commit()
        return True


    def remove_item(self, item_id):
        if not isinstance(item_id, (int, long)):
            return False

        query = 'select id, category from catalog_items where id=?'
        self.cursor.execute(query, (item_id,))
        row = list(self.cursor)
        if row:
            query = 'delete from catalog_items where id=?'
            self.cursor.execute(query, (item_id,))
            self.connection.commit()
            return True

        return False


    def create_category(self, name):
        query = 'insert into catalog_categories(name, amount) values(?, 0)'
        self.cursor.execute(query, (name,))
        self.connection.commit()
        return self.cursor.lastrowid


    def edit_category(self, category_id, category):
        '''
        category - set of tuples (field, value)
        '''
        if not isinstance(category_id, (int, long)):
            return False

        if not self.valid_tuple('catalog_categories', category):
            return False

        placeholders = ', '.join(['"%s"=?' % name for name, _ in category])
        values = map(lambda x: x[1], category)
        values.append(category_id)

        query = 'update catalog_categories set ' + placeholders + ' where id=?'
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
        except:
            return False

        return True


    def get_category(self, category_id):
        if not isinstance(category_id, (int, long)):
            return False

        query = 'select * from catalog_categories where id=?'
        self.cursor.execute(query, (category_id,))
        result = list(self.cursor)
        if not result:
            return False

        return result[0]


    def category_list(self):
        query = 'select id, name from catalog_categories order by id'
        self.cursor.execute(query)
        return list(self.cursor)


    def remove_category(self, category_id):
        if not isinstance(category_id, (int, long)):
            return False

        query = 'delete from catalog_categories where id=?'
        self.cursor.execute(query, (category_id,))
        self.connection.commit()
        return True


    def catalog_map(self):
        '''
        query result row - 
        type({'c': "category", 'i': "item"}), id, parent(null or id)
        '''

        query = '''
        select "c" as type, id, null as parent, \
        ifnull(updated_on, created_on) as lastmod from catalog_categories union
        select "i" as type, id, category, ifnull(updated_on, created_on) \
        as lastmod from catalog_items where active=1 order by type, parent
        '''
        self.cursor.execute(query)

        while True:
            rows = self.cursor.fetchmany(100)
            if not rows:
                break
            for row in rows:
                yield row


    def browse(self, category=None, active_only=True, page=1):
        offset = (page - 1) * self.items_per_page

        field_names = map(lambda x: x[1], self.item_fields())

        if category:
            result_categories = []
            if active_only:
                query = 'select * from catalog_items where active=1 and \
                category=? order by id limit ? offset ?'
            else:
                query = 'select * from catalog_items where category=? \
                order by id limit ? offset ?'
            self.cursor.execute(query, (category, self.items_per_page, offset))
            result_items = zip(field_names, list(self.cursor))
            return (result_categories, result_items)

        if active_only:
            query = 'select id, "category" as value from catalog_categories \
            union select id, "item" as value from catalog_items where \
            active=1 and category is null order by value, id limit ? offset ?'
        else:
            query = 'select id, "category" as value from catalog_categories \
            union select id, "item" as value from catalog_items where \
            category is null order by value, id limit ? offset ?'
        self.cursor.execute(query, (self.items_per_page, offset))
        rows = list(self.cursor)

        pk_categories = []
        pk_items = []

        if rows:
            for row in rows:
                if row[1] == "category":
                    pk_categories.append(row[0])
                if row[1] == "item":
                    pk_items.append(row[0])

        holder = '?'
        holders = ', '.join(holder for unused in pk_categories)

        query = 'select * from catalog_categories where id in (%s) order by id'
        self.cursor.execute(query % holders, pk_categories)
        result_categories = list(self.cursor)

        holder = '?'
        holders = ', '.join(holder for unused in pk_items)

        query = 'select * from catalog_items where id in (%s) order by id'
        self.cursor.execute(query % holders, pk_items)

        result_items = map(lambda x: zip(field_names, x), \
            self.cursor.fetchall())

        return (result_categories, result_items)


class UploadedManager(SqliteManager):

    def __init__(self, *args, **kwargs):
        super(UploadedManager, self).__init__(*args, **kwargs)


    def install(self):
        query = 'drop table if exists uploaded;'
        query += '''create table uploaded (
            hash varchar(64) not null primary key,
            size integer not null,
            name varchar(64) not null
        );'''
        self.cursor.executescript(query)


    def count_images(self):
        self.cursor.execute("select count(*) from uploaded")
        result = list(self.cursor)
        if result:
            return result[0][0]

        return 0


    def remove_image(self, name):
        query = "delete from uploaded where name=?"
        self.cursor.execute(query, (name,))
        self.connection.commit()
        return True


    def get_image_name(self, h, size):
        query = 'select name from uploaded where hash=? and size=?'
        self.cursor.execute(query, (h, size))
        result = list(self.cursor)
        if result:
            return result[0][0]

        return None


    def add_image(self, h, size, name):
        query = 'insert into uploaded(hash, size, name) values(?,?,?)'
        self.cursor.execute(query, (h, size, name))
        self.connection.commit()
        return True


# set global settings

config_manager = ConfigManager()
if config_manager.exists():
    # MANAGER_URL always must be end with slash (only [a-zA-Z0-9_-])
    THEME = config_manager.get('theme', empty='default')
    SITE_NAME = config_manager.get('sitename')
    LOGO_USED = config_manager.get('theme_use_logo', empty='')
    LOGO = config_manager.get('theme_logo', empty='')
    MANAGER_URL = config_manager.get('manager_url', empty='/manager/')
    SITEDESC_SHORT = config_manager.get('short_description', empty='')
    SITEDESC = config_manager.get('description', empty='')
    KEYWORDS = config_manager.get('keywords', empty='')
    EMAIL = config_manager.get('connect_email', empty='')

    catalog_enabled = config_manager.get('catalog_enabled', '0')
    catalog = CatalogManager()
    catalog_exist = catalog.exist()
    catalog.done()
    if catalog_enabled == '1' and catalog_exist:
        CATALOG_ENABLED = 1
    else:
        CATALOG_ENABLED = 0

    connect_enabled = config_manager.get('connect_enabled', '0')
    if connect_enabled == '1':
        CONNECT_ENABLED = 1
    else:
        CONNECT_ENABLED = 0
    config_manager.done()
