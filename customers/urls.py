from django.conf.urls import url, include

from . views import \
add, \
do_add, \
find, \
do_find, \
do_view_all, \
delete, \
do_delete, \
edit, \
do_edit, \
view_details, \
delete_customer, \
update

from customers import search_urls
from customers import autocomplete_urls

urlpatterns = [
	url(r'^add', add, name='add-customer'),
	url(r'^do-add', do_add, name='do-add-customer'),
	url(r'^find', find, name='find-customer'),
	url(r'^do-find', do_find, name='do-find-customer'),
	url(r'^list-all', do_view_all, name='list-all-customers'),
	url(r'^edit', edit, name='edit-customer'),
	url(r'^do-edit', do_edit, name='do-edit-customer'),
	url(r'^delete', delete, name='delete-customer'),
	url(r'^do-delete', do_delete, name='do-delete-customer'),
	url(r'^view-details', view_details, name='view-details-customer'),
	url(r'^confirmed-delete', delete_customer, name='confirmed-delete-customer'),
	url(r'^update', update, name='update-customer'),
	url(r'^search/', include(search_urls.urlpatterns)),
	url(r'^autocomplete/', include(autocomplete_urls.urlpatterns)),
]