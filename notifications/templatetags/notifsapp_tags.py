# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Library

from django.utils.translation import gettext as _

from notifications.views import UserNotificationsView

register = Library()

# @register.inclusion_tag('dashboard/assets/top-bar/notifications.html', takes_context=True)
@register.inclusion_tag('notifications/notifications.html', takes_context=True)
def user_notifications(context):
  request = context['request']

  view = UserNotificationsView(user=request.user)
  #objs = view.get_context_data()['object_list']
  notifs = view.object_list

  return {'request': request, 'notifications': notifs}
