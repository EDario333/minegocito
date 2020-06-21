from django.conf.urls import url

from . views import index, \
main_panel, \
processing, \
choose_app_version

urlpatterns = [
  url(r'^index', index, name='index'),
	url(r'^main-panel', main_panel, name='main-panel'),
	url(r'^processing', processing, name='processing'),
	url(r'^choose-app-version', choose_app_version, name='choose-app-version'),
]