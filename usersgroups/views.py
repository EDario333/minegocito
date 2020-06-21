# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse#, HttpResponse

from django.core.serializers import serialize

from django.views.generic.list import ListView

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

from django.utils.translation import gettext as _

import json

class UsersGroupsView(ListView):
	object_list = Group.objects.none()

	def __init__(self, *args, **kwargs):
		super(UsersGroupsView, self).__init__(*args, **kwargs)
		self.object_list = Group.objects.all()

def get_permissions_group(request):
	if request.method == 'GET':
		group = request.GET.get('group', None)

		if group and group is not None:
			permissions = Permission.objects.filter(group=group)
			#permissions = serialize('json', permissions)

			return JsonResponse({'status': 'success'}), permissions

		return JsonResponse({'status': 'error', 'msg': _('The permissions for the group can not retrieve')}), None

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg}), None

def get_permissions_group_html(request):
	result, permissions = get_permissions_group(request)
	result = json.loads(result.content.decode())

	if result['status'] == 'success':
		#permissions = result['permissions']
		if len(permissions) > 0:
			#html = '<div class="menu">'
			#html += '<div class="slimScrollDiv" style="position: relative; overflow: hidden; width: auto; height: 571px;">'
			#html += '<ul style="list-style: none" class="list">'
			html = '<p>'
			html += _('Make a click to expand_collapse the list')
			html += '.</p>'
			html += '<div class="panel-group">'
			ct = None
			inner_menu_opened = False

			for permission in permissions:
				if permission.content_type != ct:
					ct = permission.content_type
					lbl = permission.content_type.app_label
					icon = ''
					if '[icon=' in lbl:
						icon = lbl[lbl.index('[icon=') + len('[icon='):lbl.index(']')]
						lbl = lbl[:lbl.index('[')]

					if inner_menu_opened:
						html += '</div></div></div>'

					'''
					html += '<li><a href="#" onclick="return false;"'
					html += 'class="menu-toggle waves-effect waves-block">'
					html += '<i class="material-icons">' + icon + '</i>'
					html += lbl + '<a></li>'
					html += '<ul class="ml-menu" style="display: block;">'
					'''
					id_str = str(permission.content_type.id)
					html += '<div class="panel panel-default" id="'
					html += 'groupmodule' + id_str + '">'
					html += '<div class="panel-heading">'
					html += 	'<a href="#grouppermissions' + id_str + '" data-toggle="collapse" '
					html +=   'aria-controls="grouppermissions' + id_str + '" data-parent="#groupmodule' + id_str + '">'
					html += 	'<i class="material-icons">' + icon + '</i>'
					html += 	lbl + '</a>'
					html += '</div>'
					html += '<div class="panel-collapse collapse" '
					html += 'id="grouppermissions' + id_str + '">'
					html += '<div class="panel-body">'
					inner_menu_opened = True
				else:
					'''
					html += '<li>'
					html += '<i class="material-icons">check</i>'
					html += permission.name + '</li>'
					'''
					html += '<i class="material-icons">check</i>'
					html += permission.name + '<br />'

			#html += '</ul>'
			#html += '</div>'
			html += '</div>'
		else:
			html = _('This group does not have any permission')

		return JsonResponse({'status': 'success', 'html': html})

	return json.dumps(result)