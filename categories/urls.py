from django.conf.urls import url, include

from categories import autocomplete_urls

urlpatterns = [
  url(r'^autocomplete/', include(autocomplete_urls.urlpatterns)),
]