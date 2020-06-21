from django.conf.urls import url

from . views import \
get_permissions_group_html

urlpatterns = [
	#url(r'^get-permissions-group', get_permissions_group, name='get-permissions-group'),
	url(r'^get-permissions-group', get_permissions_group_html, name='get-permissions-group'),
]