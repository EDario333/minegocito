from django.conf.urls import url

from .views_autocomplete import \
my_shops_autocomplete

urlpatterns = [
  url(r'^my-shops', my_shops_autocomplete, name='my-shops'),
]