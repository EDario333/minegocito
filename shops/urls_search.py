from django.conf.urls import url

from .views_search import \
search_by_name

urlpatterns = [
  url(r'^by-name', search_by_name, name='search-shop-by-name'),
]