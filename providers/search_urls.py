from django.conf.urls import url, include

from . search_views import \
by_rfc, by_name, by_email

urlpatterns = [
	url(r'^by-rfc', by_rfc, name='search-provider-by-rfc'),
	url(r'^by-name', by_name, name='search-provider-by-name'),
	url(r'^by-email', by_email, name='search-provider-by-email'),
]