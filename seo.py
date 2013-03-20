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

import os
import datetime
import http
import core

def create_sitemap(request):
    path = os.path.join(core.VAR_ROOT, 'sitemap.xml')
    domain = http.get_header(request['headers'], 'Host')
    config = core.ConfigManager()
    install_date = config.get('install_date')
    if install_date:
        install_date = install_date[:10]
    config.done()

    try:
        sitemap = open(path, 'w+b')
    except:
        return False

    content = '<?xml version="1.0" encoding="UTF-8"?>'
    content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

    # front page
    content += '<url>'
    content += '<loc>http://%s/</loc>' % domain
    content += '<lastmod>%s</lastmod>' % install_date
    content += '<changefreq>weekly</changefreq>'
    content += '<priority>1</priority>'
    content += '</url>'
    sitemap.write(content)


    # static pages
    page_manager = core.PageManager()
    pages = page_manager.list(page=0, active_only=True)
    page_manager.done()


    for p in pages:
        content = '<url>'
        content += '<loc>http://%s/%s.html</loc>' % (domain, p[1])
        content += '<lastmod>%s</lastmod>' % p[5][:10] if p[5] else p[4][:10]
        content += '<changefreq>weekly</changefreq>'
        content += '<priority>0.8</priority>'
        content += '</url>'
        sitemap.write(content)

    # catalog pages
    if core.CATALOG_ENABLED:
        content = '<url>'
        content += '<loc>http://%s/catalog/</loc>' % domain
        content += '<lastmod>%s</lastmod>' % install_date
        content += '<changefreq>weekly</changefreq>'
        content += '<priority>0.8</priority>'
        content += '</url>'
        sitemap.write(content)

        catalog_manager = core.CatalogManager()

        for item in catalog_manager.catalog_map():
            if item[0] == "c":
                content = '<url>'
                content += '<loc>http://%s/catalog/category-%s/</loc>' % (domain, item[1])
                content += '<lastmod>%s</lastmod>' % item[3][:10]
                content += '<changefreq>weekly</changefreq>'
                content += '<priority>0.6</priority>'
                content += '</url>'
                sitemap.write(content)
            elif item[0] == "i":
                content = '<url>'
                content += '<loc>http://%s/catalog/%s/</loc>' % (domain, item[1])
                content += '<lastmod>%s</lastmod>' % item[3][:10]
                content += '<changefreq>weekly</changefreq>'
                content += '<priority>%s</priority>' % ('0.5' if item[2] else '0.6')
                content += '</url>'
                sitemap.write(content)

        catalog_manager.done()

    # connect page
    if core.CONNECT_ENABLED:
        content = '<url>'
        content += '<loc>http://%s/connect/</loc>' % domain
        content += '<lastmod>%s</lastmod>' % install_date
        content += '<changefreq>weekly</changefreq>'
        content += '<priority>0.8</priority>'
        content += '</url>'
        sitemap.write(content)

    content = '</urlset>'

    sitemap.write(content)
    sitemap.close()
    return True