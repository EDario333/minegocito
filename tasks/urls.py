from django.conf.urls import url

from . views import \
retrieve_user_tasks, remove_from_alerts, view_all_tasks, \
remove_task_completely, change_cfg

urlpatterns = [
	url(r'^$', view_all_tasks, name='view-all-tasks'),
  url(r'^retrieve-user-tasks/', retrieve_user_tasks, name='retrieve-user-tasks'),
  url(r'^remove-from-alerts/', remove_from_alerts, name='remove-from-alerts'),
  url(r'^remove-task-completely/', remove_task_completely, name='remove-task-completely'),
  url(r'^change-cfg/', change_cfg, name='change-cfg'),
]