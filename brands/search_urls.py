from django.conf.urls import url, include

from . search_views import \
by_name

urlpatterns = [
  url(r'^by-name', by_name, name='search-brand-by-name'),
]