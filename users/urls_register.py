from django.conf.urls import url

from . views import \
register

urlpatterns = [
  url(r'^$', register, name='app'),
  url(r'^fb', register, name='fb'),
  url(r'^google', register, name='google'),
]