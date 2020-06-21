from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction

from django.db.models import Q

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from .forms import FrmUsers, FrmUserProfile
from .models import Users, Ratings
from users.views import register

import json

def get_users_created_by_user(request):
	my_user = Users.objects.get(pk=request.user)
	users = Users.objects.filter(created_by_user=my_user, dropped=False)

	return users

def add(request):
	context = {}
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	context['itm_menu'] = itm_menu
	url='users/admin/add.html'

	if request.method == 'GET':
		frm = FrmUsers(title=_('Add user'), action='/users/admin/do-add', btn_label=_('Save'), icon_btn_submit='save')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['app_version'] = app_version

		counter_users=len(get_users_created_by_user(request))
		limit=1

		if app_version==_('Free version'):
			if counter_users>=limit:
				url='users/admin/add-free-version-limited.html'
		elif _('Basic version') in app_version:
			limit=3
			if counter_users>=limit:
				url='users/admin/add-basic-version-limited.html'
		elif _('Pro version') in app_version:
			limit=6
			if counter_users>=limit:
				url='users/admin/add-pro-version-limited.html'
		elif _('Advanced version') in app_version:
			limit=60
			if counter_users>=limit:
				url='users/admin/add-advanced-version-limited.html'

	return render(request, url, context=context)

def find(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_users_created_by_user(request)) < 1:
			return render(request, 'users/admin/user-have-no-users-created.html', context={'itm_menu': itm_menu})

		frm = FrmUsers(title=_('Find user'), action='/users/admin/do-find', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'users/admin/find.html', context=context)

def do_add(request):
	frm = FrmUsers(title=_('Add user'), action='/users/admin/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The user can not be saved')
	context['level'] = 'error'

	if request.method == 'POST':
		app_version = request.POST['app_version']
		itm_menu = request.POST.get('itm_menu', '')
		context['itm_menu'] = itm_menu

		'''
		if app_version == _('Free version'):
			if get_users_created_by_user(request) > 0:
				return render(request, 'users/add-free-version-limited.html', context={'itm_menu': itm_menu})
		'''
		context['app_version'] = app_version

		result = register(request)
		'''
		if request.status_code == 200:
			context['level'] = 'success'
			context['msg'] = _('User account has been successfully created')
		'''
		context['level'] = 'success'
		context['msg'] = _('User account has been successfully created')

	return render(request, 'users/admin/add.html', context=context)

def __generic_find_view__(request, can_delete=False, can_edit=False, view_all=False):
	frm = FrmUsers(title=_('Find user'), action='/users/admin/do-find', btn_label=_('Find'), icon_btn_submit='search')
	context = {}
	context['msg'] = _('We can not find any user matching with your query options')
	context['level'] = 'error'
	users = Users.objects.none()
	itm_menu = request.POST.get('itm_menu', request.GET.get('itm_menu', ''))
	context['itm_menu'] = itm_menu
	#context['url_view_all'] = '/users/list-all/'

	# Retrieve the user logged in
	my_user = Users.objects.get(pk=request.user)

	if request.method == 'POST':
		try:
			app_version = request.POST.get('app_version', _('Free version'))
			#itm_menu = request.POST.get('itm_menu', '')
			#context['itm_menu'] = itm_menu
			context['app_version'] = app_version

			search_by = {
				'last_name__icontains': False, 
				'mothers_last_name__icontains': False, 
				'first_name__icontains': False, 
				'middle_name__icontains': False, 
				'email__icontains': False
			}
			
			ln = request.POST.get('last_name', None)
			if ln and ln is not None and len(ln.strip()) > 0:
				search_by['last_name__icontains'] = ln.strip()

			mln = request.POST.get('mothers_last_name', None)
			if mln and mln is not None and len(mln.strip()) > 0:
				search_by['mothers_last_name__icontains'] = mln.strip()

			fn = request.POST.get('first_name', None)
			if fn and fn is not None and len(fn.strip()) > 0:
				search_by['first_name__icontains'] = fn.strip()

			mn = request.POST.get('middle_name', None)
			if mn and mn is not None and len(mn.strip()) > 0:
				search_by['middle_name__icontains'] = mn.strip()

			email = request.POST.get('email', None)
			if email and email is not None and len(email.strip()) > 0:
				search_by['email__icontains'] = email.strip()

			# Retrieve the user logged in
			#user = User.objects.get(email=request.POST.get('user', ''))
			#my_user = Users.objects.get(pk=user.id)
			#my_user = Users.objects.get(pk=request.user)

			query = Q(created_by_user=my_user) & Q(dropped=False)

			final_search_by = {}

			for criteria in search_by:
				if search_by[criteria]:
					final_search_by[criteria] = search_by[criteria]

			# Build the query...
			# See https://stackoverflow.com/questions/38131563/django-filter-with-or-condition-using-dict-argument
			# for more details
			from functools import reduce
			import operator
			query &= reduce(operator.or_, (Q(**d) for d in [dict([i]) for i in final_search_by.items()]))

			users = Users.objects.filter(query)

			#context['msg'] = _('We found {0} result(s) matching your query').format(len(users))
			#context['level'] = "success"
		except MultiValueDictKeyError:
			return redirect('/')
		except ObjectDoesNotExist:
			return redirect('/')
	elif view_all:
		app_version = request.GET.get('app_version', _('Free version'))
		itm_menu = request.GET.get('itm_menu', '')
		context['itm_menu'] = itm_menu
		context['app_version'] = app_version

		# Retrieve the user logged in
		#user = User.objects.get(email=request.GET.get('user', ''))
		#my_user = Users.objects.get(pk=user.id)
		#query = Q(created_by_user=my_user) & Q(dropped=False)
		users = Users.objects.filter(created_by_user=my_user, dropped=False)

	if len(users) > 0:
		context['users'] = users

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmUsers(title=_('Edit user'), action='/users/admin/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmUsers(title=_('Delete user'), action='/users/admin/do-delete', btn_label=_('Find'), icon_btn_submit='search')

	context['form'] = frm

	return render(request, 'users/admin/find.html', context=context)

def do_find(request):
	return __generic_find_view__(request)

def do_view_all(request):
	if request.method == 'GET':
		edit = request.GET.get('edit', False)
		delete = request.GET.get('delete', False)
		return __generic_find_view__(request, view_all=True, can_edit=edit, can_delete=delete)

	return __generic_find_view__(request, view_all=True, can_edit=False, can_delete=False)

def edit(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_users_created_by_user(request)) < 1:
			return render(request, 'users/admin/user-have-no-users-created.html', context={'itm_menu': itm_menu})

		frm = FrmUsers(title=_('Edit user'), action='/users/admin/do-edit', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'users/admin/find.html', context=context)

def do_edit(request):
	return __generic_find_view__(request, can_edit=True)

def delete(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_users_created_by_user(request)) < 1:
			return render(request, 'users/admin/user-have-no-users-created.html', context={'itm_menu': itm_menu})

		frm = FrmUsers(title=_('Delete user'), action='/users/admin/do-delete', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'users/admin/find.html', context=context)

def do_delete(request):
	return __generic_find_view__(request, can_delete=True)

def view_details(request):
	if request.method == 'GET':
		try:
			user = request.GET.get('obj', None)
			user = Users.objects.get(pk=user)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'user': user, 'can_edit': can_edit, 
				'can_delete': can_delete, 'itm_menu': itm_menu
			}

			return render(request, 'users/admin/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def confirm_delete(request):
	if request.method == 'GET':
		try:
			user = request.GET.get('user', None)
			user = Users.objects.get(pk=user)

			context = {
				'user': user, 
				'can_delete': True
			}

			return render(request, 'users/admin/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def delete_user(request):
	if request.method == 'POST':
		try:
			user = request.POST.get('user', None)
			user = Users.objects.get(pk=user)
			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			'''
			from datetime import datetime
			full_time = datetime.now()

			user.dropped = True
			user.dropped_at = full_time
			user.dropped_when = full_time
			user.dropped_reason = reason
			user.save()
			'''
			user.drop(reason=reason)

			frm = FrmUsers(title=_('Delete user'), action='/users/admin/do-delete', btn_label=_('Find'), icon_btn_submit='search')
			#app_version = request.GET['app_version']
			#context['form'] = frm
			#context['itm_menu'] = itm_menu

			context = {
				'level': 'success',
				'msg': _('The user has been deleted successfully'),
				'itm_menu': itm_menu,
				'form': frm
			}

			return render(request, 'users/admin/find.html', context=context)
			#return find(request)
			#return redirect('/users/find')
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def update(request):
	if request.method == 'POST':
		try:
			module = request.POST.get('module', None)
			if module is None:
				passw=request.POST.get('password', None)
				valid_pass=__verify_my_current_password__(request.user,passw)
				valid_pass_=json.loads(valid_pass.content)
				if 'success' not in valid_pass_['status']:
					return valid_pass

				user = request.POST.get('user', None)
				user = Users.objects.get(email=user)
			else:
				user = request.POST.get('user', None)
				user = Users.objects.get(pk=user)

			ln = request.POST.get('last_name', None)
			mln = request.POST.get('mothers_last_name', None)
			fn = request.POST.get('first_name', None)
			mn = request.POST.get('middle_name', None)
			email = request.POST.get('email', None)
			profile_picture=request.FILES.get('profile_picture', None)
			new_pass=request.POST.get('new_password', None)

			if new_pass and new_pass is not None:
				user.password=make_password(new_pass)

			user.last_name = ln
			user.mothers_last_name = mln
			user.first_name = fn
			user.middle_name = mn
			user.email = email
			user.username=email
			if profile_picture is not None:
				user.profile_picture=profile_picture
			# if profile_picture is None:
			# 	user.profile_picture='/static/imgs/user.png'
			# else:
			# 	user.profile_picture=profile_picture

			#module = request.POST.get('module', None)
			if module and module is not None and 'MY_ADMIN_MODULE' in module.upper():
				usergroup = request.POST.get('usergroup', None)
				permissions = request.POST.get('permissions', None)

				if usergroup and usergroup is not None and len(usergroup.strip()) > 0:
					user.groups.clear()
					user.user_permissions.clear()
					user.groups.add(usergroup)
				else:
					user.groups.clear()

				if permissions and permissions is not None and len(permissions.strip()) > 0:
					permissions = permissions.split(',')
					user.groups.clear()
					user.user_permissions.clear()
					user.user_permissions.set(permissions)
				else:
					user.user_permissions.clear()

			user.save()
			msg = _('The user has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg, 'new_profile_picture': user.static_profile_picture})
		except ObjectDoesNotExist:
			msg = _('The user you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def change_my_profile_picture(request):
	if request.method == 'POST':
		try:
			#user = Users.objects.get(pk=request.user)
			user = Users.objects.get(username=request.user)
		except ObjectDoesNotExist:
			try:
				user = Users.objects.get(email=request.user)
			except ObjectDoesNotExist:
				msg = _('The user you are trying to update does not exist')
				return JsonResponse({'status': 'error', 'msg': msg})
		profile_picture=request.FILES.get('profile_picture', None)
		user.profile_picture=profile_picture

		user.save()
		msg = _('The user has been updated successfully')

		return JsonResponse({'status': 'success', 'msg': msg, 'new_profile_picture': user.static_profile_picture})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def change_top_bar_theme(request):
	if request.method == 'GET':
		theme = request.GET.get('theme', 'red')
		try:
			usr = Users.objects.get(pk=request.user)
			usr.top_bar_theme = theme
			usr.save()
			msg = _('The user has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The user you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def load_my_top_bar_theme(request):
	if request.method == 'GET':
		try:
			usr = Users.objects.get(pk=request.user)
			return JsonResponse({'status': 'success', 'theme': usr.top_bar_theme})
		except ObjectDoesNotExist:
			msg = _('The user you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def profile(request):
	if request.method == 'GET':
		try:
			my_user=Users.objects.get(pk=request.user)
		except ObjectDoesNotExist:
			msg = _('You do not have permission to perform this request')
			return JsonResponse({'status': 'error', 'msg': msg})

		frm=FrmUserProfile(user=my_user,title=_('My user profile'), action='/users/admin/update', btn_label=_('Save'), icon_btn_submit='save')
		context={'user': request.user, 'form': frm, 'user': my_user}
		return render(request, 'users/profile/index.html', context=context)

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def __verify_my_current_password__(user, passw):
	if user.check_password(passw):
		return JsonResponse({'status': 'success', 'msg': _('Password valid')})
	return JsonResponse({'status': 'error', 'msg': _('Wrong password')})

def verify_my_current_password(request):
	if request.method == 'GET':
		passw=request.GET.get('password', None)
		return __verify_my_current_password__(request.user, passw)
		
		# try:
		# 	if request.user.check_password(passw):
		# 		return JsonResponse({'status': 'success', 'msg': _('')})
		# except ObjectDoesNotExist:
		# 	msg = _('You do not have permission to perform this request')
		# 	return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def automatic_updates(request):
	if request.method == 'GET':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		automatic_updates='true' in request.GET.get('automatic_updates',True)

		try:
			my_u=Users.objects.get(username=request.user)
		except ObjectDoesNotExist:
			try:
				my_u=Users.objects.get(email=request.user)
			except ObjectDoesNotExist:
				return JsonResponse({'status': 'error', 'msg': _('The user you are trying to update does not exist')})

		my_u.automatic_updates=automatic_updates
		my_u.save()
		return JsonResponse({'status': 'success', 'msg': _('The user has been updated successfully')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

def save_rating(request):
	if request.method == 'POST':
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

		rating=request.POST.get('rating', None)
		comments=request.POST.get('comments', None)

		if rating is None or len(rating.strip())<1:
			rating=None

		try:
			#my_u=Users.objects.get(email=request.user)
			my_u=Users.objects.get(username=request.user)
			my_u.has_rated=True

			rating=Ratings(user=my_u,rating=rating,comments=comments)

			with transaction.atomic():
				my_u.save()
				rating.save()
				return JsonResponse({'status': 'success', 'msg': _('Thank you so much for your comments and for rate us')})

		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The user you are trying to update does not exist')})

		return JsonResponse({'status': 'success', 'msg': _('The user has been updated successfully')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})