from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _

from django.core.mail import send_mail
from django.conf import settings

def index(request):
	context={
		'subject': ''
	}

	if request.method=='GET':
		context['subject']=request.GET.get('subject', '')

	return render(request, 'contact/index.html', context=context)

def __replace_in_message__(fn, ln, email, user_message, message, message_format):
	message = message.replace('@URL_APP@', 'http://tinyurl.com/minegocito-mx/')
	message = message.replace('@COMPANY_NAME@', _('Company name'))
	message = message.replace('@APP_NAME@', _('Organization name'))
	message = message.replace('@MESSAGE@', user_message)
	message = message.replace('@RESPONSE_TO_EMAIL@', email)

	if message_format != 'text/html':
		message = message.replace('<br />', '\n')

	message = message.replace('@FULL_NAME@', fn + ' ' + ln)

	return message

def send_message(request):
	if request.method=='POST':
		context={}
		fn=request.POST.get('c_fname', None)
		ln=request.POST.get('c_lname', None)
		email=request.POST.get('c_email', None)
		subject=request.POST.get('c_subject', None)
		msg=request.POST.get('c_message', None)

		message_text = _('Send message from contact page. Text format')
		message_html = _('Send message from contact page. HTML format')

		message_html = __replace_in_message__(fn, ln, email, msg, message_html, 'text/html')
		message_text = __replace_in_message__(fn, ln, email, msg, message_text, 'text/plain')

		message_text += '\n------------------------------------------------------------------------------------------------------------------------------------------------\n'
		message_text += _('Notice email format text/plain')

		result = send_mail(
			subject,
			message_text,
			email,
			[settings.EMAIL_CONTACT],
			html_message=message_html
		)

		if result and result>0:
			context['level']='success'
			context['msg']=_('Your message was sent successfully')
		else:
			context['level']='error'
			context['msg']=_('Your message cannot be delivered')+'. '+_('Retry, and if the problem persist get in touch with the system administrator and report')+': error 001 at send_message@contact.views'

		return render(request, 'contact/index.html', context=context)

	msg = _('You do not have permission to perform this request')
	html='<script type="text/javascript">'
	html+='show_msg_with_toastr("error", "' + msg + '");'
	html+='</script>'

	# return JsonResponse({'status': 'error', 'msg': msg})
	return HttpResponse(html, 'text/html; charset=utf-8')