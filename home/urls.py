from django.conf.urls import url

from .views import retrieve_most_visited_shop, \
retrieve_most_visited_shops

urlpatterns = [
  url(r'^retrieve-most-visited-shop/', retrieve_most_visited_shop, name='retrieve-most-visited-shop-home'),
  url(r'^most-visited-shops/', retrieve_most_visited_shops, name='most-visited-shops-home'),
]