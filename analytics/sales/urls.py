from django.conf.urls import url, include

from . views import \
index, by_range, by_customer, by_user, \
by_product, by_brand, by_shop, \
advanced_cfg_by_range, \
advanced_cfg_by_customers, \
advanced_cfg_by_users, \
advanced_cfg_by_products, \
advanced_cfg_by_brands, \
advanced_cfg_by_shops, \
all_customers, all_users, all_products, all_brands, all_shops

urlpatterns = [
  url(r'^$', index, name='index-analytics-sales'),
  url(r'^by-range/', by_range, name='analytics-sales-by-range'),
  url(r'^by-customer/', by_customer, name='analytics-sales-by-customer'),
  url(r'^all-customers/', all_customers, name='analytics-sales-all-customers'),
  url(r'^by-user/', by_user, name='analytics-sales-by-user'),
  url(r'^all-users/', all_users, name='analytics-sales-all-users'),
  url(r'^by-product/', by_product, name='analytics-sales-by-product'),
  url(r'^all-products/', all_products, name='analytics-sales-all-products'),
  url(r'^by-brand/', by_brand, name='analytics-sales-by-brand'),
  url(r'^all-brands/', all_brands, name='analytics-sales-all-brands'),
  url(r'^by-shop/', by_shop, name='analytics-sales-by-shop'),
  url(r'^all-shops/', all_shops, name='analytics-sales-all-shops'),
  url(r'^advanced-cfg-by-range/', advanced_cfg_by_range, name='analytics-sales-advanced-cfg-by-range'),
  url(r'^advanced-cfg-by-customers/', advanced_cfg_by_customers, name='analytics-sales-advanced-cfg-by-customers'),
  url(r'^advanced-cfg-by-users/', advanced_cfg_by_users, name='analytics-sales-advanced-cfg-by-users'),
  url(r'^advanced-cfg-by-products/', advanced_cfg_by_products, name='analytics-sales-advanced-cfg-by-products'),
  url(r'^advanced-cfg-by-brands/', advanced_cfg_by_brands, name='analytics-sales-advanced-cfg-by-brands'),
  url(r'^advanced-cfg-by-shops/', advanced_cfg_by_shops, name='analytics-sales-advanced-cfg-by-shops'),
]