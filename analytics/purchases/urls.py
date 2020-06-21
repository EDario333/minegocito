from django.conf.urls import url, include

from . views import \
index, by_range, by_provider, by_user, \
by_product, by_brand, by_shop, \
advanced_cfg_by_range, \
advanced_cfg_by_providers, \
advanced_cfg_by_users, \
advanced_cfg_by_products, \
advanced_cfg_by_brands, \
advanced_cfg_by_shops, \
all_providers, all_users, all_products, all_brands, all_shops

urlpatterns = [
  url(r'^$', index, name='index-analytics-purchases'),
  url(r'^by-range/', by_range, name='analytics-purchases-by-range'),
  url(r'^by-provider/', by_provider, name='analytics-purchases-by-provider'),
  url(r'^all-providers/', all_providers, name='analytics-purchases-all-providers'),
  url(r'^by-user/', by_user, name='analytics-purchases-by-user'),
  url(r'^all-users/', all_users, name='analytics-purchases-all-users'),
  url(r'^by-product/', by_product, name='analytics-purchases-by-product'),
  url(r'^all-products/', all_products, name='analytics-purchases-all-products'),
  url(r'^by-brand/', by_brand, name='analytics-purchases-by-brand'),
  url(r'^all-brands/', all_brands, name='analytics-purchases-all-brands'),
  url(r'^by-shop/', by_shop, name='analytics-purchases-by-shop'),
  url(r'^all-shops/', all_shops, name='analytics-purchases-all-shops'),
  url(r'^advanced-cfg-by-range/', advanced_cfg_by_range, name='analytics-purchases-advanced-cfg-by-range'),
  url(r'^advanced-cfg-by-providers/', advanced_cfg_by_providers, name='analytics-purchases-advanced-cfg-by-providers'),
  url(r'^advanced-cfg-by-users/', advanced_cfg_by_users, name='analytics-purchases-advanced-cfg-by-users'),
  url(r'^advanced-cfg-by-products/', advanced_cfg_by_products, name='analytics-purchases-advanced-cfg-by-products'),
  url(r'^advanced-cfg-by-brands/', advanced_cfg_by_brands, name='analytics-purchases-advanced-cfg-by-brands'),
  url(r'^advanced-cfg-by-shops/', advanced_cfg_by_shops, name='analytics-purchases-advanced-cfg-by-shops'),
]