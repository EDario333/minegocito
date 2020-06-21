from django.conf.urls import url, include

import analytics.sales.urls, \
analytics.purchases.urls, \
analytics.products_stores.urls
#from . views import \

urlpatterns = [
  url(r'^sales/', include(analytics.sales.urls.urlpatterns)),
  url(r'^purchases/', include(analytics.purchases.urls.urlpatterns)),
  url(r'^products-stores/', include(analytics.products_stores.urls.urlpatterns)),
]