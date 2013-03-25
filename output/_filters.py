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
# registered filters
#
import json
import files
import protection

def length(value):
    if not value:
        return 0
    return value.__len__()

def is_none(value):
    if not value or value in ('None', '0', 'False', ''):
        return True
    return False

def is_true_or_empty(value):
    if value or value == '':
        return True
    return False

def is_not_true_or_empty(value):
    return not is_true_or_empty(value)

def is_some(value):
    return not is_none(value)

def escape(value):
    return value.replace('&', '&amp;').replace('>', '&gt;')\
    .replace('<', '&lt;').replace("'", '&#39;').replace('"', '&#34;')

def linebreaksbr(value):
    return value.replace('\n', '<br />')

def theme_name(theme):
    name = theme[1]['name'] if theme else ''
    return name

def theme_navigations(theme):
    navigations = theme[1]['navigation'] if theme else ''
    return ', '.join(navigations)

def theme_author(theme):
    if not theme:
        return ''

    desc = theme[1]

    if desc['url']:
        author = '<a href="%s">%s</a>' % (desc['url'], desc['author'])
    else:
        author = desc['author']

    return author

def categories(catalog):
    return catalog[0]

def items(catalog):
    return catalog[1]

def custom_fields(item):
    return item[3:-3] if item else ()

def get_field(item, num):
    if not item:
        return None

    return item[num]

def get_field_name(item, num):
    if not item:
        return None

    return item[num][0]

def get_field_value(item, num):
    if not item:
        return None

    return item[num][1]

def category(item):
    if not item:
        return None

    category = item.get_category(value)
    value = category[1] if category else None
    return value

def main_image(item):
    if not item:
        return None

    if isinstance(item[2][1], basestring):
        d = json.loads(item[2][1])
        return d['main'] if 'main' in d else ''

    d = item[2][1]
    return d['main'] if 'main' in d else ''

def extra_images(item, num=None):
    if not item:
        return None

    data = item[2][1]

    if isinstance(data, basestring):
        result = json.loads(data)['extra']

        if num is None:
            return result

        return result[num] if num < len(result) else ''

    if num is None:
        return data['extra']

    return data['extra'][num] if num < len(data['extra']) else ''

def get_mini_image(s):
    return files.get_mini_image(s)

def get_small_image(s):
    return files.get_small_image(s)

def get_medium_image(s):
    return files.get_medium_image(s)

def get_big_image(s):
    return files.get_big_image(s)

def get_original_image(s):
    return files.get_original_url(s)


filterCollection = {
    'length': length,
    'range': xrange,
    'is_none': is_none,
    'is_some': is_some,
    'is_true_or_empty': is_true_or_empty,
    'is_not_true_or_empty': is_not_true_or_empty,
    'escape': escape,
    'linebreaksbr': linebreaksbr,
    'theme_name': theme_name,
    'theme_navigations': theme_navigations,
    'theme_author': theme_author,
    'categories': categories,
    'items': items,
    'custom_fields': custom_fields,
    'get_field': get_field,
    'get_field_name': get_field_name,
    'get_field_value': get_field_value,
    'main_image': main_image,
    'extra_images': extra_images,
    'get_mini_image': get_mini_image,
    'get_small_image': get_small_image,
    'get_medium_image': get_medium_image,
    'get_big_image': get_big_image,
    'get_original_image': get_original_image
}