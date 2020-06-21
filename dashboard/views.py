from django.shortcuts import render

from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist

from django.utils.translation import gettext as _

from datetime import datetime, timedelta

from users import utils as users_utils

# Create your views here.

def index(request):
	context = {}

	if request.method == 'GET':
		login_with_fb = request.GET.get('login_with_fb', False)
		login_with_google = request.GET.get('login_with_google', False)

		if login_with_fb or login_with_google:
			email = request.GET.get('email', None)
			csrfmiddlewaretoken = request.GET.get('csrfmiddlewaretoken', None)

			obj = users_utils.authenticate_using_email(email)
			if login_with_fb:
				password = obj.fb_id[:8]
			else:
				password = obj.google_id[:8]
			user = User.objects.get(pk=obj.id)

			if not user or user is None:
				msg = _('User account does not exist')
				context = {
					'level': 'error',
					'msg': msg,
					'logged-in': False
				}

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

					return render(request, 'home/index.html', context=context)

				#from users.models import Users
				#obj = Users.objects.get(pk=user.id)

				# Check if the user account wasn't dropped (on table 'users_users')
				if obj.dropped:
					msg = _('User account does not exist')
					context = {
						'level': 'error',
						'msg': msg,
						'logged-in': False
					}

					return render(request, 'home/index.html', context=context)

				# Check if the user account is active (on table 'users_users')
				if obj.disabled:
					msg = _('User account has been disabled')
					context = {
						'level': 'error',
						'msg': msg,
						'logged-in': False
					}

					return render(request, 'home/index.html', context=context)

				# Check if the email was confirmed (on table 'users_users')
				if not obj.email_confirmed:
					msg = _('The email address is not confirmed yet')
					context = {
						'level': 'error',
						'msg': msg,
						'logged-in': False
					}

					return render(request, 'home/index.html', context=context)

				# Check if the email was approved (on table 'users_users')
				if not obj.email_approved:
					msg = _('The email address is not approved yet')
					context = {
						'level': 'error',
						'msg': msg,
						'logged-in': False
					}

					return render(request, 'home/index.html', context=context)

				today = datetime.now()

				context['user'] = user
				context['csrfmiddlewaretoken'] = csrfmiddlewaretoken
				context['my_user'] = obj
				context['app_version'] = request.GET.get('app_version', _('Free version'))

				# Check if still active the 'Free version'
				year_approved = obj.email_approved_when.year
				month_approved = obj.email_approved_when.month
				day_approved = obj.email_approved_when.day

				hour_approved = obj.email_approved_at.hour
				minute_approved = obj.email_approved_at.minute

				supported = datetime(year_approved, month_approved, day_approved, hour_approved, minute_approved)
				supported = supported + timedelta(days=15)

				current = datetime.now()

				if current > supported:
					msg = _('Your free version has expired')
					context = {
						'level': 'error',
						'msg': msg,
						'logged-in': False
					}

					return render(request, 'home/index.html', context=context)

				context['expires'] = request.GET.get('expires', supported)

				obj.menu = users_utils.build_user_menu(obj)

	return render(request, 'dashboard/index.html', context=context)

def main_panel(request):
	return render(request, 'dashboard/assets/content/content.html')	

def processing(request):
	return render(request, 'dashboard/assets/page-loader.html')

def choose_app_version(request):
	context = {}

	if request.method == 'GET':
		if request.GET.get('login_with_fb', False):
			email = request.GET.get('email', None)
			current = datetime.now()

			# Verify the user's payments
			from appversions.models import Payments
			from users.models import Users
			#from django.core.exceptions import DoesNotExist

			try:
				user = Users.objects.get(email__iexact=email)
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

						return render(request, 'home/index.html', context=context)
					else:
						expires = supported

				context['expires'] = expires

	return render(request, 'dashboard/app-version/choose-app-version.html', context=context)