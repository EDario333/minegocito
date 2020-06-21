from django.conf.urls import url, include

from . contact_persons_views import \
edit, \
delete_all, \
update, \
delete_contact_person

urlpatterns = [
  url(r'^edit', edit, name='edit-provider-contact-person'),
  url(r'^delete-all', delete_all, name='delete-provider-all-contact-persons'),
  url(r'^update', update, name='update-provider-contact-person'),
  url(r'^confirmed-delete', delete_contact_person, name='confirmed-delete-provider-contact-person'),
]