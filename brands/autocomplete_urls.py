from django.conf.urls import url

from . autocomplete_views import \
my_brands_autocomplete

urlpatterns = [
  url(r'^my-brands', my_brands_autocomplete, name='my-brands-autocomplete'),
]