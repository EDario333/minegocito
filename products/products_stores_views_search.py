from django.shortcuts import render, redirect

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
#from django.utils.datastructures import MultiValueDictKeyError

#from .models import ProductsInStores
#from users.models import Users

from purchases.models import PurchasesProductsDetails

def by_sku(request):
	if request.method == 'GET':
		sku = request.GET.get('sku', None)

		try:
			#user = Users.objects.get(pk=request.user)
			#product = ProductsInStores.objects.get(sku__iexact=sku, created_by_user=user)
			product = PurchasesProductsDetails.objects.get(sku__iexact=sku)
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': product.dropped, 'product': product.id, 'msg': _('The indicated SKU already exists')})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})