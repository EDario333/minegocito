from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from django.core.mail import send_mail
from django.conf import settings

from .models import Subscriptions
from users.models import Users

from utils import utils

def __replace_in_message__(request, email, message, message_format):
	url=utils.get_main_url(request)

	message = message.replace('@URL_APP@', url)
	message = message.replace('@COMPANY_NAME@', _('Company name'))
	message = message.replace('@APP_NAME@', _('Organization name'))
	message = message.replace('@RESPONSE_TO_EMAIL@', 'minegocito.mx@gmail.com')	
	message = message.replace('@ANCHOR_PHISHING@', url+'/newsletter/notify-phishing/?email='+email)

	if message_format != 'text/html':
		message = message.replace('<br />', '\n')

	return message

def subscribe(request):
	if request.method=='POST':
		result = utils.validate_recaptcha(request.POST['g-recaptcha-response'])

		if not result['success']:
			msg = utils.retrieve_recaptcha_error(result['error-codes'])
			return JsonResponse({'status': 'error', 'msg': msg})

		email=request.POST.get('email', None)
		suscription=None

		try:
			suscription=Subscriptions.objects.get(email__iexact=email)
			if not suscription.dropped:
				return JsonResponse({'status': 'error', 'msg': _('The specified email addres already exists in our newsletter')})
			else:
				raise ObjectDoesNotExist
		except ObjectDoesNotExist:
			context={}

			message_text = _('Newsletter subscription message. Text format')
			message_html = _('Newsletter subscription message. HTML format')

			message_html = __replace_in_message__(request, email, message_html, 'text/html')
			message_text = __replace_in_message__(request, email, message_text, 'text/plain')

			message_text += '\n------------------------------------------------------------------------------------------------------------------------------------------------\n'
			message_text += _('Notice email format text/plain')

			result = send_mail(
				_('Newsletter subscription subject email'),
				message_text,
				email,
				[email],
				html_message=message_html
			)

			if result and result>0:
				if suscription is not None and suscription.dropped:
					suscription.undrop()
				else:
					my_u=Users.objects.get(pk=1)
					subscription=Subscriptions(email=email,created_by_user=my_u)
					subscription.save()
				return JsonResponse({'status': 'success', 'msg': _('Thank you for your subscription to our newsletter')})
			else:
				msg=_('The requested operation can not be completed')+'. '+_('Retry, and if the problem persist get in touch with the system administrator and report')+': error 001 at subscribe@newsletter.views'
				return JsonResponse({'status': 'error', 'msg': msg})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request')})

def notify_phishing(request):
	context={
		'msg': _('You do not have permission to perform this request'),
		'level': 'error'
	}

	if request.method=='GET':
		email=request.GET.get('email', None)

		try:
			subscription=Subscriptions.objects.get(email__iexact=email,dropped=False)

			message_text = _('Newsletter phishing message. Text format')
			message_html = _('Newsletter phishing message. HTML format')

			message_html = __replace_in_message__(request, email, message_html, 'text/html')
			message_text = __replace_in_message__(request, email, message_text, 'text/plain')

			message_text += '\n------------------------------------------------------------------------------------------------------------------------------------------------\n'
			message_text += _('Notice email format text/plain')

			result = send_mail(
				_('Newsletter phishing subject email'),
				message_text,
				email,
				[email],
				html_message=message_html
			)

			if result and result>0:
				subscription.drop(reason=_('Phishing notification'))
				context['level']='success'
				context['msg']=_('Your subscription to our newsletter has been erased')
			else:
				msg=_('The requested operation can not be completed')+'. '+_('Retry, and if the problem persist get in touch with the system administrator and report')+': error 002 at notify_phishing@newsletter.views'
				context['level']='error'
				context['msg']=msg
		except ObjectDoesNotExist:
			context['msg']=_('The specified email does not exist in our subscription newsletter')
			context['level']='error'

	return render(request, 'home/index.html', context=context)

def verify_unique_email(request):
	if request.method=='GET':
		email=request.GET.get('email', None)
		try:
			Subscriptions.objects.get(email__iexact=email,dropped=False)
			return JsonResponse({'status': 'error', 'msg': _('The specified email addres already exists in our newsletter'), 'continue': False})
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'success', 'msg': _('The specified email addres does not exists in our newsletter'), 'continue': True})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'), 'continue': False})