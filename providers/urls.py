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
delete_provider, \
update, \
new_contact_person, \
view_details_contact_person, \
show_contact_persons

from providers import search_urls
from providers import autocomplete_urls
from providers import contact_persons_urls

urlpatterns = [
  url(r'^add', add, name='add-provider'),
  url(r'^do-add', do_add, name='do-add-provider'),
  url(r'^find', find, name='find-provider'),
  url(r'^do-find', do_find, name='do-find-provider'),
  url(r'^list-all', do_view_all, name='list-all-providers'),
  url(r'^edit', edit, name='edit-provider'),
  url(r'^do-edit', do_edit, name='do-edit-provider'),
  url(r'^delete', delete, name='delete-provider'),
  url(r'^do-delete', do_delete, name='do-delete-provider'),
  url(r'^view-details', view_details, name='view-details-provider'),
  url(r'^confirmed-delete', delete_provider, name='confirmed-delete-provider'),
  url(r'^update', update, name='update-provider'),
  url(r'^new-contact-person', new_contact_person, name='new-contact-person-provider'),
  url(r'^search/', include(search_urls.urlpatterns)),
  url(r'^autocomplete/', include(autocomplete_urls.urlpatterns)),
  url(r'^details-contact-person', view_details_contact_person, name='view-details-contact-person-provider'),
  url(r'^show-contact-persons', show_contact_persons, name='show-contact-persons-provider'),
  url(r'^contact-persons/', include(contact_persons_urls.urlpatterns)),
]