from django.conf.urls import url

from . views import \
get_permissions_html

urlpatterns = [
	url(r'^get-permissions', get_permissions_html, name='get-permissions'),
]