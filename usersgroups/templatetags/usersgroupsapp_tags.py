# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Library

from django.utils.translation import gettext as _

from usersgroups.views import UsersGroupsView

register = Library()

@register.inclusion_tag('users/admin/assign-group.html', takes_context=True)
def user_assign_group(context):
	request = context['request']

	view = UsersGroupsView()
	#objs = view.get_context_data()['object_list']
	groups = view.object_list

	return {'request': request, 'groups': groups}