from django.conf.urls import url, include

from . search_views import \
by_identifier, \
by_unique_sale_user

urlpatterns = [
  url(r'^by-identifier', by_identifier, name='search-sale-by-identifier'),
  url(r'^by-unique-sale-user', by_unique_sale_user, name='search-sale-by-unique-sale-user'),
]