from django.conf.urls import url

from . autocomplete_views import \
my_customers_autocomplete

urlpatterns = [
  url(r'^my-customers', my_customers_autocomplete, name='my-customers-autocomplete'),
]