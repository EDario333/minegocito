"""minegocito URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from home import views as v_home

import users.urls
import dashboard.urls
import translator.urls
import appversions.urls
import shops.urls
import catalogues.urls
import notifications.urls
import stores.urls
import products.urls
import products.products_stores_urls
import brands.urls
import categories.urls
import usersgroups.urls
import permissions.urls
import purchases.urls
import providers.urls
import customers.urls
import sales.urls
import analytics.urls
import contact.urls
import about.urls
import home.urls
import tasks.urls
import agreements.urls
import newsletter.urls

urlpatterns = [
  url(r'^$', v_home.index, name='index'),
  url(r'^home/', include(home.urls)),
  url(r'^users/', include(users.urls)),
  url(r'^dashboard/', include(dashboard.urls)),
  url(r'^catalogues/', include(catalogues.urls)),
  url(r'^translator/', include(translator.urls)),
  url(r'^app-versions/', include(appversions.urls)),
  url(r'^shops/', include(shops.urls)),
  url(r'^stores/', include(stores.urls)),
  url(r'^notifications/', include(notifications.urls)),
  url(r'^products/', include(products.urls)),
  url(r'^products-stores/', include(products.products_stores_urls)),
  url(r'^brands/', include(brands.urls)),
  url(r'^categories/', include(categories.urls)),
  url(r'^users-groups/', include(usersgroups.urls)),
  url(r'^permissions/', include(permissions.urls)),
  url(r'^purchases/', include(purchases.urls)),
  url(r'^providers/', include(providers.urls)),
  url(r'^customers/', include(customers.urls)),
  url(r'^sales/', include(sales.urls)),
  url(r'^tasks/', include(tasks.urls)),
  url(r'^analytics/', include(analytics.urls)),
  url(r'^contact/', include(contact.urls)),
  url(r'^about/', include(about.urls)),
  url(r'^agreements/', include(agreements.urls)),
  url(r'^newsletter/', include(newsletter.urls)),
  path('admin/', admin.site.urls),
]

'''
from django.conf import settings

if settings.DEBUG:
  import debug_toolbar
  urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
  ] + urlpatterns
'''