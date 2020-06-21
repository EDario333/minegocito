# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse#, HttpResponse

from django.views.generic.list import ListView

from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from django.utils.translation import gettext as _

import json

class PermissionsView(ListView):
	object_list = Permission.objects.none()
	permissions_user = Permission.objects.none()
	permissions_user_group = []
	permissions_id_user_group = []

	def __init__(self, user=None, *args, **kwargs):
		super(PermissionsView, self).__init__(*args, **kwargs)
		self.object_list = Permission.objects.none()
		self.permissions_user = Permission.objects.none()
		self.permissions_user_group = []
		self.permissions_id_user_group = []
		if user is not None:
			#self.permissions_user = Permission.objects.filter(user=user)
			user = User.objects.get(pk=user)
			self.permissions_user = user.user_permissions.all()
			groups = user.groups.all()
			#print('********groups*******')
			#print(groups)
			for group in groups:
				permissions = group.permissions.all()
				self.permissions_user_group.append(permissions)
				for permission in permissions:
					self.permissions_id_user_group.append(permission.id)

		self.object_list = Permission.objects.all()

def get_permissions(request):
	if request.method == 'GET':
		#permissions = Permission.objects.all()
		user = request.GET.get('user', None)
		view = PermissionsView(user=user)
		permissions = view.object_list
		permissions_user = view.permissions_user
		permissions_user_group = view.permissions_user_group
		permissions_id_user_group = view.permissions_id_user_group

		return JsonResponse({'status': 'success'}), permissions, permissions_user, permissions_user_group, permissions_id_user_group

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg}), None

def get_permissions_html(request):
	result, permissions, permissions_user, permissions_user_group, permissions_id_user_group = get_permissions(request)
	result = json.loads(result.content.decode())

	if result['status'] == 'success':
		if len(permissions) > 0:
			html = '<p>'
			html += _('Make a click to expand_collapse the list')
			html += '.</p>'

			html += '<p id="parSelectAll">'
			html += 	'<a href="#" id="actSelectall">'
			html += 	_('Select all') + '</a>'
			html += '</p>'

			html += '<p id="parSelectNone">'
			html += 	'<a href="#" id="actSelectNone">'
			html += 	_('Select none') + '</a>'
			html += '</p>'

			html += '<div class="panel-group">'
			ct = None
			inner_menu_opened = False

			for permission in permissions:
				if permission.content_type != ct:
					ct = permission.content_type
					lbl = permission.content_type.app_label
					icon = ''
					if not '[icon=' in lbl:
						continue

					icon = lbl[lbl.index('[icon=') + len('[icon='):lbl.index(']')]
					lbl = lbl[:lbl.index('[')]

					if inner_menu_opened:
						html += '</div></div></div>'

					id_str = str(permission.content_type.id)
					html += '<div class="panel panel-default" id="'
					html += 'module' + id_str + '">'
					html += '<div class="panel-heading">'
					html += 	'<a href="#permissions' + id_str + '" data-toggle="collapse" '
					html +=   'aria-controls="permissions' + id_str + '" data-parent="#module' + id_str + '">'
					html += 	'<i class="material-icons">' + icon + '</i>'
					html += 	lbl + '</a>'
					html += '</div>'
					html += '<div class="panel-collapse collapse" '
					html += 'id="permissions' + id_str + '">'
					html += '<div class="panel-body">'

					#html += '<p class="select-all">'
					html += '<a href="#" class="select-all-group select-all" id="actSelectAllGroup' + id_str + '" '
					html += 'style="text-decoration: none;">'
					html += _('Select all') + '<br /><br /></a>'#</p>'

					#html += '<p class="select-none">'
					html += '<a href="#" class="select-none-group select-none" id="actSelectNoneGroup' + id_str + '" '
					html += 'style="text-decoration: noneM">'
					html += _('Select none') + '<br /><br /></a>' #</p>'
					inner_menu_opened = True
				else:
					id_perm = str(permission.id)
					#if permission in permissions_user or permission.id in permissions_id_user_group:
						#html += '<input type="checkbox" class="group' + id_str + ' checked" name="permissions" '
					#else:
					html += '<input type="checkbox" class="group' + id_str + '" name="permissions" '
					html += 'id="permission' + id_perm + '" '
					if permission in permissions_user or permission.id in permissions_id_user_group:
						html += 'checked="true" '
					html += '/><label for="permission' + id_perm + '">'
					html += permission.name + '</label><br />'

			html += '</div>'
		else:
			html = _('There are not any permission')

		return JsonResponse({'status': 'success', 'html': html})

	return json.dumps(result)