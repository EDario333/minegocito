# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

from django.core.exceptions import ObjectDoesNotExist

from django.utils.translation import gettext as _

from django.http import JsonResponse#, HttpResponse

from django.views.generic.list import ListView

from .models import UsersNotifications, Notifications
from users.models import Users

from datetime import datetime

dummy = _('Congratulations, you have finished the app initial tutorial')

class UserNotificationsView(ListView):
	user = None
	object_list = UsersNotifications.objects.none()

	def __init__(self, user=None, all=False, *args, **kwargs):
		super(UserNotificationsView, self).__init__(*args, **kwargs)
		self.user = user
		if not all:
			self.object_list = UsersNotifications.objects.filter(user=user,dropped=False,fully_dropped=False,done=False).order_by('-created_when', '-created_at')
			self.object_list = self.object_list[:5]
		else:
			self.object_list = UsersNotifications.objects.filter(user=user,fully_dropped=False).order_by('-created_when', '-created_at')

def mark_as_read(request):
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		notif_id = request.GET.get('notif', None)

		if notif_id is None:
			return JsonResponse({'status': 'error', 'msg': _('The requested operation cannot be performed')})

		try:
			un = UsersNotifications.objects.get(pk=notif_id)
			un.done = True
			un.save()
			'''
			unv = UserNotificationsView(user=request.user)
			context = {'notifications': unv.object_list}
			return render(request, 'dashboard/assets/top-bar/notifications.html', context=context)
			'''
			return JsonResponse({'status': 'success', 'msg': _('The user notification has been updated successfully')})
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('The requested operation cannot be performed')})

def mark_as_unread(request):
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		notif_id = request.GET.get('notif', None)

		if notif_id is None:
			return JsonResponse({'status': 'error', 'msg': _('The requested operation cannot be performed')})

		try:
			un = UsersNotifications.objects.get(pk=notif_id)
			un.done = False
			un.save()
			return JsonResponse({'status': 'success', 'msg': _('The user notification has been updated successfully')})
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('The requested operation cannot be performed')})

def retrieve_user_notifications(request):
	context={}
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		view = UserNotificationsView(user=request.user)
		notifs = view.object_list
		context['notifications']=notifs

	# return render(request, 'dashboard/assets/top-bar/updating-notifications.html', context=context)
	return render(request, 'notifications/updating-notifications.html', context=context)

def change_cfg(request):
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		show_notifs='true' in request.GET.get('show_notifications',True)

		try:
			my_u=Users.objects.get(username=request.user)
		except ObjectDoesNotExist:
			try:
				my_u=Users.objects.get(email=request.user)
			except ObjectDoesNotExist:
				return JsonResponse({'status': 'error', 'msg': _('The user you are trying to update does not exist')})
		my_u.show_notifications=show_notifs
		my_u.save()

		return JsonResponse({'status': 'success', 'msg': _('The user has been updated successfully')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

def view_all_notifications(request):
	context={}
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		view = UserNotificationsView(user=request.user,all=True)
		notifications = view.object_list
		context['notifications']=notifications

		return render(request, 'notifications/index.html', context=context)

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

def remove_notif_completely(request):
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		un=request.GET.get('notification', None)

		try:
			un=UsersNotifications.objects.get(pk=un)
			today=datetime.now()
			un.fully_dropped=True
			un.fully_dropped_at=today
			un.fully_dropped_when=today
			un.fully_dropped_reason=_('Removed by user')
			un.save()
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The object does not exist')})

		return JsonResponse({'status': 'success', 'msg': _('The notification was removed completely')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})