from django.shortcuts import render, redirect

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
#from django.utils.datastructures import MultiValueDictKeyError

from .models import Sales
from users.models import Users

def by_identifier(request):
	if request.method == 'GET':
		identifier = request.GET.get('identifier', None)

		try:
			sale = Sales.objects.get(identifier__iexact=identifier)
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': sale.dropped, 'sale': sale.id, 'msg': _('The indicated sale identifier already exists')})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})

'''
Same sale = 
created_by_user, identifier, sold_at, sold_when 

See models for details
'''
def by_unique_sale_user(request):
	if request.method == 'GET':
		identifier = request.GET.get('identifier', None)
		user = Users.objects.get(pk=request.user)
		sold_at = request.GET.get('sold_at', None)
		sold_when = request.GET.get('sold_when', None)
		sold_when = sold_when[6:] + '-' + sold_when[3:5] + '-' + sold_when[0:2]

		if sold_at and sold_at is not None:
			sold_at = '\'' + sold_at + '\''

		if sold_when and sold_when is not None:
			sold_when = '\'' + sold_when + '\''

		try:
			sale = Sales.objects.get(identifier__iexact=identifier, created_by_user=user, sold_at__iexact=sold_at, sold_when__iexact=sold_when)
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': sale.dropped, 'sale': sale.id, 'msg': _('One sale was done at the specified date time and identifier already exists')})
		except ObjectDoesNotExist as e:
			try:
				# Verify also its owner identifier
				sale = Sales.objects.get(identifier__iexact=identifier, created_by_user=user)

				return JsonResponse({'exist': True, 'status': 'info', 'dropped': sale.dropped, 'sale': sale.id, 'msg': _('One sale with the specified identifier already exists')})
			except ObjectDoesNotExist as e2:
				pass

		return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'exist': False, 'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})