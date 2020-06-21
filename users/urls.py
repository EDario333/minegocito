from django.conf.urls import url, include

from . views import \
forgot_password, \
exist_user_account_by_email, \
confirm_user_account, \
notify_phishing, \
delete_user_account, \
approve_user_account, \
logout, \
reset_password, \
do_reset_password, \
disable_first_time_tutorial_for_user, \
check_first_time_login_for_user, \
check_first_tutorial_completed, \
update_step_first_tutorial, \
search_user_by_email

from users import urls_autocomplete, \
urls_login, \
urls_register, \
urls_admin

urlpatterns = [
  #url(r'^login', login, name='login'),
  url(r'^login/', include(urls_login.urlpatterns)),
  url(r'^register/', include(urls_register.urlpatterns)),
  #url(r'^register', register, name='register'),
  url(r'^forgot-password', forgot_password, name='forgot-password'),
  url(r'^exist-user-account-by-email', exist_user_account_by_email, name='exist-user-account-by-email'),
  url(r'^confirm-user-account/$', confirm_user_account, name='confirm-user-account'),
  url(r'^notify-phishing', notify_phishing, name='notify-phishing'),
  url(r'^delete-user-account', delete_user_account, name='delete-user-account'),
  url(r'^approve-user-account', approve_user_account, name='approve-user-account'),
  url(r'^logout', logout, name='logout'),
  url(r'^reset-password', reset_password, name='reset-password'),
  url(r'^do-reset-password', do_reset_password, name='do-reset-password'),
  url(r'^disable-first-time-tutorial-for-user', disable_first_time_tutorial_for_user, name='disable-first-time-tutorial-for-user'),
  url(r'^check-first-time-login-for-user', check_first_time_login_for_user, name='check-first-time-login-for-user'),
  url(r'^check-first-tutorial-completed', check_first_tutorial_completed, name='check-first-tutorial-completed'),
  url(r'^update-step-first-tutorial', update_step_first_tutorial, name='update-step-first-tutorial'),
  url(r'^autocomplete/', include(urls_autocomplete.urlpatterns)),
  url(r'^search-by-email$', search_user_by_email, name='search-user-by-email'),
  url(r'^admin/', include(urls_admin.urlpatterns)),
]