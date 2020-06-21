from django.conf.urls import url

from users.views_autocomplete import \
users_autocomplete, \
users_shop_admins_autocomplete, \
my_users_autocomplete, \
users_store_admins_autocomplete, \
my_users_analytics_autocomplete

urlpatterns = [
  url(r'^all', users_autocomplete, name='users-autocomplete'),
  url(r'^my-users', my_users_autocomplete, name='my-users-autocomplete'),
  url(r'^users-analytics', my_users_analytics_autocomplete, name='my-users-analytics-autocomplete'),
  url(r'^shop-admins', users_shop_admins_autocomplete, name='users-shop-admins-autocomplete'),
  url(r'^store-admins', users_store_admins_autocomplete, name='users-store-admins-autocomplete'),
]