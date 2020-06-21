from django.shortcuts import render, redirect

#from django.db.models import Q

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from .models import Customers
from users.models import Users

def search_by_rfc(rfc, request):
	try:
		user = Users.objects.get(pk=request.user)
		customer = Customers.objects.get(rfc__iexact=rfc,created_by_user=user,dropped=False)

		#from django.core.serializers import serialize
		#product = serialize('json', [product])

		#return JsonResponse({'exist': True, 'status': 'info', 'product': product})
		return JsonResponse({'exist': True, 'status': 'info', 'dropped': customer.dropped, 'customer': customer.id})
	except ObjectDoesNotExist:
		return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'exist': None, 'status': 'info', 'msg': _('We can not determine the results')})

def search_by_email(email, request):
	try:
		user = Users.objects.get(pk=request.user)
		customer = Customers.objects.get(email__iexact=email,created_by_user=user,dropped=False)

		#from django.core.serializers import serialize
		#product = serialize('json', [product])

		#return JsonResponse({'exist': True, 'status': 'info', 'product': product})
		return JsonResponse({'exist': True, 'status': 'info', 'dropped': customer.dropped, 'customer': customer.id})
	except ObjectDoesNotExist:
		return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'exist': None, 'status': 'info', 'msg': _('We can not determine the results')})

def by_rfc(request):
	if request.method == 'GET':
		rfc = request.GET.get('rfc', None)
		return search_by_rfc(rfc, request)

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})

def by_email(request):
	if request.method == 'GET':
		email = request.GET.get('email', None)
		return search_by_email(email, request)

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})