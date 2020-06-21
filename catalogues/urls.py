from django.conf.urls import url

from . views import \
cities_autocomplete, \
search_city_by_name

urlpatterns = [
	url(r'^cities/$', cities_autocomplete, name='cities-autocomplete'),
	url(r'^cities/search-by-name$', search_city_by_name, name='search-city-by-name'),
]