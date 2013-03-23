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

import core
import functions

#
# URLs are hardcode (used by server.py, seo.py, functions.py, js files, ...)
# (URL, (GET_handler, POST_handler), cachable)
#
router = (
    (r'^/$', (functions.index_page, None), 1),
    (r'^%s$' % core.MANAGER_URL, (functions.manager_page, None), 0),

    (r'^%slogin/$' % core.MANAGER_URL, (
        functions.login_page, # GET
        functions.login_page  # POST
    ), 0),

    (r'^%slogout/$' % core.MANAGER_URL, (
        functions.logout_page,
        None
    ), 0),

    (r'^%ssettings/$' % core.MANAGER_URL, (
        functions.manager_config,
        functions.manager_config_post
    ), 0),

    (r'^%ssettings/logo/clear/$' % core.MANAGER_URL, (
        None,
        functions.manager_config_logo_delete
    ), 0),

    (r'^%sseo/sitemap/$' % core.MANAGER_URL, (
        None,
        functions.manager_seo_sitemap
    ), 0),

    (r'^%snav/$' % core.MANAGER_URL, (
        functions.manager_navigation_list,
        functions.manager_navigation_create
    ), 0),

    (r'^%snav/update/$' % core.MANAGER_URL, (
        None,
        functions.manager_navigation_update
    ), 0),

    (r'^%snav/(?P<pk>\d+)/$' % core.MANAGER_URL, (
        None,
        functions.manager_navigation_edit
    ), 0),

    (r'^%snav/remove/$' % core.MANAGER_URL, (
        None,
        functions.manager_navigation_remove
    ), 0),

    (r'^%spage/$' % core.MANAGER_URL, (
        functions.static_pages_redirect,
        functions.static_page_edit
    ), 0),

    (r'^%spage/save/$' % core.MANAGER_URL, (
        None,
        functions.static_page_save
    ), 0),

    (r'^%spage/delete/$' % core.MANAGER_URL, (
        None,
        functions.static_page_delete
    ), 0),

    (r'^%spage/preview/$' % core.MANAGER_URL, (
        None,
        functions.static_page_preview
    ), 0),

    (r'^%spages/$' % core.MANAGER_URL, (
        functions.static_page_list,
        None
    ), 0),

    (r'^%spages/layout/$' % core.MANAGER_URL, (
        None,
        functions.static_layout
    ), 0),

    (r'^%spages/url/$' % core.MANAGER_URL, (
        None,
        functions.static_pages_url
    ), 0),

    (r'^%scatalog/$' % core.MANAGER_URL, (
        functions.manager_catalog,
        functions.manager_catalog_listing
    ), 0),

    (r'^%scatalog/category/$' % core.MANAGER_URL, (
        None,
        functions.manager_catalog_category_action
    ), 0),

    (r'^%scatalog/prepare/$' % core.MANAGER_URL, (
        None,
        functions.manager_catalog_wizard_start
    ), 0),

    (r'^%scatalog/create/$' % core.MANAGER_URL, (
        None,
        functions.manager_catalog_wizard_end
    ), 0),

    (r'^%scatalog/add/$' % core.MANAGER_URL, (
        functions.manager_catalog_add,
        functions.manager_catalog_add_data
    ), 0),

    (r'^%scatalog/add/(?P<category>\d+)/$' % core.MANAGER_URL, (
        functions.manager_catalog_add_to_category,
        functions.manager_catalog_add_to_category_post
    ), 0),

    (r'^%scatalog/edit/$' % core.MANAGER_URL, (
        functions.manager_catalog_edit,
        functions.manager_catalog_edit_data
    ), 0),

    (r'^%scatalog/activate/$' % core.MANAGER_URL, (
        None,
        functions.manager_catalog_activate
    ), 0),

    (r'^%scatalog/delete/$' % core.MANAGER_URL, (
        None,
        functions.manager_catalog_delete
    ), 0),

    (r'^%scatalog/import/$' % core.MANAGER_URL, (
        functions.manager_catalog_import,
        None
    ), 0),

    (r'^%scatalog/upload/$' % core.MANAGER_URL, (
        None,
        functions.manager_catalog_image_upload
    ), 0),

    (r'^%suploaded/remove/$' % core.MANAGER_URL, (
        None,
        functions.remove_uploaded_image
    ), 0),

    (r'^%supload/$' % core.MANAGER_URL, (
        None,
        functions.image_upload
    ), 0),

    (r'^%sresize/$' % core.MANAGER_URL, (
        None,
        functions.image_resize
    ), 0),

    (r'^%sbrowse/$' % core.MANAGER_URL, (
        None,
        functions.image_browse
    ), 0),

    (r'^%schoice/$' % core.MANAGER_URL, (
        None,
        functions.image_choice
    ), 0),

    (r'^/(?P<name>.{1,75})\.html$', (
        functions.static_page,
        None
    ), 1),

    (r'^/catalog/$', (
        functions.catalog_page,
        None
    ), 1),

    (r'^/catalog/(?P<item>\d+)/$', (
        functions.catalog_item_page,
        None
    ), 1),

    (r'^/catalog/category-(?P<pk>\d+)/$', (
        functions.catalog_category_page,
        None
    ), 1),

    (r'^/connect/$', (
        functions.connect_page,
        functions.connect_page_post
    ), 0)
)
