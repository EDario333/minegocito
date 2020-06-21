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
delete_purchase, \
update, \
product_details, \
sku_products, \
show_purchased_products
#add_product_details
#products_details, \

#from purchases import products_stores_search_urls
#from products import autocomplete_urls
from purchases import search_urls
from . import purchased_products_urls

urlpatterns = [
  url(r'^add', add, name='add-purchase'),
  url(r'^do-add', do_add, name='do-add-purchase'),
  url(r'^find', find, name='find-purchase'),
  url(r'^do-find', do_find, name='do-find-purchase'),
  url(r'^list-all', do_view_all, name='list-all-purchases'),
  url(r'^edit', edit, name='edit-purchase'),
  url(r'^do-edit', do_edit, name='do-edit-purchase'),
  url(r'^delete', delete, name='delete-purchase'),
  url(r'^do-delete', do_delete, name='do-delete-purchase'),
  url(r'^view-details', view_details, name='view-details-purchase'),
  url(r'^confirmed-delete', delete_purchase, name='confirmed-delete-purchase'),
  url(r'^update', update, name='update-purchase'),
  url(r'^search/', include(search_urls.urlpatterns)),
  url(r'^product-details', product_details, name='product-details-purchase'),
  url(r'^sku-products', sku_products, name='sku-products-purchase'),
  url(r'^show-purchased-products', show_purchased_products, name='show-purchased-products'),
  url(r'^purchased-products/', include(purchased_products_urls.urlpatterns)),
  #url(r'^autocomplete/', include(autocomplete_urls.urlpatterns)),
]