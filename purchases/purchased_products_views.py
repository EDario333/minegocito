from django.shortcuts import render

from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction,IntegrityError,DatabaseError

from brands.models import Brands
from stores.models import Stores
from products.models import Products
from .models import Purchases, PurchasesDetails, PurchasesProductsDetails

def save_purchased_product(request):
	context = {}

	if request.method == 'POST':
		original_product=request.POST.get('original_product',None)
		new_product=request.POST.get('new_product',None)
		try:
			ppd=PurchasesProductsDetails.objects.get(pk=original_product)
			#pd=PurchasesDetails.objects.get(pk=ppd.purchase_detail.pk)
			#print('************* PASO 1')
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The product you are trying to update does not exists')})

		try:
			product=Products.objects.get(pk=new_product)
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The selected product does not exists')})

		#pd.product=product
		ppd.purchase_detail.product=product

		brand=request.POST.get('brand',None)

		try:
			brand=Brands.objects.get(pk=brand)
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The selected brand does not exists')})

		#original_brand=pd.brand
		#pd.brand=brand
		ppd.purchase_detail.brand=brand

		#original_sku=ppd.sku
		ppd.sku=request.POST.get('sku',None)

		#original_purchase_price=pd.purchase_price
		#pd.purchase_price=request.POST.get('purchase_price',None)
		ppd.purchase_detail.purchase_price=request.POST.get('purchase_price',None)

		store=request.POST.get('store',None)

		try:
			store=Stores.objects.get(pk=store)
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The selected store does not exists')})

		#original_store=ppd.store
		ppd.in_store=store

		img=request.FILES.get('image', None)
		ppd.image=img

		with transaction.atomic():
			ppd.purchase_detail.save()
			ppd.save()
			#ppd.purchase_detail.refresh_from_db()
			#ppd.refresh_from_db()

		#img=request.POST.get('img',None)

		return JsonResponse({'status': 'success', 'msg': _('The purchased product was successfully updated')})

	return JsonResponse({'status': 'warning', 'msg': _('The requested operation cannot be performed')})

'''
def save_purchased_product(request):
	context = {}

	if request.method == 'POST':
		original_product=request.POST.get('original_product',None)
		new_product=request.POST.get('new_product',None)
		try:
			ppd=PurchasesProductsDetails.objects.get(pk=original_product)
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The product you are trying to update does not exists')})

		print('************* ppd')
		print(ppd)

		print('************* ppd.purchase_detail')
		print(ppd.purchase_detail)

		try:
			product=Products.objects.get(pk=new_product)
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The selected product does not exists')})

		#pd.product=product
		ppd.purchase_detail.product=product

		brand=request.POST.get('brand',None)

		try:
			brand=Brands.objects.get(pk=brand)
			print('brand')
			print(brand.name)
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The selected brand does not exists')})

		#original_brand=pd.brand
		#pd.brand=brand
		ppd.purchase_detail.brand=brand

		#original_sku=ppd.sku
		ppd.sku=request.POST.get('sku',None)

		#original_purchase_price=pd.purchase_price
		#pd.purchase_price=request.POST.get('purchase_price',None)
		print('************* ppd.purchase_detail.purchase_price ANTES DE SAVE **********')
		print(ppd.purchase_detail.purchase_price)

		ppd.purchase_detail.purchase_price=request.POST.get('purchase_price',None)

		store=request.POST.get('store',None)

		try:
			store=Stores.objects.get(pk=store)
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The selected store does not exists')})

		#original_store=ppd.store
		ppd.store=store

		ppd.purchase_detail.save()

		print('************* ppd.purchase_detail.purchase_price DESPUES DE SAVE **********')
		print(ppd.purchase_detail.purchase_price)

		print('************* ppd')
		print(ppd)

		print('************* ppd.purchase_detail')
		print(ppd.purchase_detail)

		img=request.POST.get('img',None)

		return JsonResponse({'status': 'success', 'msg': _('The purchased product was successfully updated')})

	return JsonResponse({'status': 'warning', 'msg': _('The requested operation cannot be performed')})
'''