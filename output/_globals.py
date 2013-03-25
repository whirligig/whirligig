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
# template inclusion tags
#
import re
import core
import files
import protection
import _filters

variableCollection = {
    'THEME': core.THEME,
    'LOGO': 'logo.png',
    'LOGO_USED': core.LOGO_USED,
    'SITENAME': core.SITE_NAME,
    'SITEDESC': core.SITEDESC,
    'SITEDESC_SHORT': core.SITEDESC_SHORT,
    'KEYWORDS': core.KEYWORDS,
    'MANAGER_URL': core.MANAGER_URL,
    'CATALOG_ENABLED': core.CATALOG_ENABLED,
    'CONNECT_ENABLED': core.CONNECT_ENABLED
}

def is_auth(request):
    auth = protection.CookieAuthenticator()
    if auth.valid_auth(request['headers']):
        return True

    return False


def inc(i1, i2=1):
    return i1 + i2


def no_image(size):
    return files.no_image(size)


def groups(value, linecount, fill_with=None):
    result = []
    tmp = []
    for item in value:
        if len(tmp) == linecount:
            yield tmp

            tmp = []
        tmp.append(item)
    if tmp:
        if fill_with is not None and len(tmp) < linecount:
            tmp += [fill_with] * (linecount - len(tmp))
        yield tmp


def do_slice(value, slices, fill_with=None):
    seq = list(value)
    length = len(seq)
    items_per_slice = length // slices
    slices_with_extra = length % slices
    offset = 0
    for slice_number in xrange(slices):
        start = offset + slice_number * items_per_slice
        if slice_number < slices_with_extra:
            offset += 1
        end = offset + (slice_number + 1) * items_per_slice
        tmp = seq[start:end]
        if fill_with is not None and slice_number >= slices_with_extra:
            tmp.append(fill_with)
        yield tmp


def do_batch(value, linecount, fill_with=None):
    result = []
    tmp = []
    for item in value:
        if len(tmp) == linecount:
            yield tmp

            tmp = []
        tmp.append(item)
    if tmp:
        if fill_with is not None and len(tmp) < linecount:
            tmp += [fill_with] * (linecount - len(tmp))
        yield tmp


def range(start, stop, step):
    return xrange(start, stop, step)


def equal(left, right):
    if left == right:
        return True

    return False


def not_equal(left, right):
    return not equal(left, right)


def manager_nav(request):
    o = '<ul class="menu manager-nav">'
    o += '<li %s><a href="%s">Dashboard</a></li>' % (
        'class="active"' if request.get('path', '') == core.MANAGER_URL else '',
        core.MANAGER_URL
    )
    o += '<li %s><a href="%ssettings/">Settings</a></li>' % (
        'class="active"' if request.get('path', '') == core.MANAGER_URL + 'settings/' else '',
        core.MANAGER_URL
    )
    o += '<li %s><a href="%spages/">Pages</a></li>' % (
        'class="active"' if request.get('path', '') == core.MANAGER_URL + 'pages/' else '',
        core.MANAGER_URL
    )
    o += '<li %s><a href="%snav/">Navigation</a></li>' % (
        'class="active"' if request.get('path', '') == core.MANAGER_URL + 'nav/' else '',
        core.MANAGER_URL
    )
    o += '<li %s><a href="%scatalog/">Catalog</a></li>' % (
        'class="active"' if request.get('path', '') == core.MANAGER_URL + 'catalog/' else '',
        core.MANAGER_URL
    )
    o += '<li><a href="%slogout/">Logout</a></li>' % core.MANAGER_URL
    return o


def static_page_layouts(items, columns=5):
    o = '<div class="columnwrapper block">'
    for column in do_slice(items,columns):
        o += '<ul class="column">'
        for item in column:
            o += '<li><div class="layout_name">%s</div>' % (item.keys()[0])
            o += '<div class="layout_img">%s</div></li>' % (item.values()[0])
        o += '</ul>'
    o += '</div>'
    return o


def property_types_select():
    o = '''<select name="container" class="property_container">
    <option value="S">Single line</option>
    <option value="M">Multiple lines</option>
    <option value="B">Yes / No</option>
    </select>'''
    return o


def category_row(category):
    o = '<td class="first">'
    o += '<input type="hidden" name="pk" value="%s" />' % (category[0])
    o += '<div><span class="category_name">%s</span>' % (category[1])
    o += '<ul><li>Items: <span>%s</span></li></ul></div>' % (category[2])
    o += '</td><td class="last"><div>'
    o += '<ul class="category_meta block">'
    o += '<li class="view">Browse</li>'
    o += '<li class="add">+ item</li>'
    o += '<li class="rename">Rename</li>'
    o += '<li class="delete">Delete</li></ul>'
    o += '</div></td>'
    return o


def item_row(item):
    o = '<td class="first"><div>%s</div></td>' % (item[0])
    o += '<td class="img70_cell"><div><img src="%s" alt="" title="" /></div>\
    </td>' % _filters.get_mini_image(item[1])

    o += '<td><div>%s</div></td>' % item[3]
    o += '<td class="last"><div>'
    o += '<ul class="item_meta block">'
    o += '<li class="view">View</li>'
    o += '<li class="edit">Edit</li>'
    o += '<li class="activate">Hide</li>'
    o += '<li class="delete">Delete</li>'
    o += '</ul></div></td>'
    return o


def catalog_navigation(catalog, current_page):
    o = '''<div class="catalog-nav">
<input type="hidden" name="page" value="%s" />
<input type="hidden" name="category" value="" />
<input type="button" name="catalog_prev" class="form-submit" value="Prev" />
<input type="text" name="catalog_page" class="form-text" value="%s" size="3" />
<input type="button" name="go" class="form-submit" value="Go" />
<input type="button" name="catalog_next" class="form-submit" value="Next" />
</div>''' % (current_page, current_page)
    return o


def categories_table(catalog, page):
    o = '''<table><thead><tr><th class="first">Category</th>
    <th class="last">Actions</th></tr></thead><tbody>'''

    if catalog[0]:
        for i, categ in enumerate(catalog[0]):
            o += '''<tr class="%s"><td class="first">
            <input type="hidden" name="pk" value="%s" />
            <div><span class="category_name">%s</span>
            <ul><li>Items: <span>%s</span></li></ul></div></td>
            <td class="last"><div>
            <ul class="category_meta block">
            <li class="view">Browse</li>
            <li class="add">+ item</li>
            <li class="rename">Rename</li>
            <li class="delete">Delete</li></ul></div></td></tr>
            ''' % ('odd' if i & 1 else 'even', categ[0], categ[1], categ[2])
    else:
        o += '''<tr><td colspan="2" class="center first last done">
        There are no categories</td></tr>'''
    o += '</tbody></table>'
    return o


def items_table(catalog, page):
    o = '''<table><thead><tr><th class="first">&#x2116;</th><th>Image</th>
    <th>Item</th><th class="last">Actions</th></tr></thead><tbody>'''

    row = '''<tr class="%s%s"><td class="first"><div>%s</div></td>
<td class="img70_cell"><div><img src="%s" alt="" title="" /></div></td>
<td><div>%s</div></td><td class="last"><div><ul class="item_meta block">
<li class="view">View</li><li class="edit">Edit</li>
<li class="activate">%s</li>
<li class="delete">Delete</li></ul></div></td></tr>'''

    if catalog[1]:
        for i, item in enumerate(catalog[1]):
            o += row % (
                'odd' if i & 1 else 'even',
                ' h' if item[-3][1] == 0 else '',
                item[0][1], _filters.get_mini_image(_filters.main_image(item)),
                item[3][1], 'Show' if item[-3][1] == 0 else 'Hide'
            )
    else:
        o += '''<tr><td colspan="4" class="center first last done">
        There are no items</td></tr>'''
    o += '</tbody></table>'
    return o


def empty_table():
    o = '''<table><thead><tr><th class="first last"></th></tr></thead>
    <tbody><tr><td class="center first last done">There are no items</td></tr>
    </tbody></table>'''
    return o


def print_time_token():
    o = '<input type="hidden" name="token" value="%s" />'
    return o % protection.set_server_token()


def print_menu(name, request=None):
    nav = core.NavigationManager()
    rows = nav.get_menu(name)
    nav.done()
    html = ''
    if rows:
        html = '<ul class="menu %s-nav">' % name
        if request:
            for row in rows:
                label = row[2]
                href = row[3]
                # check for static page name
                if re.match(r'^[a-z0-9\-]+$', href):
                    href = '/{0}.html'.format(href)

                if (request['path'].startswith(href) and href != '/') or \
                request['path'] == href:
                    html += '<li class="active"><a href="%s">%s</a>\
                    </li>' % (href, label)
                else:
                    html += '<li><a href="%s">%s</a></li>' % (href, label)
        else:
            for row in rows:
                label = row[2]
                href = row[3]
                if re.match(r'^[a-z0-9\-]+$', href):
                    href = '/{0}.html'.format(href)
                html += '<li><a href="%s">%s</a></li>' % (href, label)
        html += '</ul>'
    return html


def connect_form():
    o = '''<div class="connect-form">
    <form action="" method="post">
    <input type="hidden" name="token" value="%s" />
    <table>
    <tr><td><input type="text" name="sender" value="Name" /></td></tr>
    <tr><td><input type="text" name="email" value="E-mail" /></td></tr>
    <tr><td><textarea name="message">Message</textarea></td></tr>
    <tr><td><input type="submit" name="submit" value="Send" /></td></tr>
    </table></form></div>''' % protection.set_server_token()
    return o


def theme_screenshots(theme):
    folder = theme[0]
    screenshots = files.get_theme_screenshots(folder)

    o = '''<table class="screenshots"><tr>
    <td><img src="{0}" alt="Front page" title="Front page" /></td>
    <td><img src="{1}" alt="Static page" title="Static page" /></td>
    <td><img src="{2}" alt="Catalog" title="Catalog" /></td>
    <td><img src="{3}" alt="Catalog category" title="Catalog category" /></td>
    <td><img src="{4}" alt="Catalog item" title="Catalog item" /></td>
    <td><img src="{5}" alt="Connect" title="Connect" /></td>
    </tr></table>'''.format(*screenshots)

    return o