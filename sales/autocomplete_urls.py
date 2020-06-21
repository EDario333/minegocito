from django.conf.urls import url

from . autocomplete_views import \
my_sales_query_product_autocomplete

urlpatterns = [
  url(r'^query-products', my_sales_query_product_autocomplete, name='query-products-sales-autocomplete'),
]