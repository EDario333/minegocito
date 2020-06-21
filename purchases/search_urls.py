from django.conf.urls import url#, include

from . search_views import \
by_identifier, \
by_unique_purchase_user, \
by_product_sku, \
by_product_name

urlpatterns = [
  url(r'^by-identifier', by_identifier, name='search-purchase-by-identifier'),
  url(r'^by-unique-purchase-user', by_unique_purchase_user, name='search-purchase-by-unique-purchase-user'),
  url(r'^by-product-sku', by_product_sku, name='search-purchase-by-product-sku'),
  url(r'^by-product-name', by_product_name, name='search-purchase-by-product-name'),
]