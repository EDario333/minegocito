from django.conf.urls import url

from . views import \
login

urlpatterns = [
  url(r'^$', login, name='login'),
  url(r'^fb', login, name='login-with-fb'),
  url(r'^google', login, name='login-with-google'),
]