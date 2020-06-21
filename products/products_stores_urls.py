from django.conf.urls import url, include

from . products_stores_views import \
add, \
find, \
view_details, \
delete, \
edit, \
delete_product, \
update, \
remove_many_from_stores
'''
, \
do_add, \
find, \
do_find, \
do_view_all, 
do_delete, \
do_edit, \
view_details, \
, \
update
'''
from products import products_stores_search_urls
#from products import autocomplete_urls

urlpatterns = [
  url(r'^add', add, name='add-product-store'),
  #url(r'^do-add', do_add, name='do-add'),
  url(r'^find', find, name='find-product-store'),
  #url(r'^do-find', do_find, name='do-find'),
  #url(r'^list-all', do_view_all, name='list-all'),
  url(r'^edit', edit, name='edit-product-store'),
  #url(r'^do-edit', do_edit, name='do-edit'),
  url(r'^delete', delete, name='delete-product-store'),
  #url(r'^do-delete', do_delete, name='do-delete'),
  url(r'^view-details', view_details, name='view-details-product-store'),
  url(r'^confirmed-delete', delete_product, name='confirmed-delete-product-store'),
  #url(r'^update', update, name='update'),
  url(r'^search/', include(products_stores_search_urls.urlpatterns)),
  url(r'^update', update, name='update'),
  url(r'^remove-many-from-stores', remove_many_from_stores, name='remove-many-products-from-stores'),
  #url(r'^autocomplete/', include(autocomplete_urls.urlpatterns)),
]