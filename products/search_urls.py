from django.conf.urls import url, include

from . search_views import \
by_name, \
by_sku

urlpatterns = [
  url(r'^by-name', by_name, name='search-product-by-name'),
  url(r'^sku', by_sku, name='search-product-by-sku'),
]