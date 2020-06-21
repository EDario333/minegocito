from django.conf.urls import url, include

from . search_views import \
by_rfc, by_email

urlpatterns = [
	url(r'^by-rfc', by_rfc, name='search-customer-by-rfc'),
	url(r'^by-email', by_email, name='search-customer-by-email'),
]