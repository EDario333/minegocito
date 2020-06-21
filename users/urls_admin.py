from django.conf.urls import url, include

from . views_my_admin import \
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
delete_user, \
update, \
change_top_bar_theme, \
load_my_top_bar_theme, \
profile, \
verify_my_current_password, \
change_my_profile_picture, \
automatic_updates, \
save_rating

#from stores import search_urls
#from stores import autocomplete_urls

urlpatterns = [
  url(r'^add', add, name='add-user'),
  url(r'^do-add', do_add, name='do-add-user'),
  url(r'^find', find, name='find-user'),
  url(r'^do-find', do_find, name='do-find-user'),
  url(r'^list-all', do_view_all, name='list-all-users'),
  url(r'^edit', edit, name='edit-user'),
  url(r'^do-edit', do_edit, name='do-edit-user'),
  url(r'^delete', delete, name='delete-user'),
  url(r'^do-delete', do_delete, name='do-delete-user'),
  url(r'^view-details', view_details, name='view-details-user'),
  url(r'^confirmed-delete', delete_user, name='confirmed-delete-user'),
  url(r'^update', update, name='update-user'),
  url(r'^change-top-bar-theme', change_top_bar_theme, name='change-top-bar-theme'),
  url(r'^load-my-top-bar-theme', load_my_top_bar_theme, name='load-my-top-bar-theme'),
  url(r'^my-profile', profile, name='my-profile'),
  url(r'^verify-my-current-password', verify_my_current_password, name='verify-my-current-password'),
  url(r'^change-my-profile-picture', change_my_profile_picture, name='change-my-profile-picture'),
  url(r'^automatic-updates', automatic_updates, name='automatic-updates'),
  url(r'^save-rating', save_rating, name='save-rating'),
  #url(r'^search/', include(search_urls.urlpatterns)),
  #url(r'^autocomplete/', include(autocomplete_urls.urlpatterns)),
]