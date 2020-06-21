from django.conf.urls import url

from . autocomplete_views import \
my_stores_autocomplete

urlpatterns = [
  url(r'^my-stores', my_stores_autocomplete, name='my-stores-autocomplete'),
]