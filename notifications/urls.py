from django.conf.urls import url

from . views import \
mark_as_read, retrieve_user_notifications, change_cfg, \
view_all_notifications, remove_notif_completely, mark_as_unread

urlpatterns = [
	url(r'^$', view_all_notifications, name='view-all-notifications'),
  url(r'^mark-as-read', mark_as_read, name='mark-notification-as-read'),
  url(r'^mark-as-unread', mark_as_unread, name='mark-notification-as-unread'),
  url(r'^retrieve-user-notifications/', retrieve_user_notifications, name='retrieve-user-notifications'),
  url(r'^change-cfg/', change_cfg, name='change-cfg'),
  url(r'^remove-notification-completely/', remove_notif_completely, name='remove-notification-completely'),
]