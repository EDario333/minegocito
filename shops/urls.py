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
delete_shop, \
update, \
home, \
apply_filters_shops_home, \
new_visit

from shops import urls_autocomplete, urls_search

urlpatterns = [
  url(r'^add', add, name='add-shop'),
  url(r'^do-add', do_add, name='do-add-shop'),
  url(r'^find', find, name='find-shop'),
  url(r'^do-find', do_find, name='do-find-shop'),
  url(r'^list-all', do_view_all, name='list-all-shops'),
  url(r'^edit', edit, name='edit-shop'),
  url(r'^do-edit', do_edit, name='do-edit-shop'),
  url(r'^delete', delete, name='delete-shop'),
  url(r'^do-delete', do_delete, name='do-delete-shop'),
  url(r'^view-details', view_details, name='view-details-shop'),
  url(r'^confirmed-delete', delete_shop, name='confirmed-delete-shop'),
  url(r'^update', update, name='update-shop'),
  url(r'^autocomplete/', include(urls_autocomplete.urlpatterns)),
  url(r'^search/', include(urls_search.urlpatterns)),
  url(r'^home', home, name='shops'),
  url(r'^apply-filters-shops-home', apply_filters_shops_home, name='apply-filters-shops-home'),
  url(r'^new-visit', new_visit, name='shop-new-visit'),
]