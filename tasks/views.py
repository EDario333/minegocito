# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import JsonResponse#, HttpResponse

from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

'''
from django.contrib.auth.models import User
'''
from django.views.generic.list import ListView

from .models import UsersTasks
from users.models import Users

from datetime import datetime

dummy=_('Title dlg task already done')
dummy=_('Msg dlg task already done')
dummy=_('Btn goto anyway dlg task already done')
dummy=_('Btn remove this task dlg task already done')
dummy=_('This operation cannot be undone')
dummy=_('Prompt are you sure to continue')

class UserTasksView(ListView):
	user = None
	object_list = UsersTasks.objects.none()

	def __init__(self, user=None, all=False, *args, **kwargs):
		super(UserTasksView, self).__init__(*args, **kwargs)
		self.user = user
		# self.object_list = UsersTasks.objects.filter(user=user, percent__lt=100).order_by('created_when', 'created_at')
		if not all:
			self.object_list = UsersTasks.objects.filter(user=user,dropped=False,fully_dropped=False).order_by('percent', 'created_when', 'created_at')
		else:
			self.object_list = UsersTasks.objects.filter(user=user,fully_dropped=False).order_by('percent', 'created_when', 'created_at')

def remove_from_alerts(request):
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		task_id = request.GET.get('task', None)

		if task_id is None:
			return JsonResponse({'status': 'error', 'msg': _('The requested operation cannot be performed')})

		try:
			ut = UsersTasks.objects.get(pk=task_id)
			ut.drop(reason=_('The task was removed from alerts'))
			return JsonResponse({'status': 'success', 'msg': _('The user task has been updated successfully')})
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('The requested operation cannot be performed')})

def retrieve_user_tasks(request):
	context={}
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		view = UserTasksView(user=request.user)
		tasks = view.object_list
		context['tasks']=tasks

	# return render(request, 'dashboard/assets/top-bar/updating-tasks.html', context=context)
	return render(request, 'tasks/updating-tasks.html', context=context)

def view_all_tasks(request):
	context={}
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		view = UserTasksView(user=request.user,all=True)
		tasks = view.object_list
		context['tasks']=tasks

		# return render(request, 'dashboard/assets/top-bar/updating-tasks.html', context=context)
		return render(request, 'tasks/index.html', context=context)

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

def remove_task_completely(request):
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		ut=request.GET.get('task', None)

		try:
			ut=UsersTasks.objects.get(pk=ut)
			today=datetime.now()
			ut.fully_dropped=True
			ut.fully_dropped_at=today
			ut.fully_dropped_when=today
			ut.fully_dropped_reason=_('Removed by user')
			ut.save()
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The object does not exist')})

		return JsonResponse({'status': 'success', 'msg': _('The task was removed completely')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

def change_cfg(request):
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		show_tasks='true' in request.GET.get('show_tasks',True)

		try:
			my_u=Users.objects.get(username=request.user)
		except ObjectDoesNotExist:
			try:
				my_u=Users.objects.get(email=request.user)
			except ObjectDoesNotExist:
				return JsonResponse({'status': 'error', 'msg': _('The user you are trying to update does not exist')})
		my_u.show_tasks=show_tasks
		my_u.save()

		return JsonResponse({'status': 'success', 'msg': _('The user has been updated successfully')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})