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
delete_sale, \
update, \
product_details, \
show_sold_products, \
view_product_details, \
view_selected_product_details, \
show_dlg_help_add_sale, \
save_product_from_sale, \
remove_product_from_sale
#add_product_details
#products_details, \
#sku_products, \

#from sales import products_stores_search_urls
#from products import autocomplete_urls
from sales import \
search_urls, \
autocomplete_urls

urlpatterns = [
  url(r'^add', add, name='add-sale'),
  url(r'^do-add', do_add, name='do-add-sale'),
  url(r'^find', find, name='find-sale'),
  url(r'^do-find', do_find, name='do-find-sale'),
  url(r'^list-all', do_view_all, name='list-all-sales'),
  url(r'^edit', edit, name='edit-sale'),
  url(r'^do-edit', do_edit, name='do-edit-sale'),
  url(r'^delete', delete, name='delete-sale'),
  url(r'^do-delete', do_delete, name='do-delete-sale'),
  url(r'^view-details', view_details, name='view-details-sale'),
  url(r'^confirmed-delete', delete_sale, name='confirmed-delete-sale'),
  url(r'^update', update, name='update-sale'),
  url(r'^search/', include(search_urls.urlpatterns)),
  url(r'^product-details', product_details, name='product-details-sale'),
  #url(r'^sku-products', sku_products, name='sku-products-sale'),
  url(r'^show-sold-products', show_sold_products, name='show-sold-products'),
  url(r'^view-product-details', view_product_details, name='view-product-details'),
  url(r'^view-selected-product-details', view_selected_product_details, name='view-selected-product-details'),
  url(r'^dlg-help-add-sale', show_dlg_help_add_sale, name='dlg-help-add-sale'),
  url(r'^save-product-from-sale', save_product_from_sale, name='save-product-from-sale'),
  url(r'^remove-product-from-sale', remove_product_from_sale, name='remove-product-from-sale'),
  url(r'^autocomplete/', include(autocomplete_urls.urlpatterns)),
]