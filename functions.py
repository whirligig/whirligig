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

import json
import smtplib
import os
import re
import protection
import http
from output import html
import core
import files
import seo

#
# reload settings without restart server
# this function does not modify core.ROOT, core.MANAGER_URL
# and core.THEME variables
#
def reload_core():
    from output import _globals
    reload(core)
    reload(_globals)

CACHE = files.Cache()

# =================================
#          secure decorator
# =================================

def secure_page(func):
    def decorator(request, *args, **kwargs):
        auth = protection.CookieAuthenticator()
        if not auth.valid_auth(request['headers']):
            return http.redirect('%slogin/' % core.MANAGER_URL)
        return func(request, *args, **kwargs)
    return decorator


# ------- configuration edit ---------

@secure_page
def manager_config(request):
    config = {}
    config_manager = core.ConfigManager()
    config['sitename'] = config_manager.get('sitename', '')
    no_image = '/manager/static/no-image-70.png'
    config['logo'] = config_manager.get('logo', no_image)
    config['short_description'] = config_manager.get('short_description', '')
    config['description'] = config_manager.get('description', '')
    config['keywords'] = config_manager.get('keywords', '')
    config['translator_cid'] = config_manager.get('translator_cid', '')
    config['translator_secret'] = config_manager.get('translator_secret', '')
    config['connect_email'] = config_manager.get('connect_email', '')
    config['smtp_host'] = config_manager.get('smtp_host', '')
    config['smtp_port'] = config_manager.get('smtp_port', '')
    config['smtp_login'] = config_manager.get('smtp_login', '')
    config['smtp_password'] = config_manager.get('smtp_password', '')
    config['catalog_enabled'] = config_manager.get('catalog_enabled', 0)
    config['connect_enabled'] = config_manager.get('connect_enabled', 0)
    config_manager.done()

    template = 'manager/templates/settings.tpl'
    return http.html_page(template, {'config': config}, request)


@secure_page
def manager_config_post(request):
    variables = request['variables']
    config = {}

    sitename = variables.get('sitename', '').strip()
    logo = variables.get('logo', None)
    short_description = variables.get('short_description', '').strip()
    description = variables.get('description', '').strip()
    keywords = variables.get('keywords', '').strip()
    translator_cid = variables.get('translator_cid', '').strip()
    translator_secret = variables.get('translator_secret', '').strip()
    catalog_enabled = variables.get('catalog_enabled', '').strip()
    connect_enabled = variables.get('connect_enabled', '').strip()
    connect_email = variables.get('connect_email', '').strip()

    host = variables.get('smtp_host').strip()
    port = variables.get('smtp_port').strip()
    login = variables.get('smtp_login').strip()
    password = variables.get('smtp_password').strip()

    config_manager = core.ConfigManager()
    config_manager.set('sitename', sitename)

#    if logo:
#        saved_logo = files.save_logo(logo)
    #     uploaded.done()
    #     if saved_image:
    #         logo_url = files.get_mini_image(saved_image)
    #         config_manager.set(u'logo', logo_url)
    # else:
    #     config_manager.set(u'logo', 'logo.png')

    config_manager.set('short_description', short_description)
    config_manager.set('description', description)
    config_manager.set('keywords', keywords)
    config_manager.set('translator_cid', translator_cid)
    config_manager.set('translator_secret', translator_secret)
    config_manager.set('connect_email', connect_email)

    config_manager.set('smtp_host', host)
    config_manager.set('smtp_port', port)
    config_manager.set('smtp_login', login)
    config_manager.set('smtp_password', password)

    if catalog_enabled == 'on':
        config_manager.set('catalog_enabled', 1)
    else:
        config_manager.set('catalog_enabled', 0)

    if connect_enabled == 'on':
        config_manager.set('connect_enabled', 1)
    else:
        config_manager.set('connect_enabled', 0)

    config_manager.done()

    CACHE.clear()
    reload_core()

    return manager_config(request)


@secure_page
def manager_config_logo_delete(request):
    variables = request['variables']
    action = variables.get('action', 'error')
    if action == 'delete' and files.delete_logo():
        CACHE.clear()
        return http.text_data('success')
    return http.text_data('error')


# -------------- SEO -----------------

@secure_page
def manager_seo_sitemap(request):
    variables = request['variables']
    action = variables.get('action')
    if action == 'create':
        seo.create_sitemap(request)
        return http.text_data('created')
    return http.text_data('error')


# --------- catalog edit -------------

@secure_page
def manager_catalog(request, page=1):
    template = 'manager/templates/catalog.tpl'

    catalog = core.CatalogManager()
    if not catalog.exist():
        catalog.done()
        context = {'catalog': (), 'page': page, 'exist': False}
        return http.html_page(template, context, request)

    if catalog.empty():
        catalog.done()
        context = {'catalog': (), 'page': page, 'exist': True}
        return http.html_page(template, context, request)

    result = catalog.browse(category=None, page=1)
    catalog.done()

    if len(result[0]) == 0 and len(result[1]) == 0:
        context = {'catalog': (), 'page': page, 'exist': True}
        return http.html_page(template, context, request)

    context = {'catalog': result, 'page': page, 'exist': True}
    return http.html_page(template, context, request)


@secure_page
def manager_catalog_listing(request):
    template = 'manager/templates/catalog_rows.tpl'

    variables = request['variables']
    category = variables.get('category', 0)
    page = variables.get('page', 1)

    try:
        category = int(category)
        page = int(page)
    except:
        category = 0
        page = 1

    if category < 1:
        category = 0
    if page < 1:
        page = 1

    catalog = core.CatalogManager()
    result = catalog.browse(category=category, page=page)
    catalog.done()
    context = {'catalog': result, 'page': page}
    return http.html_page(template, context, request)


@secure_page
def manager_catalog_category_action(request):
    template = 'manager/templates/catalog_rows.tpl'

    variables = request['variables']
    catalog = core.CatalogManager()

    if not catalog.exist():
        catalog.done()
        return http.text_data('error')

    action = variables.get('action', None)
    name = variables.get('name', None)
    pk = variables.get('pk', None)

    if action == 'browse' and pk:
        try:
            pk = int(pk)
        except:
            catalog.done()
            return http.text_data('error')

        page = 1
        rows = catalog.browse(category=pk, page=1)
        catalog.done()
        context = {'catalog': rows, 'page': page}
        return http.html_page(template, context, request)

    if action == 'create' and name:
        if catalog.create_category(name) == 0:
            catalog.done()
            return http.text_data('error')

        page = 1
        rows = catalog.browse(category=None, page=1)
        catalog.done()
        context = {'catalog': rows, 'page': page}
        return http.html_page(template, context, request)

    if action == 'delete' and pk:
        try:
            pk = int(pk)
        except:
            catalog.done()
            return http.text_data('error')

        category = catalog.get_category(pk)
        pk = category[0]
        name = category[1]
        childrens = category[2]

        catalog.remove_category(pk)
        catalog.done()

        CACHE.clear()

        return http.json_data({'pk': pk, 'name': name, 'number': 0})

    if action == 'rename' and pk and name:
        try:
            pk = int(pk)
        except:
            catalog.done()
            return http.text_data('error')

        category = (
            (u'name', name),
        )

        if catalog.edit_category(pk, category):
            catalog.done()

            CACHE.clear()

            return http.json_data({'pk': pk, 'name': name})

    catalog.done()
    return http.text_data('error')


@secure_page
def manager_catalog_wizard_start(request):
    template = 'manager/templates/catalog_wizard_1.tpl'

    catalog = core.CatalogManager()
    if catalog.exist():
        catalog.done()
        return http.redirect('%scatalog/' % core.MANAGER_URL)

    catalog.done()
    return http.html_page(template, {}, request)


@secure_page
def manager_catalog_wizard_end(request):
    template = 'manager/templates/catalog_wizard_2.tpl'

    variables = request['variables']
    properties = variables.get('properties', None)
    data = []

    if properties is None:
        context = {'result': 'error', 'message': 100}
        return http.html_page(template, context, request)

    properties = json.loads(properties)

    for key in properties:
        name = key
        i = properties[key][0]
        value = properties[key][1]
        data.append((i, name, value))

    properties = []

    data.sort(key=lambda x: int(x[0]))

    for item in data:
        i = item[0]
        name = item[1]
        value = item[2]
        check = re.match(r'[\w\d\s-]{1,75}', name, re.UNICODE)
        if check:
            values = ['( Single line )', '( Multiple lines )', '( Yes / No )']
            if value in values:
                if value == values[0]:
                    properties.append((name, 'S'))
                if value == values[1]:
                    properties.append((name, 'M'))
                if value == values[2]:
                    properties.append((name, 'B'))

    if properties:
        catalog = core.CatalogManager()
        catalog.create_items_table(properties)
        catalog.done()

        context = {
            'result': 'created'
        }

        return http.html_page(template, context, request)

    context = {
        'result': 'error',
        'message': 101
    }

    return template(template, context, request)


@secure_page
def manager_catalog_image_upload(request):
    variables = request['variables']
    image = variables.get('image', None)
    if image:
        uploaded = core.UploadedManager()
        saved_image = files.save_uploaded_image(uploaded, image)
        uploaded.done()

        if saved_image:
            preview_url = files.get_small_image(saved_image)
            return http.text_data(preview_url)

    return http.text_data("error")


@secure_page
def clear_catalog_image(request):
    variables = request['variables']
    item = variables.get('item', 0)
    src = variables.get('src', None)

    if not src:
        return http.text_data('error')

    try:
        item = int(item)
    except:
        item = 0

    if item == 0:
        return http.text_data('error')

    catalog = core.CatalogManager()
    images = catalog.get_item_images(item)

    if not images:
        catalog.done()
        return http.text_data('error')

    candidat = os.path.basename(src)
    images = json.loads(images[0])

    if candidat == images['main']:
        if images['extra']:
            images['main'] = images['extra'].pop(0)
        else:
            images['main'] = ''

        core.edit_item()
        catalog.done()
        return http.text_data('deleted')

    if candidat in images['extra']:
        images['extra'].pop(images['extra'].index(candidat))
        core.edit_item(item, ('images', images))
        catalog.done()
        return http.text_data('deleted')

    catalog.done()
    return http.text_data('deleted')


@secure_page
def manager_catalog_add(request, added=False, item=None, cat=None, edit=None):
    template = 'manager/templates/catalog_add.tpl'

    catalog = core.CatalogManager()
    columns = catalog.item_fields()
    if not columns:
        catalog.done()
        return http.redirect('%scatalog/' % core.MANAGER_URL)

    properties = []
    categories = []

    try:
        cat = int(cat)
    except:
        cat = 0

    categories = catalog.category_list()
    catalog.done()

    r_names = (
        'id', 'category', 'images', 'active', 'created_on', 'updated_on'
    )

    radio_no = '<input type="radio" id="radio_no" name="%s" value="0" %s>'
    radio_yes = '<input type="radio" id="radio_yes" name="%s" value="1" %s>'
    line = '<input type="text" class="form-text" maxlength="75" name="%s" value="%s" />'
    text = '<textarea name="%s">%s</textarea>'

    for column in columns:
        pk = column[0]
        name = column[1]

        if name in r_names:
            continue

        if column[2] == 'integer':
            container = []
            if item and item[pk][1] == 1:
                container.append(radio_yes % (name, 'checked'))
                container.append(radio_no % (name, ''))
            else:
                container.append(radio_yes % (name, ''))
                container.append(radio_no % (name, 'checked'))

        if column[2] == 'varchar(75)':
            if item:
                container = line % (name, item[pk][1])
            else:
                container = line % (name, '')

        if column[2] == 'text':
            if item:
                container = text % (name, item[pk][1].replace('<br />', '\n'))
            else:
                container = text % (name, '')

        properties.append((name, container))

    context = {
        'properties': properties,
        'category': cat,
        'categories': categories,
        'added': added,
        'edit':edit,
        'item': item
    }

    return http.html_page(template, context, request)


@secure_page
def manager_catalog_add_data(request, item=None):
    variables = request['variables']
    catalog = core.CatalogManager()
    columns = catalog.item_fields()
    if not columns:
        catalog.done()
        return http.redirect('%scatalog/' % core.MANAGER_URL)

    properties = []

    r_names = (
        'id', 'category', 'images', 'active', 'created_on', 'updated_on'
    )

    for column in columns:
        name = column[1]
        column_type = column[2]

        if name in r_names:
            continue

        if column_type.lower() == 'integer':
            try:
                properties.append((name, int(request.POST.get(name, 0))))
            except:
                properties.append((name, 0))
        else:
            value = variables.get(name, '').replace('\n', '<br />')
            properties.append((name, value))

    category = variables.get('category', None)
    if category:
        try:
            category = int(category)
        except:
            category = None

    if category == 0:
        category = None

    images = variables.get('images', None)
    if images:
        images = json.loads(images)
    else:
        images = {}
        images['main'] = ''
        images['extra'] = []

    # security checks
    image_names = {}
    path = files.get_original_path(images['main'])
    if os.path.isfile(path):
        image_names['main'] = os.path.basename(path)
    extra_images = []
    for i in images['extra']:
        path = files.get_original_path(i)
        if os.path.isfile(path):
            extra_images.append(os.path.basename(path))

    image_names['extra'] = extra_images
    properties.append(('images', json.dumps(image_names)))
    properties.append(('category', category))
    properties.append(('active', 1))
    properties.append(('created_on', None))
    properties.append(('updated_on', None))

    if item:
        pk = item[0][1]
        if not catalog.edit_item(pk, properties):
            catalog.done()
            return manager_catalog_add(request, added=False)

        item = catalog.get_item(pk)
        catalog.done()

        CACHE.clear()

        return manager_catalog_add(request, added=False, item=item)

    last_id = catalog.add_item(properties)
    if not last_id:
        catalog.done()
        return manager_catalog_add(request, added=False)

    item = catalog.get_item(last_id)
    catalog.done()

    CACHE.clear()

    return manager_catalog_add(request, added=True, item=item)


@secure_page
def manager_catalog_edit(request):
    variables = request['variables']
    pk = variables.get('id', None)
    try:
        pk = int(pk)
    except:
        pk = None

    if not pk:
        return http.redirect('%scatalog/add/' % core.MANAGER_URL)

    catalog = core.CatalogManager()
    item = catalog.get_item(pk)
    catalog.done()

    if not item:
        return http.redirect('%scatalog/add/' % core.MANAGER_URL)

    return manager_catalog_add(request, added=False, item=item)


@secure_page
def manager_catalog_edit_data(request):
    variables = request['variables']
    pk = variables.get('id', None)
    try:
        pk = int(pk)
    except:
        pk = None

    if not pk:
        return http.redirect('%scatalog/add/' % core.MANAGER_URL)

    catalog = core.CatalogManager()
    item = catalog.get_item(pk)
    catalog.done()

    if not item:
        return http.redirect('%scatalog/add/' % core.MANAGER_URL)

    return manager_catalog_add_data(request, item=item)


@secure_page
def manager_catalog_activate(request):
    variables = request['variables']
    pk = variables.get('id', None)
    try:
        pk = int(pk)
    except:
        pk = None

    if not pk:
        return http.text_data('error')

    catalog = core.CatalogManager()
    item = catalog.get_item(pk)

    if not item:
        catalog.done()
        return http.text_data('error')

    if item[len(item)-3][1]:
        catalog.acvivate_item(pk, activate=False)
        catalog.done()

        CACHE.clear()

        return http.text_data('hide')
    else:
        catalog.acvivate_item(pk, activate=True)
        catalog.done()

        CACHE.clear()

        return http.text_data('active')


@secure_page
def manager_catalog_delete(request):
    variables = request['variables']
    pk = variables.get('id', None)
    try:
        pk = int(pk)
    except:
        pk = None

    if not pk:
        return http.text_data('error')

    catalog = core.CatalogManager()
    result = catalog.remove_item(pk)
    catalog.done()

    if not result:
        return http.text_data('error')

    CACHE.clear()

    return http.text_data('deleted')


def manager_catalog_add_to_category(request, category):
    return manager_catalog_add(request, \
        added=False, item=False, category=category)


def manager_catalog_add_to_category_post(request, category):
    return manager_catalog_add_data(request)


@secure_page
def manager_catalog_import(request):
    template = 'manager/templates/catalog_import.tpl'

    catalog = core.CatalogManager()
    if not catalog.exist():
        catalog.done()
        return http.redirect('%scatalog/' % core.MANAGER_URL)

    return http.html_page(template, {}, request)

# ------- static page edit -----------

def static_page_stuctures():
    items = []
    path = os.path.join(core.ROOT, "themes", core.THEME, "layouts")

    for name in os.listdir(path):
        item = {}

        if name[:7] == 'static_' and name[-4:] == '.png':
            layout_name = name[7:-4].replace('_', ' ')
            png_name = os.path.join(path, name)
            tpl_name = png_name[:-4] + '.tpl'

            if not os.path.isfile(tpl_name):
                continue

            try:
                png = open(png_name, 'r+b')
                data_uri = png.read().encode('base64').replace('\n', '')
                img_tag = '<img src="data:image/png;base64,%s">' % data_uri
                png.close()
            except:
                img_tag = '<img src="data:image/png;base64,">'
            item[layout_name] = img_tag
            items.append(item)
    return items


@secure_page
def image_upload(request):
    template = 'manager/templates/image_upload.tpl'

    variables = request['variables']
    data = variables.get('image', None)
    if data:
        uploaded = core.UploadedManager()
        saved_image = files.save_uploaded_image(uploaded, data)
        uploaded.done()
        if saved_image:
            preview_url = files.get_small_image(saved_image)
            context = {'url': preview_url}
            return http.html_page(template, context, request)

    return http.text_data("error")


@secure_page
def image_resize(request):
    variable = request['variables']
    name = variable.get('name', None)
    size = variable.get('size', None)
    if not (name and size):
        return http.text_data('error')

    if size == 'mini':
        thumbnail = files.get_mini_image(name)
        if thumbnail:
            return http.json_data('<img src="%s" alt="" title="">' % thumbnail)

    if size == 'small':
        thumbnail = files.get_small_image(name)
        if thumbnail:
            return http.json_data('<img src="%s" alt="" title="">' % thumbnail)

    if size == 'medium':
        thumbnail = files.get_medium_image(name)
        if thumbnail:
            return http.json_data('<img src="%s" alt="" title="">' % thumbnail)

    if size == 'big':
        thumbnail = files.get_big_image(name)
        if thumbnail:
            return http.json_data('<img src="%s" alt="" title="">' % thumbnail)

    return http.text_data('error')


@secure_page
def image_browse(request, page_pass=0):
    template = 'manager/templates/image_upload.tpl'

    amount = 18
    thumbnails = []
    prev = False
    next = False
    variables = request['variables']
    if page_pass:
        page = page_pass
    else:
        page = variables.get('page', 1)
        try:
            page = int(page)
        except:
            page = 1

    if page < 1:
        page = 1

    offset = (page - 1) * amount

    images = files.get_original_images(amount=amount, offset=offset)
    for name in images:
        image = files.get_mini_image(name)
        if image:
            thumbnails.append(image)

    uploaded = core.UploadedManager()
    uploaded_count = uploaded.count_images()
    uploaded.done()

    if (uploaded_count / amount) >= page:
        if (uploaded_count / amount) == page and not (uploaded_count % amount):
            next = False
        else:
            next = True

    if page > 1:
        prev = True

    context = {
        'images': thumbnails,
        'page': page,
        'prev': prev,
        'next': next,
        'url': None
    }

    return http.html_page(template, context, request)


@secure_page
def remove_uploaded_image(request):
    variables = request['variables']
    src = variables.get('src', None)
    page = variables.get('page', 1)
    try:
        page = int(page)
    except:
        page = 1
    if src:
        uploaded = core.UploadedManager()
        files.delete_image(uploaded, src)
        uploaded.done()
    return image_browse(request, page_pass=page)


@secure_page
def image_choice(request):
    template = 'manager/templates/image_upload.tpl'

    variables = request['variables']
    image = variables.get('image', None)
    if image:
        preview_url = files.get_small_image(image)

        context = {
            'url': preview_url
        }

        return http.html_page(template, context, request)

    return http.text_data('error')


@secure_page
def static_layout(request):
    variables = request['variables']
    action = variables.get('action', None)
    if action == 'load':
        name = variables.get('name', None)
        if name:
            tpl_template = "./themes/%s/layouts/static_%s.tpl"
            tpl_name = tpl_template % (core.THEME, name.replace(' ', '_'))

            if os.path.isfile(tpl_name):
                f = open(tpl_name, 'r+b')
                content = f.read()
                f.close()

                data = {
                    'content': content
                }

                return http.json_data(data)

    data = {
        'content': ''
    }

    return http.json_data(data)


@secure_page
def static_pages_url(request):
    variables = request['variables']
    text = variables.get('text', None)
    if not text:
        return http.text_data('error')
    if text.__len__() > 75:
        return http.text_data('error')

    if re.match(r'[a-zA-Z\-\_\d\s]+', text):
        result = text.lower()
    else:
        config = core.ConfigManager()
        cid = config.get('translator_cid')
        secret = config.get('translator_secret')
        config.done()

        result = core.Translator().translate(cid, secret, text)

        result = result.lower() if result else None

    result = re.sub(r'\W', '-', result) if result else ''

    return http.text_data(result)


@secure_page
def static_page_list(request, pagitation_page=1):
    template = 'manager/templates/static_page_list.tpl'

    pages = core.PageManager()
    page_page = pages.list(page=pagitation_page)
    pages.done()
    result = {}
    result['active'] = []
    result['hidden'] = []

    for p in page_page:
        if p[6] == 'on':
            result['active'].append(p)
        else:
            result['hidden'].append(p)

    context = {
        'pages': result
    }

    return http.html_page(template, context, request)



@secure_page
def static_pages_redirect(request):
    return http.redirect('%spages/' % core.MANAGER_URL)


@secure_page
def static_page_edit(request):
    template = 'manager/templates/static_page.tpl'

    variables = request['variables']
    pk = variables.get('pk', None)
    try:
        pk = int(pk)
    except:
        pk = 0

    pages = core.PageManager()
    page = pages.get(pk)
    pages.done()

    content = {}

    if page is None:
        content['pk'] = ''
        content['name'] = ''
        content['title'] = ''
        content['content'] = ''
        content['created'] = ''
        content['updated'] = ''
        content['status'] = ''
    else:
        content['pk'] = page[0]
        content['name'] = page[1]
        content['title'] = page[2]
        content['content'] = page[3]
        content['created'] = page[4]
        content['updated'] = page[5]
        content['status'] = page[6]

    layouts = static_page_stuctures()

    context = {
        'page': content,
        'layouts': layouts
    }

    return http.html_page(template, context, request)



@secure_page
def static_page_preview(request):
    template = 'static_page.tpl'

    variables = request['variables']
    content = {}
    content['name'] = ''
    content['title'] = ''
    content['content'] = variables.get('content', '')

    context = {
        'content': content
    }

    return http.html_page(template, context, request)



@secure_page
def static_page_save(request):
    variables = request['variables']
    pk = variables.get('pk', None)
    name = variables.get('name', '').strip()
    title = variables.get('title', '').strip()
    content = variables.get('content', '')
    status = variables.get('status', '').strip()

    try:
        pk = int(pk)
    except:
        pk = None

    page = (
        ('name', name),
        ('title', title),
        ('content', content),
        ('status', status),
    )

    pages = core.PageManager()

    if pk is None:
        pk = pages.create(page)
        pages.done()

        CACHE.clear()

        data = {
            'result': 'created',
            'pk': pk
        }

        return http.json_data(data)

    pages.edit(pk, page)
    pages.done()

    CACHE.clear()

    data = {
        'result': 'updated'
    }

    return http.json_data(data)



@secure_page
def static_page_delete(request):
    variables = request['variables']
    pk = variables.get('pk', None)
    try:
        pk = int(pk)
    except:
        pk = None

    if pk is not None:
        pages = core.PageManager()
        pages.remove(pk)
        pages.done()

        CACHE.clear()
	
    return http.redirect('%spages/' % core.MANAGER_URL)

# ------- navigation edit ------------

@secure_page
def manager_navigation_list(request):
    template = 'manager/templates/navigations_page.tpl'

    nav = core.NavigationManager()
    allitems = nav.get_items()
    menu_list = nav.get_all_menu_names()
    nav.done()
    items = {}

    options = []
    options.append(('/', 'Main page'))

    pages = core.PageManager()
    for i in pages.list():
        if (i[1], i[2]) not in options:
            options.append((i[1], i[2]))
    pages.done()

    if core.CATALOG_ENABLED:
        options.append(('/catalog/', 'Catalog'))
    if core.CONNECT_ENABLED:
        options.append(('/connect/', 'Message Form'))

    for item in allitems:
        if item[1] in items:
            items[item[1]].append(item)
        else:
            items[item[1]] = [item]

        if not [i for i in options if item[3] == i[0]]:
            options.append((item[3], item[3]))

    context = {
        'items': items,
        'menu_list': menu_list,
        'options': options
    }

    return http.html_page(template, context, request)


@secure_page
def manager_navigation_create(request):
    template = 'manager/templates/menu_list.tpl'

    variables = request['variables']
    menu_name = variables.get('menu_name', None)
    title = variables.get('title', None)
    url = variables.get('url', None)
    order_num = variables.get('order_num', None)

    if not menu_name or not title or not url or not order_num:

        data = {
            'error': 'All fields are required',
            'html': ''
        }

        return http.json_data(data)

    menu_name = menu_name.strip()
    title = title.strip()
    url = url.strip()
    try:
        order_num = int(order_num)
    except:
        order_num = 0

    nav = core.NavigationManager()
    if not nav.add_item(menu_name, title, url, order_num):
        nav.done()

        data = {
            'error': 'Unable create menu item',
            'html': ''
        }

        return http.json_data(data)

    CACHE.clear()

    allitems = nav.get_items()
    menu_list = nav.get_all_menu_names()
    nav.done()
    items = {}

    options = []
    options.append(('/', 'Main page'))
    pages = core.PageManager()
    for i in pages.list():
        if (i[1], i[2]) not in options:
            options.append((i[1], i[2]))
    pages.done()

    if core.CATALOG_ENABLED:
        options.append(('/catalog/', 'Catalog'))
    if core.CONNECT_ENABLED:
        options.append(('/connect/', 'Message Form'))

    for item in allitems:
        if item[1] in items:
            items[item[1]].append(item)
        else:
            items[item[1]] = [item]

        if not [i for i in options if item[3] == i[0]]:
            options.append((item[3], item[3]))

    context = {
        'items':items,
        'menu_list': menu_list,
        'options': options
    }

    data = {
        'error': '',
        'html': html.template(template, context, request)
    }

    return http.json_data(data)


@secure_page
def manager_navigation_edit(request, pk):
    template = 'manager/templates/menu_list.tpl'

    try:
        pk = int(pk)
    except:

        data = {
            'error': 'Invalid menu item id',
            'html': ''
        }

        return http.json_data(data)

    nav = core.NavigationManager()
    item_pk = nav.check_item_id(pk)
    if not item_pk:
        nav.done()

        data = {
            'error': 'Invalid menu item id',
            'html': ''
        }

        return http.json_data(data)

    variables = request['variables']

    menu_name = variables.get('menu_name', None)
    title = variables.get('title', None)
    url = variables.get('url', None)
    order_num = variables.get('order_num', None)

    if not menu_name or not title or not url or not order_num:
        nav.done()

        data = {
            'error': 'All fields are required',
            'html': ''
        }

        return http.json_data(data)

    title = title.strip()
    url = url.strip()

    try:
        menu_name = int(menu_name)
    except:
        nav.done()

        data = {
            'error': 'Unable save changes',
            'html': ''
        }

        return http.json_data(data)

    try:
        order_num = int(order_num)
    except:
        order_num = 0

    if not nav.edit_item(pk, (menu_name, title, url, order_num)):
        nav.done()

        data = {
            'error': 'Unable save changes',
            'html': ''
        }

        return http.json_data(data)

    CACHE.clear()

    allitems = nav.get_items()
    menu_list = nav.get_all_menu_names()
    nav.done()
    items = {}
    options = []
    options.append(('/', 'Main page'))

    pages = core.PageManager()
    for i in pages.list():
        if (i[1], i[2]) not in options:
            options.append((i[1], i[2]))
    pages.done()

    if core.CATALOG_ENABLED:
        options.append(('/catalog/', 'Catalog'))
    if core.CONNECT_ENABLED:
        options.append(('/connect/', 'Message Form'))

    for item in allitems:
        if item[1] in items:
            items[item[1]].append(item)
        else:
            items[item[1]] = [item]

        if not [i for i in options if item[3] == i[0]]:
            options.append((item[3], item[3]))

    context = {
        'items': items,
        'menu_list': menu_list,
        'options': options
    }

    data = {
        'error': '',
        'html': html.template(template, context, request)
    }

    return http.json_data(data)


@secure_page
def manager_navigation_update(request):
    template = 'manager/templates/menu_list.tpl'

    variables = request['variables']
    menu = variables.get('menu', None)
    if menu:
        menu = json.loads(menu)
        nav = core.NavigationManager()
        for menu_name in menu:
            for counter, pk in enumerate(menu[menu_name]):
                try:
                    pk = int(pk)
                except:
                    continue
                nav.update_item(pk, menu_name, counter)

        CACHE.clear()

        allitems = nav.get_items()
        menu_list = nav.get_all_menu_names()
        nav.done()
        items = {}

        options = []
        options.append(('/', 'Main page'))
        pages = core.PageManager()
        for i in pages.list():
            options.append((i[1], i[2]))
        pages.done()
        
        if core.CATALOG_ENABLED:
            options.append(('/catalog/', 'Catalog'))
        if core.CONNECT_ENABLED:
            options.append(('/connect/', 'Message Form'))

        for item in allitems:
            if item[1] in items:
                items[item[1]].append(item)
            else:
                items[item[1]] = [item]

            if not [i for i in options if item[3] == i[0]]:
                options.append((item[3], item[3]))

        context = {
            'items': items,
            'menu_list': menu_list,
            'options': options
        }

        data = {
            'error': '',
            'html': html.template(template, context, request)
        }

        return http.json_data(data)

    data = {
        'error': 'Invalid menu name',
        'html': ''
    }

    return http.json_data(data)


@secure_page
def manager_navigation_remove(request):
    template = 'manager/templates/menu_list.tpl'

    variables = request['variables']
    pk = variables.get('pk', None)
    if pk:
        try:
            pk = int(pk)
        except:

            data = {
                'error': 'Invalid menu item id',
                'success': False
            }

            return http.json_data(data)

        nav = core.NavigationManager()
        nav.remove_item(pk)

        CACHE.clear()

        allitems = nav.get_items()
        menu_list = nav.get_all_menu_names()
        nav.done()
        items = {}

        options = []
        options.append(('/', 'Main page'))
        pages = core.PageManager()
        for i in pages.list():
            options.append((i[1], i[2]))
        pages.done()

        if core.CATALOG_ENABLED:
            options.append(('/catalog/', 'Catalog'))
        if core.CONNECT_ENABLED:
            options.append(('/connect/', 'Message Form'))

        for item in allitems:
            if item[1] in items:
                items[item[1]].append(item)
            else:
                items[item[1]] = [item]

            if not [i for i in options if item[3] == i[0]]:
                options.append((item[3], item[3]))

        context = {
            'items': items,
            'menu_list': menu_list,
            'options': options
        }

        data = {
            'error': '',
            'html': html.template(template, context, request)
        }

        return http.json_data(data)


# =================================
#           connect page
# =================================

def connect_page(request):
    template = 'connect_page.tpl'

    if not core.CONNECT_ENABLED:
        return http.error(404, "Not Found")

    context = {
        'success': '',
        'error': False
    }

    return http.html_page(template, context, request)


def connect_page_post(request):
    template = 'connect_page.tpl'

    if not core.CONNECT_ENABLED:
        return http.error(404, "Not Found")

    variables = request['variables']

    sender = variables.get('sender', None)
    from_email = variables.get('email', None)
    message = variables.get('message', None)

    if not (sender and from_email and message):

        context = {
            'error': 'All fields are required',
            'success': False
        }

        return http.html_page(template, context, request)

    config_manager = core.ConfigManager()
    host = config_manager.get('smtp_host')
    port = config_manager.get('smtp_port')
    login = config_manager.get('smtp_login')
    password = config_manager.get('smtp_password')
    to_email = config_manager.get('connect_email')
    config_manager.done()

    s = smtplib.SMTP()
    try:
        s.connect(host, port)
    except:

        context = {
            'error': 'Mailbox: Unable connect to SMTP-server',
            'success': False
        }

        return http.html_page(template, context, request)

    try:
        s.login(login, password)
    except:

        context = {
            'error': 'Mailbox: Authentication error',
            'success': False
        }

        return http.html_page(template, context, request)

    try:
        s.sendmail(from_email, to_email, message)
    except:

        context = {
            'error': 'Mailbox: Message sending error',
            'success': False
        }

        return http.html_page(template, context, request)

    context = {
        'success': True,
        'error': False
    }

    return http.html_page(template, context, request)


# =================================
#             routes
# =================================

def index_page(request):
    template = 'front_page.tpl'

    content = "FRONT PAGE"

    context = {
        'content': content
    }

    return http.html_page(template, context, request)


def login_page(request):
    template = 'manager/templates/login_page.tpl'

    error = ''
    variables = request['variables']
    if request['method'] == 'POST':
        username = variables.get('username', '')
        password = variables.get('password', '')
        auth = protection.CookieAuthenticator()
        result = auth.login(username, password)
        if result:
            headers = [result]
            return http.redirect(core.MANAGER_URL, headers)

        return http.redirect('%slogin/' % core.MANAGER_URL)

    context = {
        'error': error
    }

    return http.html_page(template, context, request)


def logout_page(request):
    auth = protection.CookieAuthenticator()
    headers = auth.logout(request['headers'])
    if headers is None:
        return http.redirect('%slogin/' % core.MANAGER_URL)

    return http.redirect('/', [headers])


@secure_page
def manager_page(request):
    template = 'manager/templates/dashboard_page.tpl'

    return http.html_page(template, {}, request)


def catalog_page(request):
    template = 'catalog_page.tpl'

    if not core.CATALOG_ENABLED:
        return http.error(404, "Not Found")

    catalog_manager = core.CatalogManager()

    if not catalog_manager.exist():
        catalog_manager.done()
        return http.error(404, "Not Found")

    catalog = catalog_manager.browse()
    catalog_manager.done()

    context = {
        'catalog': catalog
    }

    return http.html_page(template, context, request)


def catalog_category_page(request, pk):
    template = 'catalog_category_page.tpl'

    if not core.CATALOG_ENABLED:
        return http.error(404, "Not Found")

    catalog_manager = core.CatalogManager()
    category = catalog_manager.get_category(int(pk))
    if category is False:
        catalog_manager.done()
        return http.error(404, "Not Found")

    catalog = catalog_manager.browse(category=pk)
    catalog_manager.done()

    context = {
        'catalog': catalog
    }

    return http.html_page(template, context, request)


def catalog_item_page(request, item):
    template = 'catalog_item_page.tpl'

    if not core.CATALOG_ENABLED:
        return http.error(404, "Not Found")

    catalog_manager = core.CatalogManager()
    item = catalog_manager.get_item(int(item))
    if item is False:
        catalog_manager.done()
        return http.error(404, "Not Found")

    catalog_manager.done()

    context = {
        'item': item
    }

    return http.html_page(template, context, request)


def static_page(request, name):
    template = 'static_page.tpl'

    pages = core.PageManager()
    page = pages.show(name)
    pages.done()
    if page is None:
        return http.error(404, "Not Found")

    content = {}
    content['name'] = page[1]
    content['title'] = page[2]
    content['content'] = page[3]
    content['created'] = page[4]
    content['updated'] = page[5]

    context = {
        'content': content
    }

    return http.html_page(template, context, request)