from django.conf.urls import url

from . views_autocomplete import \
my_products_autocomplete

urlpatterns = [
  url(r'^my-products', my_products_autocomplete, name='my-products-autocomplete'),
]