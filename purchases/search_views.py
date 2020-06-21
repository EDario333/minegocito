from django.shortcuts import render, redirect

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
#from django.utils.datastructures import MultiValueDictKeyError

from .models import \
Purchases, \
PurchasesDetails, \
PurchasesProductsDetails

from products.models import Products

from users.models import Users

from django.core import serializers
import json

def by_identifier(request):
	if request.method == 'GET':
		identifier = request.GET.get('identifier', None)

		try:
			#user = Users.objects.get(pk=request.user)
			#product = ProductsInStores.objects.get(sku__iexact=sku, created_by_user=user)
			purchase = Purchases.objects.get(identifier__iexact=identifier)
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': purchase.dropped, 'purchase': purchase.id, 'msg': _('The indicated purchase identifier already exists')})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'exist': None, 'status': 'error', 'msg': _('You do not have permission to perform this request')})

'''
Same purchase = 
created_by_user, identifier, purchased_at, purchased_when 

See models for details
'''
def by_unique_purchase_user(request):
	if request.method == 'GET':
		identifier = request.GET.get('identifier', None)
		user = Users.objects.get(pk=request.user)
		purchased_at = request.GET.get('purchased_at', None)
		purchased_when = request.GET.get('purchased_when', None)
		purchased_when = purchased_when[6:] + '-' + purchased_when[3:5] + '-' + purchased_when[0:2]

		if purchased_at and purchased_at is not None:
			purchased_at = '\'' + purchased_at + '\''

		if purchased_when and purchased_when is not None:
			purchased_when = '\'' + purchased_when + '\''

		try:
			#user = Users.objects.get(pk=request.user)
			#product = ProductsInStores.objects.get(sku__iexact=sku, created_by_user=user)
			purchase = Purchases.objects.get(identifier__iexact=identifier, created_by_user=user, purchased_at__iexact=purchased_at, purchased_when__iexact=purchased_when)
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': purchase.dropped, 'purchase': purchase.id, 'msg': _('One purchase was done at the specified date time and identifier already exists')})
		except ObjectDoesNotExist as e:
			try:
				# Verify also its owner identifier
				purchase = Purchases.objects.get(identifier__iexact=identifier, created_by_user=user)

				return JsonResponse({'exist': True, 'status': 'info', 'dropped': purchase.dropped, 'purchase': purchase.id, 'msg': _('One purchase with the specified identifier already exists')})
			except ObjectDoesNotExist as e2:
				pass

		return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'exist': None, 'status': 'error', 'msg': _('You do not have permission to perform this request')})

def by_product_sku(request):
	if request.method == 'GET':
		sku = request.GET.get('sku', None)
		sold = request.GET.get('sold', False)
		sold = sold.upper()=='TRUE'
		user = Users.objects.get(pk=request.user)

		try:
			ppd = PurchasesProductsDetails.objects.get(sku__iexact=sku,created_by_user=user,dropped=False,stored=True,sold=sold)
			data={
				'ppd': ppd.id,
				'sku': ppd.sku,
				'product': ppd.purchase_detail.product.name,
				'brand': ppd.purchase_detail.brand.name,
				'purchase_price': str(ppd.purchase_detail.purchase_price),
				'sale_price': str(ppd.purchase_detail.sale_price)
			}
			#data = serializers.serialize('json', [ppd])
			data=json.dumps(data)
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': ppd.dropped, 'product': data, 'msg': _('We found one record matching with your query')})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'exist': None, 'status': 'error', 'msg': _('You do not have permission to perform this request')})

def by_product_name(request):
	if request.method == 'GET':
		product = request.GET.get('product', None)
		sold = request.GET.get('sold', False)
		sold = sold.upper()=='TRUE'
		user = Users.objects.get(pk=request.user)
		products=[]

		try:
			product = Products.objects.get(name__icontains=product,dropped=False,created_by_user=user)
			pd=PurchasesDetails.objects.filter(product=product,dropped=False,created_by_user=user)
			ppd=PurchasesProductsDetails.objects.filter(purchase_detail__in=pd,created_by_user=user,dropped=False,stored=True,sold=sold).exclude(sku=None)
			products.extend(ppd)

			if len(products) > 1:
				return JsonResponse({'exist': True, 'status': 'info', 'multiple': True, 'products': serializers.serialize('json', products), 'msg': _('We found more than one record matching your query')})
			elif len(products) == 1:
				ppd=products[0]
				data={
					'ppd': ppd.id,
					'sku': ppd.sku,
					'product': ppd.purchase_detail.product.name,
					'brand': ppd.purchase_detail.brand.name,
					'purchase_price': str(ppd.purchase_detail.purchase_price),
					'sale_price': str(ppd.purchase_detail.sale_price)
				}
				data=json.dumps(data)
				return JsonResponse({'exist': True, 'status': 'info', 'dropped': products[0].dropped, 'product': data, 'msg': _('One purchase was done with the specified SKU product')})
			else:
				raise ObjectDoesNotExist(_('We can not find any product matching with your query options'))
		except ObjectDoesNotExist as e:
			print(e.args[0])
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'exist': None, 'status': 'error', 'msg': _('You do not have permission to perform this request')})