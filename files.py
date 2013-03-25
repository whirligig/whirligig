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

from PIL import Image
import uuid
import os
import re
import json
import urlparse
import hashlib
import shutil
import core

MANAGER_STATIC_PATH = '%s/manager/static/' % core.ROOT
THEME_STATIC_PATH = '%s/themes/%s/static/' % (core.ROOT, core.THEME)

UPLOAD_BASE_PATH = '%s/uploads' % core.ROOT
UPLOAD_BASE_URL = "/uploads"

IMAGE_MAX_SIZE = 1024*1024*4 # 4 megabytes
IMAGE_FORMATS = ('jpg', 'jpeg', 'bmp', 'png', 'tif', 'tiff', 'gif')
IMAGE_SIZE = {}
IMAGE_SIZE['MINI'] = 70
IMAGE_SIZE['SMALL'] = 150
IMAGE_SIZE['MEDIUM'] = 500
IMAGE_SIZE['BIG'] = 900
RATIO = 1.1


if not os.path.exists(UPLOAD_BASE_PATH):
    try:
        os.makedirs(UPLOAD_BASE_PATH)
    except:
        print "Unable create upload directory (%s)" % UPLOAD_BASE_PATH
        exit(0)


#
# get directory on local filesystem by request url
#
def get_static_path(uri):
    root = None
    filename = os.path.basename(uri)
    if uri == '/sitemap.xml' or uri == '/robots.txt':
        root = core.VAR_ROOT
    elif uri == '/static/commons.css':
        root = MANAGER_STATIC_PATH
    elif uri == '/static/core.js':
        root = MANAGER_STATIC_PATH
    elif uri in map(lambda x: no_image(x), IMAGE_SIZE.values()):
        root = MANAGER_STATIC_PATH + 'no-image/'
    elif uri.startswith('/static/pirobox/'):
        root = MANAGER_STATIC_PATH + 'pirobox/'
    elif uri.startswith(core.MANAGER_URL + 'static/'):
        root = MANAGER_STATIC_PATH
    elif uri.startswith('/static/'):
        root = THEME_STATIC_PATH
    elif uri.startswith('/uploads/'):
        root = files.UPLOAD_BASE_PATH
        filename = uri.split('/uploads/', 1)[1]
    elif root is None:
        return root, filename

    # security check
    path = '%s/%s' % (root, filename)
    if not os.path.abspath(path).startswith(root):
        root = filename = None
    return root, filename


#
# get file content
#
def get_file(root, filename):
    content = None
    path = os.path.abspath('%s/%s' % (root, filename))
    try:
        f = open(path, 'r+b')
    except:
        return None

    content = f.read()
    return content

#
# objects stores files in directory for fast response to clients
#
class Cache(object):

    # max_items - max items (files) in cache directory
    # (0 = unlimited)
    def __init__(self, max_items=0):

        self._create_root()
        self.max_items = max_items


    def _create_root(self):
        self.path = os.path.join(core.VAR_ROOT, 'cache/')
        if not os.path.exists(self.path):
            try:
                os.makedirs(self.path)
            except os.error:
                print "ERROR: Unable create cache directory."
                exit()


    def _convert_name(self, name):
        if name.startswith('/'):
            name = name[1:]
        # index page ('/')
        if not name:
            name = 'index.html'
        if name.endswith('/'):
            name = name[:-1]
        name = name.replace('/', '_')
        return name


    def get(self, uri):
        uri = self._convert_name(uri)

        if not os.path.exists(self.path):
            self._create_root()

        cache_content = os.listdir(self.path)
        if uri not in cache_content:
            return None

        filename = os.path.join(self.path, uri)

        try:
            f = open(filename, 'r+b')
        except IOError:
            print "ERROR: Unable get content of %s (cache)" % filename
            return

        content = f.read()
        f.close()

        return content


    def set(self, uri, content):
        uri = self._convert_name(uri)
        abs_path = os.path.join(self.path, uri)

        if self.max_items:

            if not os.path.exists(self.path):
                self._create_root()

            items = os.listdir(self.path)
            if items.__len__() >= self.max_items:
                i = random.randint(1, self.max_items)
                os.remove(os.path.join(self.path, items[i]))

        with open(abs_path, 'w+b') as f:
            content = content.split('\r\n\r\n', 1)[1]
            f.write(content)
            return True

        return False


    def remove_item(uri):
        uri = self._convert_name(uri)

        if not os.path.exists(self.path):
            self._create_root()

        cache_content = os.listdir(self.path)
        if uri not in cache_content:
            return None

        filename = os.path.join(self.path, uri)
        try:
            os.remove(filename)
        except:
            return None
        return True


    def remove_catalog_files():
        pass


    def clear(self):
        shutil.rmtree(self.path, ignore_errors=True)


def find_extension(format):
    format = format.lower()
    if format not in IMAGE_FORMATS:
        return None
    if format == 'jpeg':
        format = 'jpg'
    return format


def get_available_name(name):
    extension = name.split(".")[-1]
    for i in xrange(200):
        name = "%s.%s" % (str(uuid.uuid4()), extension)
        outdir = os.path.join(UPLOAD_BASE_PATH, 'raw')
        outfile = os.path.join(outdir, name)
        if not os.path.isfile(outfile):
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            return outfile
    return None


def url_to_path(url):
    arr = url.split(UPLOAD_BASE_URL)
    if len(arr) > 1:
        relative_name = arr[1]
        return get_original_path(relative_name)
    return ''


def get_original_path(filename):
    filename = os.path.basename(filename)
    source_dir = os.path.join(UPLOAD_BASE_PATH, "raw")
    path = os.path.join(source_dir, filename)
    return path


def get_original_url(filename):
    filename = os.path.basename(filename)
    url = '%s/%s/%s' % (UPLOAD_BASE_URL, "raw", filename)
    return url


def get_original_images(amount=0, offset=0):
    images = []
    image_dir = os.path.join(UPLOAD_BASE_PATH, 'raw')
    try:
        images = os.listdir(image_dir)
        images = [os.path.join(image_dir, f) for f in images]
        images.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    except:
        pass
    if amount == 0:
        amount = len(images) - offset
    if amount < 0:
        amount = 0
    try:
        images = images[offset:offset+amount]
    except:
        pass
    return images


def save_logo(name):
    extension = name.split(".")[-1]
    name = get_original_path(name)

    content = open(name, 'r+b')

    try:
        img = Image.open(content)
        if find_extension(img.format) is None:
            content.close()
            raise IOError
    except IOError:
        return None

    content.seek(0,2)
    filesize = content.tell()
    if filesize > IMAGE_MAX_SIZE:
        return None

    dirname = os.path.dirname(name)
    img.save('%s/logo.png' % dirname)
    content.close()

    try:
        os.remove(name)
    except:
        return None

    return True


def delete_logo():
    image_path = get_original_path('logo.png')
    try:
        os.remove(image_path)
    except:
        return False

    image_dir = os.path.dirname(image_path)

    try:
        if not os.listdir(image_dir):
            os.rmdir(image_dir)
    except:
        return False

    for size_name in IMAGE_SIZE:
        delete_thumbnail(image_path, IMAGE_SIZE[size_name])

    return True


def save_uploaded_image(uploaded_manager, name):
    basename = name
    name = get_original_path(name)
    content = open(name, 'r+b')

    try:
        img = Image.open(content)
        if find_extension(img.format) is None:
            raise IOError
    except IOError:
        return None

    content.seek(0,2)
    filesize = content.tell()
    if filesize > IMAGE_MAX_SIZE:
        return None

    content.seek(0)
    hash_object = hashlib.sha256()
    while True:
        chunk = content.read(1024*100)
        if not chunk: break
        hash_object.update(chunk)
    h = hash_object.hexdigest()

    exists = uploaded_manager.get_image_name(h, filesize)
    content.close()

    if exists:
        if os.path.exists(get_original_path(exists)):
            os.remove(name)
            return exists
        else:
            uploaded_manager.remove_image(exists)
            uploaded_manager.add_image(h, filesize, basename)
            return basename
    else:
        uploaded_manager.add_image(h, filesize, basename)
    return basename


def generate_thumbnail(source_path, size):
    '''
        Generate thumbnail image
        size - max size (width or height) of thumbnail
    '''
    if not source_path or not size:
        return None

    filename = os.path.basename(source_path)
    original_dir = os.path.join(UPLOAD_BASE_PATH, "raw")
    original_path = os.path.join(original_dir, filename)

    thumbnail_dir = os.path.join(UPLOAD_BASE_PATH, str(size))
    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)
    thumbnail = os.path.join(thumbnail_dir, filename)
    if not os.path.exists(thumbnail):
        try:
            image = Image.open(original_path)
            if image.size[1] > image.size[0] * RATIO:
                width = size
                height = image.size[1]
            else:
                width = size
                height = width * image.size[1] / image.size[0]
            image.thumbnail((width, height), Image.ANTIALIAS)
            image.save(thumbnail, image.format, quality=95)
        except:
            return None

    return "%s/%s/%s" % (UPLOAD_BASE_URL, str(size), filename)


def get_thumbnail_path(image_path, size):
    if not image_path:
        return None

    filename = os.path.basename(image_path)
    thumbnail_path = os.path.join(UPLOAD_BASE_PATH, str(size))
    thumbnail_path = os.path.join(thumbnail_path, filename)
    if not os.path.isfile(thumbnail_path):
        return None

    return thumbnail_path


def get_thumbnail_url(image_url, size):
    if not image_url:
        return no_image(size)

    filename = os.path.basename(image_url)
    thumbnail_url = urlparse.urljoin(UPLOAD_BASE_URL, str(size))
    thumbnail_url = urlparse.urljoin(thumbnail_url, filename)
    image_path = url_to_path(thumbnail_url)
    if not os.path.isfile(image_path):
        return None

    return thumbnail_url


def get_mini_image(image_path):
    thumbnail_url = get_thumbnail_url(image_path, IMAGE_SIZE['MINI'])
    if thumbnail_url is None:
        thumbnail = generate_thumbnail(image_path, IMAGE_SIZE['MINI'])
        if thumbnail:
            return thumbnail

        else:
            return get_thumbnail_url(None, IMAGE_SIZE['MINI'])

    return thumbnail_url


def get_small_image(image_path):
    thumbnail_url = get_thumbnail_url(image_path, IMAGE_SIZE['SMALL'])
    if thumbnail_url is None:
        thumbnail = generate_thumbnail(image_path, IMAGE_SIZE['SMALL'])
        if thumbnail:
            return thumbnail

        else:
            return get_thumbnail_url(None, IMAGE_SIZE['SMALL'])

    return thumbnail_url


def get_medium_image(image_path):
    thumbnail_url = get_thumbnail_url(image_path, IMAGE_SIZE['MEDIUM'])
    if thumbnail_url is None:
        thumbnail = generate_thumbnail(image_path, IMAGE_SIZE['MEDIUM'])
        if thumbnail:
            return thumbnail

        else:
            return get_thumbnail_url(None, IMAGE_SIZE['MEDIUM'])

    return thumbnail_url


def get_big_image(image_path):
    thumbnail_url = get_thumbnail_url(image_path, IMAGE_SIZE['BIG'])
    if thumbnail_url is None:
        thumbnail = generate_thumbnail(image_path, IMAGE_SIZE['BIG'])
        if thumbnail:
            return thumbnail

        else:
            return get_thumbnail_url(None, IMAGE_SIZE['BIG'])

    return thumbnail_url


def delete_thumbnail(image_path, size):
    thumbnail = get_thumbnail_path(image_path, size)
    thumbnail_dir = os.path.join(UPLOAD_BASE_PATH, str(size))
    if not thumbnail:
        return None

    try:
        os.remove(thumbnail)
        if not os.listdir(thumbnail_dir):
            os.rmdir(thumbnail_dir)
    except:
        pass


def delete_image(uploaded_manager, image_path):
    image_name = os.path.basename(image_path)
    image_dir = os.path.join(UPLOAD_BASE_PATH, "raw")
    image_path = get_original_path(image_name)
    try:
        os.remove(image_path)
    except:
        return

    uploaded_manager.remove_image(image_name)

    try:
        if not os.listdir(image_dir):
            os.rmdir(image_dir)
    except:
        return

    for size_name in IMAGE_SIZE:
        delete_thumbnail(image_path, IMAGE_SIZE[size_name])


def install_theme(folder_name):
    if not isinstance(folder_name, basestring):
        return False

    description = get_theme_description(folder_name)

    config = core.ConfigManager()

    config.set('theme', description['name'])
    config.set('theme_author', description['author'])
    config.set('theme_author_url', description['url'])
    config.set('theme_use_logo', description['use logo'])
    config.set('theme_navigation', ', '.join(description['navigation']))
    config.done()

    return True


def no_image(size):
    if isinstance(size, int) and size in IMAGE_SIZE.values():
        return '/static/no-image-%s.png' % size

    if isinstance(size, basestring) and size.upper() in IMAGE_SIZE.keys():
        return '/static/no-image-%s.png' % IMAGE_SIZE[size.upper()]

    return ''


def get_theme_description(theme):
    themes_dir = os.path.join(core.ROOT, 'themes')
    desc_file = os.path.join(themes_dir, theme, 'description.txt')
    if not os.path.isfile(desc_file):
        return None

    try:
        f = open(desc_file, 'r')
    except IOError:
        return None

    description = {}
    for line in f:
        l = re.match(r'^([^:]+):\s(.+?)(\r|\n|$)+', line)
        if l:
            description[l.group(1)] = l.group(2)
    f.close()

    if 'name' not in description:
        description['name'] = theme

    if 'author' not in description:
        description['author'] = 'unknown'

    if 'url' not in description:
        description['url'] = ''

    if 'use logo' in description and description['use logo'].lower() == 'yes':
        description['use logo'] = 1
    else:
        description['use logo'] = 0

    if 'navigation' in description:
        l = description['navigation'].split(',')
        description['navigation'] = filter(bool, map(lambda x: x.strip(), l))

    return description


def get_theme_screenshots(theme):
    size = IMAGE_SIZE['MINI']
    unsecure = os.path.join(core.ROOT, 'themes', theme, 'screenshots')
    scr_dir = os.path.abspath(unsecure)
    if not os.path.isdir(scr_dir) or not scr_dir.startswith(core.ROOT):
        return []

    images = []

    images.append(os.path.join(scr_dir, 'front_page.png'))
    images.append(os.path.join(scr_dir, 'static_page.png'))
    images.append(os.path.join(scr_dir, 'catalog.png'))
    images.append(os.path.join(scr_dir, 'catalog_category.png'))
    images.append(os.path.join(scr_dir, 'catalog_item.png'))
    images.append(os.path.join(scr_dir, 'connect.png'))

    result = map(lambda x: x if os.path.isfile(x) else no_image(size), images)

    return result


#
# get installed themes
#
def get_themes():
    themes_dir = os.path.join(core.ROOT, 'themes')
    folders = os.listdir(themes_dir)
    result = []
    for folder in folders:
        description = get_theme_description(folder)
        if not description:
            continue

        result.append((folder, description))

    return result