from django.conf.urls import url, include

from . products_stores_views_search import \
by_sku

urlpatterns = [
  url(r'^by-sku', by_sku, name='search-product-stored-by-sku'),
]