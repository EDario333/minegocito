from django.shortcuts import render, redirect

# from django.db import transaction
from django.db import IntegrityError

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth import login as login_django

from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from django.utils.datastructures import MultiValueDictKeyError

#from django.db.models import Q

from django.http import JsonResponse, HttpResponse
import json

from .models import Users

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from utils import utils

from users import utils as users_utils

def exist_user_account_by_email(request):
	#if request.method == 'POST':
	exist_user, dummy1 = users_utils.exist_user_account_by_email(request)
	if exist_user:
		return JsonResponse({'level': 'error', 'msg': _('Email account already exists')})
	return JsonResponse({'passed': True})

	return redirect('/')

def login(request):
	if request.method == 'POST':
		email = request.POST['email']
		login_with_fb = request.POST.get('login_with_fb', False)
		login_with_google = request.POST.get('login_with_google', False)
		user = None

		if login_with_fb or login_with_google:
			user = users_utils.authenticate_using_email(email)
			if login_with_fb:
				password = user.fb_id[:8]
			else:
				password = user.google_id[:8]
		else:
			password = request.POST['password']			
			#user = authenticate(email=email, password=password)
			user = users_utils.authenticate_via_email(email, password)

		if not user or user is None:
			msg = _('User account does not exist')
			context = {
				'level': 'error',
				'msg': msg,
				'logged-in': False
			}
			#return redirect('/')

			if login_with_fb or login_with_google:
				return JsonResponse({'status': 'error', 'msg': msg})

			return render(request, 'home/index.html', context=context)
		else:
			# Check if the user account is active (on table 'auth_user')
			if not user.is_active:
				msg = _('User account has been disabled')
				context = {
					'level': 'error',
					'msg': msg,
					'logged-in': False
				}

				if login_with_fb or login_with_google:
					return JsonResponse({'status': 'error', 'msg': msg})

				return render(request, 'home/index.html', context=context)

			from .models import Users
			obj = Users.objects.get(pk=user.id)

			# Check if the user account wasn't dropped (on table 'users_users')
			if obj.dropped:
				msg = _('User account does not exist')
				context = {
					'level': 'error',
					'msg': msg,
					'logged-in': False
				}

				if login_with_fb or login_with_google:
					return JsonResponse({'status': 'error', 'msg': msg})

				return render(request, 'home/index.html', context=context)

			# Check if the user account is active (on table 'users_users')
			if obj.disabled:
				msg = _('User account has been disabled')
				context = {
					'level': 'error',
					'msg': msg,
					'logged-in': False
				}

				if login_with_fb or login_with_google:
					return JsonResponse({'status': 'error', 'msg': msg})

				return render(request, 'home/index.html', context=context)

			# Check if the email was confirmed (on table 'users_users')
			if not obj.email_confirmed:
				msg = _('The email address is not confirmed yet')
				context = {
					'level': 'error',
					'msg': msg,
					'logged-in': False
				}

				if login_with_fb or login_with_google:
					return JsonResponse({'status': 'error', 'msg': msg})

				return render(request, 'home/index.html', context=context)

			# Check if the email was approved (on table 'users_users')
			if not obj.email_approved:
				msg = _('The email address is not approved yet')
				context = {
					'level': 'error',
					'msg': msg,
					'logged-in': False
				}

				if login_with_fb or login_with_google:
					return JsonResponse({'status': 'error', 'msg': msg})

				return render(request, 'home/index.html', context=context)

			context = {}

			csrfmiddlewaretoken = request.POST['csrfmiddlewaretoken']

			# Check if still active the 'Free version'
			year_approved = obj.email_approved_when.year
			month_approved = obj.email_approved_when.month
			day_approved = obj.email_approved_when.day

			hour_approved = obj.email_approved_at.hour
			minute_approved = obj.email_approved_at.minute

			supported = datetime(year_approved, month_approved, day_approved, hour_approved, minute_approved)
			supported = supported + timedelta(days=15)

			if 'skip-verification-payment' not in request.POST:
				current = datetime.now()

				# Verify the user's payments
				from appversions.models import Payments
				#from django.core.exceptions import DoesNotExist

				try:
					payments = Payments.objects.filter(user=user.id)

					for payment in payments:
						expires = payment.get_expires_when()
						year = expires.year
						month = expires.month
						day = expires.day
						supported = datetime(year, month, day, payment.at.hour, payment.at.minute)

						if current > supported:
							payment.active = False
							payments = payments.exclude(id=payment.id)

				except ObjectDoesNotExist:
					payments = []

				#if payments and payments is not None:
				total_payments = len(payments)
				context['payments'] = payments
				context['total_payments'] = total_payments

				# Free version
				if total_payments < 1:
					context['app_version'] = _('Free version')

					supported = datetime(year_approved, month_approved, day_approved, hour_approved, minute_approved)
					supported = supported + timedelta(days=15)

					if current > supported:
						msg = _('Your free version has expired')
						context = {
							'level': 'error',
							'msg': msg,
							'logged-in': False
						}

						if login_with_fb or login_with_google:
							return JsonResponse({'status': 'error', 'msg': msg})

						return render(request, 'home/index.html', context=context)

					context['expires'] = supported
				elif total_payments == 1:
					context['app_version'] = payments[0].app.name
					expires = payments[0].get_expires_when()
					expires = datetime(expires.year, expires.month, expires.day, payments[0].at.hour, payments[0].at.minute)

					if current > expires:
						msg = _('Your license has expired')
						context['level'] = 'error'
						context['logged-in'] = False

						# We will try with the 'Free version'
						context['app_version'] = _('Free version')

						supported = datetime(year_approved, month_approved, day_approved, hour_approved, minute_approved)
						supported = supported + timedelta(days=15)

						if current > supported:
							msg += ', ' + _('Your free version has expired').lower()
							context['msg'] = msg

							if login_with_fb or login_with_google:
								return JsonResponse({'status': 'error', 'msg': msg})

							return render(request, 'home/index.html', context=context)
						else:
							expires = supported

					context['expires'] = expires
				else:
					context['show_modal'] = True
					context['modal_name'] = 'dlgChooseAppVersion'
					context['email'] = email
					context['password'] = password

					if login_with_fb or login_with_google:
						json_response = {
							'show_modal': True, 
							'modal_name': 'dlgChooseAppVersion', 
							'email': email, 
							'password': password
						}
						return JsonResponse(json_response)

					return render(request, 'home/index.html', context=context)
			else:
				context['app_version'] = request.POST['app-version']
				context['expires'] = request.POST['expires']

			from .models import UsersLoggedIn

			register_login = True

			try:
				dummy = UsersLoggedIn.objects.get(csrfmiddlewaretoken=csrfmiddlewaretoken)
				register_login = False
			except ObjectDoesNotExist:
				pass

			if register_login:
	    	# Get the remote IP address from the client
				x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

				if x_forwarded_for:
					ipaddress = x_forwarded_for.split(',')[-1].strip()
				else:
					ipaddress = request.META.get('REMOTE_ADDR')

				# Get user agent from the client
				user_agent = request.META.get('HTTP_USER_AGENT')

				#import datetime
				full_time = datetime.now()
				#csrfmiddlewaretoken = request.POST['csrfmiddlewaretoken']

				values = {
					'user_id': user.id,
	    		'ip': ipaddress,
	    		'user_agent': user_agent,
	    		'logged_when': full_time,
	    		'logged_at': full_time,
	    		'csrfmiddlewaretoken': csrfmiddlewaretoken
	    	}

				data = UsersLoggedIn.objects.create(**values)
				if data and data is not None:
					login_django(request, user)

					if login_with_fb or login_with_google:
						return JsonResponse({'app_version': context['app_version'], 'expires': context['expires']})

					context['user'] = user
					context['csrfmiddlewaretoken'] = csrfmiddlewaretoken
					context['my_user'] = obj

					obj.menu = users_utils.build_user_menu(obj)

					return render(request, 'dashboard/index.html', context=context)
				else:
					msg = _('I can not register your session') + '. '
					msg += _('Retry, and if the problem persist get in touch with the system administrator and report') + ': '
					msg += 'Error 004 at users.views@login'

					context={
						'level': 'error',
						'msg': msg,
						'logged-in': False
					}

					if login_with_fb or login_with_google:
						return JsonResponse({'status': 'error', 'msg': msg})
			else:
				if login_with_fb or login_with_google:
					return JsonResponse({'app_version': context['app_version'], 'expires': context['expires']})

				context['user'] = user
				context['csrfmiddlewaretoken'] = csrfmiddlewaretoken
				context['my_user'] = obj

				obj.menu = users_utils.build_user_menu(obj)

				return render(request, 'dashboard/index.html', context=context)
	else:
		return redirect('/')

	return render(request, 'home/index.html', context=context)

def __register_session__(request, user):
	if request.method == 'POST':
		from .models import UsersLoggedIn

		# Get the remote IP address from the client
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

		if x_forwarded_for:
			ipaddress = x_forwarded_for.split(',')[-1].strip()
		else:
			ipaddress = request.META.get('REMOTE_ADDR')

		# Get user agent from the client
		user_agent = request.META.get('HTTP_USER_AGENT')

		#import datetime
		full_time = datetime.now()
		csrfmiddlewaretoken = request.POST['csrfmiddlewaretoken']

		values = {
			'user_id': user.id,
			'ip': ipaddress,
			'user_agent': user_agent,
			'logged_when': full_time,
			'logged_at': full_time,
			'csrfmiddlewaretoken': csrfmiddlewaretoken
		}

		data = UsersLoggedIn.objects.create(**values)
		if data and data is not None:
			login_django(request, user)

			'''
			context = {
				'user': user, 
				'csrfmiddlewaretoken': csrfmiddlewaretoken
			}
			'''
			context = {}
			context['user'] = user
			context['csrfmiddlewaretoken'] = csrfmiddlewaretoken
			return render(request, 'dashboard/index.html', context=context)
		else:
			msg = _('I can not register your session') + '. '
			msg += _('Retry, and if the problem persist get in touch with the system administrator and report') + ': '
			msg += 'Error 004 at users.views@login'

			context={
				'level': 'error',
				'msg': msg,
				'logged-in': False
			}
	else:
		return redirect('/')

	return render(request, 'home/index.html')

def login_with_payment_verification(request):
	if request.method == 'POST':
		password = request.POST['password']
		email = request.POST['email']
		#user = authenticate(email=email, password=password)
		user = users_utils.authenticate_via_email(email, password)
		if not user or user is None:
			context = {
				'level': 'error',
				'msg': _('User account does not exist'),
				'logged-in': False
			}
			#return redirect('/')
		else:
			# Check if the user account is active (on table 'auth_user')
			if not user.is_active:
				context = {
					'level': 'error',
					'msg': _('User account has been disabled'),
					'logged-in': False
				}
				return render(request, 'home/index.html', context=context)

			from .models import Users
			obj = Users.objects.get(pk=user.id)

			# Check if the user account wasn't dropped (on table 'users_users')
			if obj.dropped:
				context = {
					'level': 'error',
					'msg': _('User account does not exist'),
					'logged-in': False
				}
				return render(request, 'home/index.html', context=context)

			# Check if the user account is active (on table 'users_users')
			if obj.disabled:
				context = {
					'level': 'error',
					'msg': _('User account has been disabled'),
					'logged-in': False
				}
				return render(request, 'home/index.html', context=context)

			# Check if the email was confirmed (on table 'users_users')
			if not obj.email_confirmed:
				context = {
					'level': 'error',
					'msg': _('The email address is not confirmed yet'),
					'logged-in': False
				}
				return render(request, 'home/index.html', context=context)

			# Check if the email was approved (on table 'users_users')
			if not obj.email_approved:
				context = {
					'level': 'error',
					'msg': _('The email address is not approved yet'),
					'logged-in': False
				}
				return render(request, 'home/index.html', context=context)

			context = {}

			# Verify the user's payments
			from appversions.models import Payments
			#from django.core.exceptions import DoesNotExist

			try:
				payments = Payments.objects.filter(user=user.id)
			except ObjectDoesNotExist:
				payments = []

			#if payments and payments is not None:
			total_payments = len(payments)
			context['payments'] = payments
			context['total_payments'] = total_payments

			hour_approved = obj.email_approved_at.hour
			minute_approved = obj.email_approved_at.minute

			# Free version
			if total_payments < 1:
				context['app_version'] = _('Free version')

				# Check if still active
				year_approved = obj.email_approved_when.year
				month_approved = obj.email_approved_when.month
				day_approved = obj.email_approved_when.day

				current = datetime.now()
				supported = datetime(year_approved, month_approved, day_approved, hour_approved, minute_approved)
				supported = supported + timedelta(days=15)

				if current > supported:
					context = {
						'level': 'error',
						'msg': _('Your free version has expired'),
						'logged-in': False
					}
					return render(request, 'home/index.html', context=context)

				context['expires'] = supported

			elif total_payments == 1:
				context['app_version'] = payments[0].app.name
				expires = payments[0].get_expires_when()
				expires = datetime(expires.year, expires.month, expires.day, payments[0].at.hour, payments[0].at.minute)
				context['expires'] = expires
			else:
				context['show_modal'] = True
				context['modal_name'] = 'dlgChooseAppVersion'
				return render(request, 'home/index.html', context=context)

			__register_session__(request, user)

	return render(request, 'home/index.html')

def register(request):
	if request.method == 'POST':
		#result = utils.validate_recaptcha(request.POST['g-recaptcha-response'])
		result = {'success': True}

		register_with_fb = request.POST.get('register_with_fb', False)
		register_with_google = request.POST.get('register_with_google', False)

		if result['success']:
			exist_user, dummy1 = users_utils.exist_user_account_by_email(request)
			# register_with_fb = request.POST.get('register_with_fb', False)
			# register_with_google = request.POST.get('register_with_google', False)

			if exist_user:
				msg = _('Email account already exists')
				context={
					'level': 'error',
					'msg': msg,
					'created': False
				}

				if register_with_fb or register_with_google:
					return JsonResponse({'status': 'error', 'msg': msg})

				return render(request, 'home/index.html', context=context)

			from django.contrib.auth.hashers import make_password

			if register_with_fb or register_with_google:
				first_name = request.POST.get('first_name', None)
				email = request.POST.get('email', None)
				password = request.POST.get('uid', first_name + '-' + email)[:8]

				full_time = datetime.now()
				values = {
					'username': request.POST.get('email', None),
	    		'first_name': first_name,
	    		'last_name': request.POST.get('last_name', None),
	    		'email': email,
	    		'created_at': full_time,
	    		'created_when': full_time,
	    		#'created_with_fb': True,
	    		'password': make_password(password),
	    		#'fb_id': request.POST.get('uid', first_name + '-' + email)
	    	}
				if register_with_fb:
					values['created_with_fb'] = True
					values['fb_id'] = request.POST.get('uid', first_name + '-' + email)
				else:
					values['created_with_google'] = True
					values['google_id'] = request.POST.get('uid', first_name + '-' + email)
			else:
				values = {
					'last_name': request.POST.get('last_name', None),
					'mothers_last_name': request.POST.get('mothers_last_name', None),
					'middle_name': request.POST.get('middle_name', None),
					'first_name': request.POST.get('first_name', None),
					'email': request.POST.get('email', None),
					'username': request.POST.get('email', None),
					'password': make_password(request.POST.get('password', None))
				}

			module = request.POST.get('module', None)

			generate_random_password = False
			pass_ = None

			if module and module is not None and 'MY_ADMIN_MODULE' in module.upper():
				values['created_by_user'] = Users.objects.get(pk=request.user)
				generate_random_password = request.POST.get('randompassword', False)
				if generate_random_password:
					full_time = datetime.now()
					year = full_time.year
					month = full_time.month
					day = full_time.day

					hour = full_time.hour
					minute = full_time.minute

					pass_ = str(year) + str(month) + str(day) + str(hour) + str(minute)
					values['password'] = make_password(pass_)
			else:
				values['created_by_user'] = Users.objects.get(pk=1)

			data = Users.objects.create(**values)
			if data and data is not None:	
				usergroup = request.POST.get('usergroup', None)
				permissions = request.POST.get('permissions', None)

				if usergroup and usergroup is not None and len(usergroup.strip()) > 0:
					#group = Group.objects.create(user=data, group=usergroup)
					#Group.objects.create(user=data, group=usergroup)
					data.groups.add(usergroup)

				if permissions and permissions is not None and len(permissions.strip()) > 0:
					permissions = permissions.split(',')
					#permissions = Permission.objects.filter(id__in=permissions)
					data.user_permissions.set(permissions)
					#permissions = permissions.split(',')
					#with transaction.atomic():

				data.plain_password = pass_
				if users_utils.send_notif_email_uac_created(request, data, generate_random_password) > 0:
					msg = _('User account has been successfully created') + '. ' + _('Required confirmation email')
					context={
						'level': 'success',
						'msg': msg,
						'created': True
					}

					if register_with_fb or register_with_google:
						return JsonResponse({'status': 'success', 'msg': msg})
				else:
					msg = _('User account has been successfully created') + '. ' + _('Missed confirmation email')
					context={
						'level': 'warning',
						'msg': msg,
						'created': True
					}

					if register_with_fb or register_with_google:
						return JsonResponse({'status': 'warning', 'msg': msg})

				return render(request, 'home/index.html', context=context)
			else:
				msg = _('An error has occurred') + '. '
				msg += _('Retry, and if the problem persist get in touch with the system administrator and report') + ':<br /><br />'
				#Please, find the way to retrieve the last DB error and write it on msg. I.e.: msg += db.get_error()
				msg += 'Error 001 at users.views@register'
				context={
					'level': 'error',
					'msg': msg,
					'created': False
				}

				if register_with_fb or register_with_google:
					return JsonResponse({'status': 'error', 'msg': msg})

			msg = _('Unknow error 002 at users.views@register')
			context={
				'level': 'error',
				'msg': msg,
				'created': False
			}

			if register_with_fb or register_with_google:
				return JsonResponse({'status': 'error', 'msg': msg})
		else:
			msg = utils.retrieve_recaptcha_error(result['error-codes'])

			context={
				'level': 'error',
				'msg': msg,
				'created': False
			}
		
			if register_with_fb or register_with_google:
				return JsonResponse({'status': 'error', 'msg': msg})

		return render(request, 'home/index.html', context=context)
	else:
		return redirect('/')

	return render(request, 'home/index.html')

def forgot_password(request):
	if request.method == 'POST':
		#exist_user, user, my_user = users_utils.exist_user_account_by_email(request)
		exist_user, my_user = users_utils.exist_user_account_by_email(request)
		if exist_user:
			#if users_utils.send_email_forgot_password(request, user, my_user):
			if users_utils.send_email_forgot_password(request, my_user):
				context = {
					'level': 'success',
					'msg': _('The email for your password recovery was successfully sent')
				}
			else:
				msg = _('I can not send the email for your password recovery') + '. ' 
				msg += _('Retry, and if the problem persist get in touch with the system administrator and report') + ': '
				context = {
					'level': 'error',
					'msg': msg
				}
			return render(request, 'home/index.html', context=context)
		else:
			context = {
				'level': 'error',
				'msg': _('User account does not exist')
			}
			return render(request, 'home/index.html', context=context)
		
	return redirect('/')

def confirm_user_account(request):
	try:
		uid = request.GET['u']
		k = request.GET['k']
		s = request.GET['s']
		p = request.GET['p']
		i = request.GET['i']
		code = request.GET['code']
		pid = request.GET['pid']
	except MultiValueDictKeyError:
		return redirect('/')

	passed = uid and k and s and p and i and code and pid

	if passed:
		uid = uid[:uid.find('d')]
		uid = uid[uid.find('-')+1:]

		from .models import Users

		try:
			user = Users.objects.get(pk=uid)
			if user.phishing or user.dropped:
				raise ObjectDoesNotExist()

			user.email_confirmed = True
			full_time = datetime.now()
			user.email_confirmed_at = full_time
			user.email_confirmed_when = full_time
			user.phishing = False
			user.phishing_at = None
			user.phishing_when = None

			# Now we must to add the user to the admin group...
			# But until the user account will be approved
			'''
			from django.contrib.auth.models import Group
			group = Group.objects.get(name='Administrador del sistema')
			group.user_set.add(user)
			'''

			user.save()

			users_utils.send_email_user_account_confirmed(request, user)
		except ObjectDoesNotExist:
			return redirect('/')
	else:
		return redirect('/')

	'''
	context = {
		'show_modal': True,
		'modal_name': 'dlgUserAccountConfirmed'
	}
	'''

	msg = _('The user account has been confirmed successfully')
	msg += '. ' + _('For security reasons you have to wait upon 24 hours to log in')

	context = {
		'level': 'success',
		'msg': msg
	}

	return render(request, 'home/index.html', context=context)

def notify_phishing(request):
	try:
		uid = request.GET['u']
		k = request.GET['k']
		s = request.GET['s']
		p = request.GET['p']
		i = request.GET['i']
		code = request.GET['code']
		pid = request.GET['pid']
	except MultiValueDictKeyError:
		return redirect('/')

	passed = uid and k and s and p and i and code and pid

	if passed:
		uid = uid[:uid.find('d')]
		uid = uid[uid.find('-')+1:]

		from .models import Users

		try:
			user = Users.objects.get(pk=uid)
			if user.phishing or user.dropped:
				raise ObjectDoesNotExist()
		except ObjectDoesNotExist:
			return redirect('/')
	else:
		return redirect('/')

	context = {
		'show_modal': True,
		'modal_name': 'dlgDeleteUserAccount',
		'email': pid,
		'reason': 'phishing'
	}

	return render(request, 'home/index.html', context=context)

def delete_user_account(request):
	context = {'show_modal': False}

	if request.method == 'POST':
		email = request.POST['email']
		reason = request.POST['reason']

		from .models import Users

		try:
			user_django = User.objects.get(email=email)
			my_user = Users.objects.get(pk=user_django.id)
			#if not my_user.phishing:
			if not my_user.dropped:
				my_user.dropped = True

				full_time = datetime.now()
				my_user.dropped_at = full_time
				my_user.dropped_when = full_time

				my_user.email_confirmed = False
				my_user.email_confirmed_at = None
				my_user.email_confirmed_when = None

				if 'phishing' in reason.lower():
					my_user.phishing = True
					my_user.phishing_at = full_time
					my_user.phishing_when = full_time
					my_user.dropped_reason = reason.upper()

				my_user.save()
			else:
				raise ObjectDoesNotExist()
		except ObjectDoesNotExist:
			context = {
				'level': 'error',
				'msg': _('User account does not exist')
			}

		context = {
			'level': 'success',
			'msg': _('User account has been deleted successfully')
		}
	else:
		return redirect('/')

	return render(request, 'home/index.html', context=context)

def approve_user_account(request):
	context = {'show_modal': False}

	if request.method == 'GET':
		email = request.GET['pid']

		from .models import Users

		try:
			user_django = User.objects.get(email=email)
			my_user = Users.objects.get(pk=user_django.id)

			if not my_user.dropped:
				super_user = Users.objects.get(pk=1)
				my_user.email_approved = True

				full_time = datetime.now()
				my_user.email_approved_at = full_time
				my_user.email_approved_when = full_time

				# Now we must to add the user to the admin group...
				# ONLY if the user register him/her self, I mean
				# created_by_user has to be 1 (superuser or admin)
				# In any other case, it means that another user
				# was the 'creator' for this user 
				# (see do_add(request) in users.views_my_admin)
				if my_user.created_by_user.id == 1:
					from django.contrib.auth.models import Group
					group = Group.objects.get(name__icontains='Administrador del sistema')
					group.user_set.add(my_user)

				# Now we must to add the initial tasks to the user...
				from tasks.models import Tasks, UsersTasks
				tasks = Tasks.objects.filter(initial=True)
				for task in tasks:
					ut = UsersTasks(user=my_user, task=task, created_by_user=super_user)
					ut.save()
					#my_user.tasks.add(task)

				# Add the notifications...
				from notifications.models import Notifications, UsersNotifications
				notifs = Notifications.objects.filter(initial=True)
				for notif in notifs:
					notif_ = notif.name.upper()
					un = UsersNotifications(user=my_user, notification=notif, created_by_user=super_user, obj_name=my_user.full_name)

					if 'CUENTA DE USUARIO CREADA' in notif_:
						un.created_at = my_user.created_at
						un.created_when = my_user.created_when
					elif 'CUENTA DE USUARIO CONFIRMADA' in notif_:
						un.created_at = my_user.email_confirmed_at
						un.created_when = my_user.email_confirmed_when
					elif 'CUENTA DE USUARIO APROBADA' in notif_:
						un.created_at = my_user.email_approved_at
						un.created_when = my_user.email_approved_when

					un.save()

				# Create the "General Public" customer...
				from customers.models import Customers
				customer=Customers()
				customer.rfc='XXXXXXXXXXX'+str(my_user.id)
				customer.created_by_user=my_user
				customer.first_name=_('Public')
				customer.last_name=_('General')
				customer.gender=''
				today=datetime.now()
				customer.dob=today-relativedelta(years=18)
				print('*********customer.save()**********')
				customer.save()

				my_user.save()
			else:
				raise ObjectDoesNotExist()
		except ObjectDoesNotExist:
			context = {
				'level': 'error',
				'msg': _('User account does not exist')
			}
		except MultiValueDictKeyError:
			return redirect('/')
		except IntegrityError as error:
			if 'tasks_userstasks.user_id' in error.args[0]:
				pass
			else:
				print(error)
				msg = _('The requested operation cannot be performed') + '. '
				msg += _('Retry, and if the problem persist get in touch with the system administrator and report') + ': '
				msg += 'error 1000 at users.views@approve_user_account'

				context = {
					'level': 'error',
					'msg': msg
				}
				return render(request, 'home/index.html', context=context)

		context = {
			'level': 'success',
			'msg': _('User account has been approved successfully')
		}

		#users_utils.send_email_user_account_approved(request, my_user)
	else:
		return redirect('/')

	return render(request, 'home/index.html', context=context)

def logout(request):
	if request.method == 'GET' and 'c' in request.GET:
		from django.contrib.auth import logout as logout_django

		csrfmiddlewaretoken = request.GET['c']

		from .models import UsersLoggedIn
		#user = UsersLoggedIn.objects.get(csrfmiddlewaretoken=csrfmiddlewaretoken)
		users = UsersLoggedIn.objects.filter(csrfmiddlewaretoken=csrfmiddlewaretoken)

		full_time = datetime.now()

		for user in users:
			if user.active:
				user.active = False
				user.disconnected_at = full_time
				user.disconnected_when = full_time
				user.save()

	logout_django(request)

	return redirect('/')

def reset_password(request):
	if request.method == 'GET':
		try:
			uid = request.GET['u']
			k = request.GET['k']
			s = request.GET['s']
			p = request.GET['p']
			i = request.GET['i']
			code = request.GET['code']
			pid = request.GET['pid']
		except MultiValueDictKeyError:
			return redirect('/')

		passed = uid and k and s and p and i and code and pid

		if passed:
			uid = uid[:uid.find('d')]
			uid = uid[uid.find('-')+1:]

			from .models import Users

			try:
				user = Users.objects.get(pk=uid)
				if user.phishing or user.dropped:
					raise ObjectDoesNotExist()
			except ObjectDoesNotExist:
				return redirect('/')
		else:
			return redirect('/')

		context = {
			'show_modal': True,
			'modal_name': 'dlgResetPassword',
			'email': pid
		}

		return render(request, 'home/index.html', context=context)

	return redirect('/')

def do_reset_password(request):
	if request.method == 'POST':
		email = request.POST['email']
		password = request.POST['password']

		from .models import Users

		try:
			#user = User.objects.get(email=email)
			#my_user = Users.objects.get(pk=user.id)
			#my_user = Users.objects.get(pk=request.user)
			my_user = Users.objects.get(email__iexact=email)

			if my_user.phishing or my_user.dropped:
				raise ObjectDoesNotExist()

			from django.contrib.auth.hashers import make_password

			my_user.password = make_password(password)
			my_user.save()

			msg = _('Your password has been successfully changed')

			#if users_utils.send_email_password_changed(request, user, my_user):
			if users_utils.send_email_password_changed(request, my_user):
				level = 'success'
				msg += '. ' + _('We have sent you a confirmation email')
			else:
				level = 'warning'
				msg += '. ' + _('The confirmation email could not be sent')

			context = {
				'level': level,
				'msg': msg
			}

			return render(request, 'home/index.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def disable_first_time_tutorial_for_user(request):
	if request.method == 'GET':
		user = None

		try:
			user = request.GET['user']
		except MultiValueDictKeyError:
			return redirect('/')

		if 'user' not in request.GET:
			return redirect('/')

		if user is not None:
			from users.models import Users
			try:
				user = Users.objects.get(email=user)
				user.show_dlg_first_tutorial_not_completed = False
				user.save()
				return JsonResponse({'status': 'success', 'msg': _('The first time tutorial was disabled')})
			except ObjectDoesNotExist:
				return redirect('/')

	return redirect('/')

def check_first_time_login_for_user(request):
	if request.method == 'GET':
		user = None

		try:
			user = request.GET['user']
		except MultiValueDictKeyError:
			return redirect('/')

		if 'user' not in request.GET:
			return redirect('/')

		if user is not None:
			from users.models import Users
			try:
				user = Users.objects.get(email=user)
				user.first_time_login = True
				user.save()
				return JsonResponse({'status': 'success', 'msg': _('The first time login for the user was marked')})
			except ObjectDoesNotExist:
				return redirect('/')

	return redirect('/')

def check_first_tutorial_completed(request):
	if request.method == 'GET':
		user = None

		try:
			user = request.GET['user']
		except MultiValueDictKeyError:
			return redirect('/')

		if 'user' not in request.GET:
			return redirect('/')

		if user is not None:
			from users.models import Users
			try:
				user = Users.objects.get(email=user)
				user.first_tutorial_completed = True
				user.save()
				return JsonResponse({'status': 'success', 'msg': _('The first tutorial was marked as completed')})
			except ObjectDoesNotExist:
				return redirect('/')

	return redirect('/')

def update_step_first_tutorial(request):
	if request.method == 'GET':
		user = None

		try:
			user = request.GET['user']
			step = request.GET['step']
		except MultiValueDictKeyError:
			return redirect('/')

		if 'user' not in request.GET:
			return redirect('/')

		if user is not None:
			from users.models import Users
			try:
				user = Users.objects.get(email=user)
				user.current_step_first_tutorial = step
				user.save()
				return JsonResponse({'status': 'success', 'msg': _('The current step for the first tutorial was saved')})
			except ObjectDoesNotExist:
				return redirect('/')

	return redirect('/')

def search_user_by_email(request):
	if request.is_ajax():
		query = request.GET.get('email', '')
		#query = query.replace('+', ' ')

		result = {}

		try:
			user = User.objects.get(email__iexact=query)
			result['exist'] = True
			result['user'] = user.id
			#result['dropped'] = user.dropped
		except ObjectDoesNotExist:
			result['exist'] = False

		data = json.dumps(result)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)