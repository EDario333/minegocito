# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Library

from django.utils.translation import gettext as _

from tasks.views import UserTasksView

register = Library()

# @register.inclusion_tag('dashboard/assets/top-bar/tasks.html', takes_context=True)
@register.inclusion_tag('tasks/tasks.html', takes_context=True)
def user_tasks(context):
  request = context['request']

  view = UserTasksView(user=request.user)
  #objs = view.get_context_data()['object_list']
  tasks = view.object_list

  return {'request': request, 'tasks': tasks}
