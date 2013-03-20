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
# URLs are hardcode (used by srever.py, seo.py, functions.py, js files, ...)
#
router = (
    (r'^/$', ('GET',), 
        functions.index_page),

    (r'^%s$' % core.MANAGER_URL, ('GET',), 
        functions.manager_page),

    (r'^%slogin/$' % core.MANAGER_URL, ('GET', 'POST'), 
        functions.login_page),

    (r'^%slogout/$' % core.MANAGER_URL, ('GET',), 
        functions.logout_page),

    (r'^%ssettings/$' % core.MANAGER_URL, ('GET',), 
        functions.manager_config),

    (r'^%ssettings/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_config_post),

    (r'^%ssettings/logo/clear/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_config_logo_delete),

    (r'^%sseo/sitemap/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_seo_sitemap),

    (r'^%snav/$' % core.MANAGER_URL, ('GET',), 
        functions.manager_navigation_list),

    (r'^%snav/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_navigation_create),

    (r'^%snav/update/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_navigation_update),

    (r'^%snav/(?P<pk>\d+)/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_navigation_edit),

    (r'^%snav/remove/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_navigation_remove),

    (r'^%spage/$' % core.MANAGER_URL, ('GET',), 
        functions.static_pages_redirect),

    (r'^%spage/$' % core.MANAGER_URL, ('POST',), 
        functions.static_page_edit),

    (r'^%spage/save/$' % core.MANAGER_URL, ('POST',), 
        functions.static_page_save),

    (r'^%spage/delete/$' % core.MANAGER_URL, ('POST',), 
        functions.static_page_delete),

    (r'^%spage/preview/$' % core.MANAGER_URL, ('POST',), 
        functions.static_page_preview),

    (r'^%spages/$' % core.MANAGER_URL, ('GET',), 
        functions.static_page_list),

    (r'^%spages/layout/$' % core.MANAGER_URL, ('POST',), 
        functions.static_layout),

    (r'^%spages/url/$' % core.MANAGER_URL, ('POST',), 
        functions.static_pages_url),

    (r'^%scatalog/$' % core.MANAGER_URL, ('GET',), 
        functions.manager_catalog),

    (r'^%scatalog/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_catalog_listing),

    (r'^%scatalog/category/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_catalog_category_action),

    (r'^%scatalog/prepare/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_catalog_wizard_start),

    (r'^%scatalog/create/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_catalog_wizard_end),

    (r'^%scatalog/add/$' % core.MANAGER_URL, ('GET',), 
        functions.manager_catalog_add),

    (r'^%scatalog/add/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_catalog_add_data),

    (r'^%scatalog/add/(?P<category>\d+)/$' % core.MANAGER_URL, ('GET',), 
        functions.manager_catalog_add_to_category),

    (r'^%scatalog/add/(?P<category>\d+)/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_catalog_add_to_category_post),

    (r'^%scatalog/edit/$' % core.MANAGER_URL, ('GET',), 
        functions.manager_catalog_edit),

    (r'^%scatalog/edit/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_catalog_edit_data),

    (r'^%scatalog/activate/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_catalog_activate),

    (r'^%scatalog/delete/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_catalog_delete),

    (r'^%scatalog/import/$' % core.MANAGER_URL, ('GET',), 
        functions.manager_catalog_import),

    (r'^%scatalog/upload/$' % core.MANAGER_URL, ('POST',), 
        functions.manager_catalog_image_upload),

#    (r'^%scatalog/image/clear/$' % core.MANAGER_URL, ('POST',), 
#        functions.clear_catalog_image),

    (r'^%suploaded/remove/$' % core.MANAGER_URL, ('POST',), 
        functions.remove_uploaded_image),

    (r'^%supload/$' % core.MANAGER_URL, ('POST',), 
        functions.image_upload),

    (r'^%sresize/$' % core.MANAGER_URL, ('POST',), 
        functions.image_resize),

    (r'^%sbrowse/$' % core.MANAGER_URL, ('POST',), 
        functions.image_browse),

    (r'^%schoice/$' % core.MANAGER_URL, ('POST',), 
        functions.image_choice),

    (r'^/(?P<name>.{1,75})\.html$', ('GET',), 
        functions.static_page),

    (r'^/catalog/$', ('GET',), 
        functions.catalog_page),

    (r'^/catalog/(?P<item>\d+)/$', ('GET',), 
        functions.catalog_item_page),

    (r'^/catalog/category-(?P<pk>\d+)/$', ('GET',), 
        functions.catalog_category_page),

    (r'^/connect/$', ('GET',), 
        functions.connect_page),

    (r'^/connect/$', ('POST',), 
        functions.connect_page_post),
)