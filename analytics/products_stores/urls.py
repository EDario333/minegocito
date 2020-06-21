from django.conf.urls import url, include

from . views import \
index, by_range, by_product, by_user, by_brand, by_store, \
advanced_cfg_by_range, \
advanced_cfg_by_product, \
advanced_cfg_by_users, \
advanced_cfg_by_brand, \
advanced_cfg_by_store, \
all_products, all_users, all_brands, all_stores

urlpatterns = [
  url(r'^$', index, name='index-analytics-products-stores'),
  url(r'^by-range/', by_range, name='analytics-products-stores-by-range'),

  url(r'^by-product/', by_product, name='analytics-products-stores-by-product'),
  url(r'^all-products/', all_products, name='analytics-products-stores-all-products'),

  url(r'^by-user/', by_user, name='analytics-products-stores-by-user'),
  url(r'^all-users/', all_users, name='analytics-products-stores-all-users'),

  url(r'^by-brand/', by_brand, name='analytics-products-stores-by-brand'),
  url(r'^all-brands/', all_brands, name='analytics-products-stores-all-brands'),

  url(r'^by-store/', by_store, name='analytics-products-stores-by-store'),
  url(r'^all-stores/', all_stores, name='analytics-products-stores-all-stores'),

  url(r'^advanced-cfg-by-range/', advanced_cfg_by_range, name='analytics-products-stores-advanced-cfg-by-range'),
  url(r'^advanced-cfg-by-product/', advanced_cfg_by_product, name='analytics-products-stores-advanced-cfg-by-product'),
  url(r'^advanced-cfg-by-users/', advanced_cfg_by_users, name='analytics-products-stores-advanced-cfg-by-users'),
  url(r'^advanced-cfg-by-brand/', advanced_cfg_by_brand, name='analytics-products-stores-advanced-cfg-by-brand'),
  url(r'^advanced-cfg-by-store/', advanced_cfg_by_store, name='analytics-products-stores-advanced-cfg-by-store'),
]