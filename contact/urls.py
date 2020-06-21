from django.conf.urls import url

from .views import index, send_message

urlpatterns = [
  url(r'^$', index, name='index'),
  url(r'^send-message/', send_message, name='send-message-contact'),
]