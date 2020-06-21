from django.conf.urls import url

from .views import get_msg, get_msgs

urlpatterns = [
  url(r'^translate/', get_msg, name='msg'),
  url(r'^many/', get_msgs, name='many'),
]