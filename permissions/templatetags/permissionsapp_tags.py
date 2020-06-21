# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Library

from django.utils.translation import gettext as _

from permissions.views import PermissionsView

register = Library()

@register.inclusion_tag('users/admin/assign-permissions.html', takes_context=True)
def user_permissions(context):
	request = context['request']

	view = PermissionsView()
	#objs = view.get_context_data()['object_list']
	permissions = view.object_list

	if len(permissions) > 0:
		html = '<div class="panel-group">'
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
				inner_menu_opened = True
			else:
				id_perm = str(permission.id)
				html += '<input type="checkbox" name="permissions" '
				html += 'id="permission' + id_perm + '" />'
				html += '<label for="permission' + id_perm + '">'
				html += permission.name + '</label><br />'

		html += '</div>'
	else:
		html = _('There are not any permission')

	return {'request': request, 'permissions': permissions, 'html': html}