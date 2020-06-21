from django.conf.urls import url

from . autocomplete_views import \
shops_categories_autocomplete

urlpatterns = [
  url(r'^shops', shops_categories_autocomplete, name='shops-categories-autocomplete'),
]