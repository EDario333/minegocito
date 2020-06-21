from django.conf.urls import url, include

from . views import \
add, \
do_add, \
find, \
do_find, \
do_view_all, \
delete, \
do_delete, \
edit, \
do_edit, \
view_details, \
delete_store, \
update

from stores import search_urls
from stores import autocomplete_urls

urlpatterns = [
  url(r'^add', add, name='add'),
  url(r'^do-add', do_add, name='do-add'),
  url(r'^find', find, name='find'),
  url(r'^do-find', do_find, name='do-find'),
  url(r'^list-all', do_view_all, name='list-all'),
  url(r'^edit', edit, name='edit'),
  url(r'^do-edit', do_edit, name='do-edit'),
  url(r'^delete', delete, name='delete'),
  url(r'^do-delete', do_delete, name='do-delete'),
  url(r'^view-details', view_details, name='view-details'),
  url(r'^confirmed-delete', delete_store, name='confirmed-delete'),
  url(r'^update', update, name='update'),
  url(r'^search/', include(search_urls.urlpatterns)),
  url(r'^autocomplete/', include(autocomplete_urls.urlpatterns)),
]