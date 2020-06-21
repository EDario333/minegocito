# from django.shortcuts import render, redirect

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from .models import Products
from purchases.models import PurchasesProductsDetails
from users.models import Users

def by_name(request):
	if request.method == 'GET':
		productname = request.GET.get('product', None)

		try:
			user = Users.objects.get(pk=request.user)
			product = Products.objects.get(name__iexact=productname, created_by_user=user)
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': product.dropped, 'product': product.id})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})

def by_sku(request):
	if request.method == 'GET':
		sku = request.GET.get('sku', None)
		if sku is None or len(sku.strip()) < 1:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

		try:
			product = PurchasesProductsDetails.objects.get(sku__iexact=sku)

			#from django.core.serializers import serialize
			#product = serialize('json', [product])

			#return JsonResponse({'exist': True, 'status': 'info', 'product': product})
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': product.dropped, 'product': product.id})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})