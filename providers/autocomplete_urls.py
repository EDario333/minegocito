from django.conf.urls import url

from . autocomplete_views import \
my_providers_autocomplete

urlpatterns = [
	url(r'^my-providers', my_providers_autocomplete, name='my-providers-autocomplete'),
]