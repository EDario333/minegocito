from django.conf.urls import url

from . purchased_products_views import \
save_purchased_product

urlpatterns = [
  url(r'^save/product', save_purchased_product, name='purchases-purchased-products-save-product'),
]