from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist

from django.utils.translation import gettext as _

from .models import Users

from utils import utils

import random

dummy_text = _('Required password strength')
dummy_text = _('Passwords does not match')

def authenticate_via_email(email, password):
	"""
	Authenticate user using email.
	Returns user object if authenticated else None
	"""
	if email:
		try:
			user = User.objects.get(email__iexact=email)
			if user.check_password(password):
				return user
		except ObjectDoesNotExist:
			pass

	return None

'''
def authenticate_via_fb(email):
	if email:
		try:
			user = Users.objects.get(email__iexact=email)
			return user
		except ObjectDoesNotExist:
			pass

	return None
'''

def authenticate_using_email(email):
	if email:
		try:
			user = Users.objects.get(email__iexact=email)
			return user
		except ObjectDoesNotExist:
			pass

	return None

def __generate_anchor__(uid, last_name, email):
	secure_random = random.SystemRandom()
	anchor = '?k='
	anchor += secure_random.choice(utils.KEYS)
	anchor += '&s=' + secure_random.choice(utils.SERVERS)
	anchor += '&p=' + secure_random.choice(utils.PROVIDERS)
	anchor += '_' + str(uid)
	u_param = secure_random.choice(utils.CRIP_UID)
	u_param = u_param.replace('@UID@', str(uid))
	anchor += '&u=' + u_param
	anchor += '&i=' + secure_random.choice(utils.IPS)
	anchor += '&code=' + str(last_name)
	anchor += '&pid=' + str(email)

	return anchor

def __replace_in_message(request, data, message, message_format):
	url=utils.get_main_url(request)
	message = message.replace('@URL_APP@', url)
	message = message.replace('@COMPANY_NAME@', _('Company name'))
	message = message.replace('@APP_NAME@', _('Organization name'))

	from django.conf import settings
	message = message.replace('@RESPONSE_TO_EMAIL@', settings.EMAIL_CONTACT)

	if message_format != 'text/html':
		message = message.replace('<br />', '\n')

	register_with_fb = request.POST.get('register_with_fb', False)
	register_with_google = request.POST.get('register_with_google', False)

	if register_with_fb or register_with_google:
		full_name = request.POST['first_name']
		mn = mln = None
	else:
		full_name = request.POST['first_name']

		mn = request.POST['middle_name']
		mln = request.POST['mothers_last_name']
	
	if mn and mn is not None and len(mn.strip()) > 0:
		full_name += ' ' + mn

	if mln and mln is not None and len(mln.strip()) > 0:
		full_name += ' ' + mln

	if register_with_fb or register_with_google:
		full_name += ' ' + request.POST['last_name']
	else:
		full_name += ' ' + request.POST['last_name']

	message = message.replace('@FULL_NAME@', full_name)

	# ***************************************
	#              Anchor confirm
	# ***************************************
	# anchor_confirm = _('Main url') + 'users/confirm-user-account'
	anchor_confirm = url + '/users/confirm-user-account'
	anchor_confirm += __generate_anchor__(data.id, data.last_name, data.email)

	message = message.replace('@ANCHOR_CONFIRM@', anchor_confirm)

	# ***************************************
	#              Anchor phishing
	# ***************************************
	# anchor_phishing = _('Main url') + 'users/notify-phishing'
	anchor_phishing = url + '/users/notify-phishing'
	anchor_phishing += __generate_anchor__(data.id, data.last_name, data.email)

	message = message.replace('@ANCHOR_PHISHING@', anchor_phishing)

	return message

#def __replace_in_message_forgot_password__(request, user, my_user, message, message_format):
def __replace_in_message_forgot_password__(request, my_user, message, message_format):
	url=utils.get_main_url(request)
	message = message.replace('@URL_APP@', url)
	message = message.replace('@COMPANY_NAME@', _('Company name'))
	message = message.replace('@APP_NAME@', _('Organization name'))

	from django.conf import settings
	message = message.replace('@RESPONSE_TO_EMAIL@', settings.EMAIL_CONTACT)

	if message_format != 'text/html':
		message = message.replace('<br />', '\n')

	full_name = my_user.first_name

	mn = my_user.middle_name
	mln = my_user.mothers_last_name
	
	if mn and mn is not None and len(mn.strip()) > 0:
		full_name += ' ' + mn

	if mln and mln is not None and len(mln.strip()) > 0:
		full_name += ' ' + mln

	full_name += ' ' + my_user.last_name

	message = message.replace('@FULL_NAME@', full_name)

	# ***************************************
	#              Anchor confirm
	# ***************************************
	# anchor_confirm = _('Main url') + 'users/reset-password'
	anchor_confirm = url + '/users/reset-password'
	anchor_confirm += __generate_anchor__(my_user.id, my_user.last_name, my_user.email)

	message = message.replace('@ANCHOR_CONFIRM@', anchor_confirm)

	# ***************************************
	#              Anchor phishing
	# ***************************************
	# anchor_phishing = _('Main url') + 'users/notify-phishing'
	anchor_phishing = url + '/users/notify-phishing'
	anchor_phishing += __generate_anchor__(my_user.id, my_user.last_name, my_user.email)

	message = message.replace('@ANCHOR_PHISHING@', anchor_phishing)

	return message

#def __replace_in_message_password_changed__(request, user, my_user, message, message_format):
def __replace_in_message_password_changed__(request, my_user, message, message_format):
	url=utils.get_main_url(request)
	message = message.replace('@URL_APP@', url)
	message = message.replace('@COMPANY_NAME@', _('Company name'))
	message = message.replace('@APP_NAME@', _('Organization name'))
	message = message.replace('@NEW_PASSWORD@', my_user.password)

	from django.conf import settings
	message = message.replace('@RESPONSE_TO_EMAIL@', settings.EMAIL_CONTACT)

	if message_format != 'text/html':
		message = message.replace('<br />', '\n')

	full_name = my_user.first_name

	mn = my_user.middle_name
	mln = my_user.mothers_last_name
	
	if mn and mn is not None and len(mn.strip()) > 0:
		full_name += ' ' + mn

	if mln and mln is not None and len(mln.strip()) > 0:
		full_name += ' ' + mln

	full_name += ' ' + my_user.last_name

	message = message.replace('@FULL_NAME@', full_name)

	# ***************************************
	#              Anchor phishing
	# ***************************************
	# anchor_phishing = _('Main url') + 'users/notify-phishing'
	anchor_phishing = url + '/users/notify-phishing'
	anchor_phishing += __generate_anchor__(my_user.id, my_user.last_name, my_user.email)

	message = message.replace('@ANCHOR_PHISHING@', anchor_phishing)

	return message

def __replace_in_message_user_account_confirmed__(request, user, message, message_format):
	url=utils.get_main_url(request)
	message = message.replace('@URL_APP@', url)
	message = message.replace('@COMPANY_NAME@', _('Company name'))
	message = message.replace('@APP_NAME@', _('Organization name'))

	from django.conf import settings
	message = message.replace('@RESPONSE_TO_EMAIL@', settings.EMAIL_CONTACT)

	if message_format != 'text/html':
		message = message.replace('<br />', '\n')

	full_name = user.first_name

	mn = user.middle_name
	mln = user.mothers_last_name
	
	if mn and mn is not None and len(mn.strip()) > 0:
		full_name += ' ' + mn

	if mln and mln is not None and len(mln.strip()) > 0:
		full_name += ' ' + mln

	'''
	mn = my_user.middle_name
	mln = my_user.mothers_last_name
	
	if mn and mn is not None and len(mn.strip()) > 0:
		full_name += ' ' + mn

	if mln and mln is not None and len(mln.strip()) > 0:
		full_name += ' ' + mln
	'''

	full_name += ' ' + user.last_name

	message = message.replace('@FULL_NAME@', full_name)

	# ***************************************
	#              Anchor confirm
	# ***************************************
	# anchor_confirm = _('Main url') + 'users/approve-user-account'
	anchor_confirm = url + '/users/approve-user-account'
	anchor_confirm += __generate_anchor__(user.id, user.last_name, user.email)

	message = message.replace('@ANCHOR_CONFIRM@', anchor_confirm)

	return message

def __replace_in_message_user_account_approved__(request, user, message, message_format):
	url=utils.get_main_url(request)
	message = message.replace('@URL_APP@', url)
	message = message.replace('@COMPANY_NAME@', _('Company name'))
	message = message.replace('@APP_NAME@', _('Organization name'))

	from django.conf import settings
	message = message.replace('@RESPONSE_TO_EMAIL@', settings.EMAIL_CONTACT)

	if message_format != 'text/html':
		message = message.replace('<br />', '\n')

	full_name = user.first_name

	mn = user.middle_name
	mln = user.mothers_last_name
	
	if mn and mn is not None and len(mn.strip()) > 0:
		full_name += ' ' + mn

	if mln and mln is not None and len(mln.strip()) > 0:
		full_name += ' ' + mln

	full_name += ' ' + user.last_name

	message = message.replace('@FULL_NAME@', full_name)

	return message

def __retrieve_email_msg_and_replace_basic_data(request, data, random_password_generated=False):
	if not random_password_generated:
		message_text = _('Email user account created. Text format')
		message_html = _('Email user account created. HTML format')
	else:
		message_text = _('Email user account created with password. Text format')
		message_html = _('Email user account created with password. HTML format')

	message_html = __replace_in_message(request, data, message_html, 'text/html')
	message_text = __replace_in_message(request, data, message_text, 'text/plain')

	if random_password_generated:
		pass_ = str(data.plain_password)
		message_html = message_html.replace('@PASSWORD@', pass_)
		message_text = message_text.replace('@PASSWORD@', pass_)

	message_text += '\n------------------------------------------------------------------------------------------------------------------------------------------------\n'
	message_text += _('Notice email format text/plain')

	return {'message_html': message_html, 'message_text': message_text}

def __retrieve_email_msg_and_replace_basic_data_using_fb__(request, data):
	message_text = _('Email user account created with fb. Text format')
	message_html = _('Email user account created with fb. HTML format')

	from django.conf import settings

	message_html = __replace_in_message(request, data, message_html, 'text/html')

	first_name = request.POST.get('first_name', None)
	email = request.POST.get('email', None)
	password = request.POST.get('uid', first_name + '-' + email)[:8]

	message_html = message_html.replace('@PASSWORD@', password)

	message_text = __replace_in_message(request, data, message_text, 'text/plain')
	message_text = message_text.replace('@PASSWORD@', password)

	message_text += '\n------------------------------------------------------------------------------------------------------------------------------------------------\n'
	message_text += _('Notice email format text/plain')

	return {'message_html': message_html, 'message_text': message_text}

def send_notif_email_uac_created(request, data, random_password_generated=False):
	from django.core.mail import send_mail
	from django.conf import settings

	subject = _('App name')

	register_using_fb = request.POST.get('register_with_fb', False)
	if not register_using_fb:
		messages = __retrieve_email_msg_and_replace_basic_data(request, data, random_password_generated)
		message_html = messages.pop('message_html', '')
		message_text = messages.pop('message_text', '') 
	else:
		# messages = __retrieve_email_msg_and_replace_basic_data_using_fb__(request, data, random_password_generated)
		messages = __retrieve_email_msg_and_replace_basic_data_using_fb__(request, data)
		message_html = messages.pop('message_html', '')
		message_text = messages.pop('message_text', '') 

	return send_mail(
		subject,
		message_text,
		settings.EMAIL_CONTACT,
		[data.email],
		html_message=message_html
	)

#def send_email_forgot_password(request, user, my_user):
def send_email_forgot_password(request, my_user):
	from django.core.mail import send_mail
	from django.conf import settings

	subject = _('App name')

	message_text = _('Email forgot password. Text format')
	message_html = _('Email forgot password. HTML format')

	#message_html = __replace_in_message_forgot_password__(request, user, my_user, message_html, 'text/html')
	#message_text = __replace_in_message_forgot_password__(request, user, my_user, message_text, 'text/plain')
	message_html = __replace_in_message_forgot_password__(request, my_user, message_html, 'text/html')
	message_text = __replace_in_message_forgot_password__(request, my_user, message_text, 'text/plain')

	message_text += '\n------------------------------------------------------------------------------------------------------------------------------------------------\n'
	message_text += _('Notice email format text/plain')

	return send_mail(
		subject,
		message_text,
		settings.EMAIL_CONTACT,
		[my_user.email],
		html_message=message_html
	)

#def send_email_password_changed(request, user, my_user):
def send_email_password_changed(request, my_user):
	from django.core.mail import send_mail
	from django.conf import settings

	subject = _('App name')

	message_text = _('Email password changed. Text format')
	message_html = _('Email password changed. HTML format')

	#message_html = __replace_in_message_password_changed__(request, user, my_user, message_html, 'text/html')
	#message_text = __replace_in_message_password_changed__(request, user, my_user, message_text, 'text/plain')
	message_html = __replace_in_message_password_changed__(request, my_user, message_html, 'text/html')
	message_text = __replace_in_message_password_changed__(request, my_user, message_text, 'text/plain')

	message_text += '\n------------------------------------------------------------------------------------------------------------------------------------------------\n'
	message_text += _('Notice email format text/plain')

	return send_mail(
		subject,
		message_text,
		settings.EMAIL_CONTACT,
		[my_user.email],
		html_message=message_html
	)

def exist_user_account_by_email(request):
	if request.method == 'POST':
		email = request.POST.get('email', None)
	else:
		email = request.GET.get('email', None)

	if email and email is not None:
		try:
			'''
			user = User.objects.get(email__iexact=email)
			my_user = Users.objects.get(pk=user.id)
			return True, user, my_user
			'''
			my_user = Users.objects.get(email__iexact=email)
			return True, my_user
			#return True
			#return True, my_user
		except ObjectDoesNotExist:
			pass

	#return False, None, None
	return False, None
'''
def retrieve_user_permissions(user, by_user_group=True):
	if by_user_group:
		from django.contrib.auth
'''

def build_user_menu(user):
	# For more details about
	# the get_all_permissions() method see 
	# https://docs.djangoproject.com/es/2.1/ref/contrib/auth/#methods
	user.permissions = sorted(list(user.get_all_permissions()))

	apps = []
	menu = []

	tope = len(user.permissions)

	from users.models import AppMenu

	z = 1

	for x in range(tope):
		app = user.permissions[x]
		app = app[:app.index('.')]
		icon = ''

		if 'icon' in app:
			icon = app[app.index('icon=') + len('icon='):app.index(']')]
			app = app[:app.index('[')]

		if app not in apps:
			apps.append(app)
			app_menu = AppMenu(app=app, icon=icon)

			for y in range(tope):
				app_ = user.permissions[y]
				app_ = app_[:app_.index('.')]
				if 'icon' in app_:
					app_ = app_[:app_.index('[')]

				if app_ == app:
					module = user.permissions[y]
					module = module[module.index('.')+1:]
					icon = ''
					action = '#'

					if 'icon' in module:
						action = user.permissions[y]
						icon = module[module.index('icon=') + len('icon='):module.index(']')]
						module = module[:module.index('[icon')]

					if 'action' in module:
						action = module[module.index('action=') + len('action='):module.index(']')]
						module = module[:module.index('[action')]

					if module not in app_menu.children:
						module_dict = {'icon': icon, 'label': module, 'action': action, 'id': z}
						#app_menu.children.append(module)
						app_menu.children.append(module_dict)
						z+=1

			menu.append(app_menu)

	return menu

def send_email_user_account_confirmed(request, my_user):
	from django.core.mail import send_mail
	from django.conf import settings

	subject = _('App name')

	message_text = _('Confirmed the user account. Text format')
	message_html = _('Confirmed the user account. HTML format')

	message_html = __replace_in_message_user_account_confirmed__(request, my_user, message_html, 'text/html')
	message_text = __replace_in_message_user_account_confirmed__(request, my_user, message_text, 'text/plain')

	message_text += '\n------------------------------------------------------------------------------------------------------------------------------------------------\n'
	message_text += _('Notice email format text/plain')

	return send_mail(
		subject,
		message_text,
		settings.EMAIL_CONTACT,
		[settings.EMAIL_SUPER_ADMIN],
		html_message=message_html
	)

def send_email_user_account_approved(request, my_user):
	from django.core.mail import send_mail
	from django.conf import settings

	subject = _('App name')

	message_text = _('User account approved. Text format')
	message_html = _('User account approved. HTML format')

	message_html = __replace_in_message_user_account_approved__(request, my_user, message_html, 'text/html')
	message_text = __replace_in_message_user_account_approved__(request, my_user, message_text, 'text/plain')

	message_text += '\n------------------------------------------------------------------------------------------------------------------------------------------------\n'
	message_text += _('Notice email format text/plain')

	return send_mail(
		subject,
		message_text,
		settings.EMAIL_CONTACT,
		[my_user.email],
		html_message=message_html
	)