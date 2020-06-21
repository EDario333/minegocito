from django.shortcuts import render, redirect

#from django.contrib.auth.models import User

#from django.db.models import Q
from django.db import transaction

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
#from django.utils.datastructures import MultiValueDictKeyError

#from .forms import FrmProductsInStores
#from .models import Products, ProductsInStores
#from users.models import Users
'''
from products.views import get_products_created_by_user
from stores.views import get_stores_created_by_user
'''
import json
from stores.models import Stores
from django.views.generic.list import ListView

from purchases.models import \
PurchasesProductsDetails, \
Purchases

from products.models import Products
from brands.models import Brands

def __get_purchases_by_user__(request):
	products = Purchases.objects.filter(created_by_user=request.user, dropped=False)

	return products

def add(request):
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	if len(__get_purchases_by_user__(request)) < 1:
		return render(request, 'products-stores/user-have-no-purchases.html', context={'itm_menu': itm_menu})

	if request.method == 'GET':
		context = {}
		#frm = FrmProductsInStores(title=_('Add product in store'), action='/products-stores/do-add', btn_label=_('Save'), icon_btn_submit='save')
		app_version = request.GET['app_version']
		#context['form'] = frm
		context['itm_menu'] = itm_menu
		context['app_version'] = app_version
	else:
		msg = _('You do not have permission to perform this request')
		return JsonResponse({'status': 'error', 'msg': msg})

	return render(request, 'products-stores/add.html', context=context)

def find(request):
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	if len(__get_purchases_by_user__(request)) < 1:
		return render(request, 'products-stores/user-have-no-purchases.html', context={'itm_menu': itm_menu})

	if request.method == 'GET':
		context = {}
		app_version = request.GET['app_version']
		context['itm_menu'] = itm_menu
		context['app_version'] = app_version
		context['can_delete'] = False
		context['can_edit'] = False
	else:
		msg = _('You do not have permission to perform this request')
		return JsonResponse({'status': 'error', 'msg': msg})

	return render(request, 'products-stores/find.html', context=context)

def view_details(request):
	if request.method == 'GET':
		try:
			product = request.GET.get('obj', None)
			product = PurchasesProductsDetails.objects.get(pk=product)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'product': product, 'can_edit': can_edit, 
				'can_delete': can_delete, 'itm_menu': itm_menu
			}

			return render(request, 'products-stores/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def edit(request):
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	if len(__get_purchases_by_user__(request)) < 1:
		return render(request, 'products-stores/user-have-no-purchases.html', context={'itm_menu': itm_menu})

	if request.method == 'GET':
		context = {}
		app_version = request.GET.get('app_version', _('Free version'))
		context['itm_menu'] = itm_menu
		context['can_edit'] = True
		context['can_delete'] = False

	return render(request, 'products-stores/edit.html', context=context)
'''
def do_edit(request):
	return __generic_find_view__(request, can_edit=True)
'''
def delete(request):
	itm_menu = request.GET.get('itm_menu', 'lnk1')

	if len(__get_purchases_by_user__(request)) < 1:
		return render(request, 'products-stores/user-have-no-purchases.html', context={'itm_menu': itm_menu})

	if request.method == 'GET':
		context = {}
		app_version = request.GET.get('app_version', _('Free version'))
		context['itm_menu'] = itm_menu
		context['can_delete'] = True
		context['can_edit'] = False

	return render(request, 'products-stores/delete.html', context=context)
'''
def do_delete(request):
	return __generic_find_view__(request, can_delete=True)
'''
def delete_product(request):
	if request.method == 'POST':
		try:
			product = request.POST.get('productstore', None)
			product = PurchasesProductsDetails.objects.get(pk=product)

			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			#product.drop(reason=reason)
			product.in_store = None
			product.stored = False
			product.save()

			context = {
				'level': 'success',
				'msg': _('The product has been removed from its store'),
				'itm_menu': itm_menu,
				'can_edit': False,
				'can_delete': True
			}

			return render(request, 'products-stores/delete.html', context=context)
			#return render(request, 'products-stores/find.html', context=context)
			#return JsonResponse({'status': 'success', 'msg': context['msg']})
		except ObjectDoesNotExist:
			#return JsonResponse({'status': 'error', 'msg': _('The product you are trying to update does not exist')})
			return redirect('/')

	return redirect('/')

def update(request):
	context = {}

	if request.method == 'POST':
		module = request.POST.get('module', None)
		if module is not None and module.upper() == 'EDIT-DETAILS':
			ppd = request.POST.get('productstore', None)
			try:
				ppd = PurchasesProductsDetails.objects.get(pk=ppd)
			except ObjectDoesNotExist:
				msg = _('The product you are trying to update does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})
			image = request.FILES.get('image', None)
			product = request.POST.get('product_obj', None)
			try:
				product = Products.objects.get(pk=product)
			except ObjectDoesNotExist:
				msg = _('The selected product does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})
			brand = request.POST.get('brand_obj', None)
			try:
				brand = Brands.objects.get(pk=brand)
			except ObjectDoesNotExist:
				msg = _('The selected brand does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})
			sku = request.POST.get('sku', None)
			p_at = request.POST.get('purchased_at', None)
			p_when = request.POST.get('purchased_when', None)
			p_id = request.POST.get('purchase_id', None)
			store = request.POST.get('store_obj', None)
			try:
				store = Stores.objects.get(pk=store)
			except ObjectDoesNotExist:
				msg = _('The selected store does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})
			price = request.POST.get('purchase_price', None)
			#ppd = PurchasesProductsDetails()
			ppd.image = image
			ppd.sku = sku
			ppd.stored = store is not None
			ppd.in_store = store
			ppd.purchase_detail.product = product
			ppd.purchase_detail.brand = brand
			ppd.purchase_detail.purchase_price = price
			ppd.purchase_detail.purchase.purchased_at = p_at
			p_when = p_when[6:] + '-' + p_when[3:5] + '-' + p_when[0:2]
			ppd.purchase_detail.purchase.purchased_when = p_when
			ppd.purchase_detail.purchase.identifier = p_id

			with transaction.atomic():
				ppd.purchase_detail.purchase.save()
				ppd.purchase_detail.save()
				ppd.save()

				msg = _('The product has been updated successfully')
				return JsonResponse({'status': 'success', 'msg': msg})
		else:
			try:
				product = request.POST.get('product', None)
				product = PurchasesProductsDetails.objects.get(pk=product)

				sku = request.POST.get('sku', None)
				store = request.POST.get('store', None)
				#itm_menu = request.POST.get('itm_menu', 'lnk1')

				product.stored = \
					store is not None and len(store.strip())>0

				product.in_store = None

				if product.stored:
					try:
						#product.in_store = Stores.objects.get(pk=store)
						product.in_store = Stores.objects.get(pk=store)
					except ObjectDoesNotExist:
						return JsonResponse({'status': 'error', 'msg': _('The store does not exists')})

				product.sku = sku
				product.save()
				msg = _('The product has been updated successfully')
				#context['status'] = 'success'
				#context['can_edit'] = True
				#context['can_delete'] = False
				#context['itm_menu'] = itm_menu
				return JsonResponse({'status': 'success', 'msg': msg})
				#return render(request, 'products-stores/find.html', context=context)

			except ObjectDoesNotExist:
				msg = _('The product you are trying to update does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})
	else:
		msg = _('You do not have permission to perform this request')
		return JsonResponse({'status': 'error', 'msg': msg})

	return render(request, 'products-stores/edit.html', context=context)

def remove_many_from_stores(request):
	if request.method == 'POST':
		try:
			products = request.POST.get('products', None)
			products = json.loads(products)

			itm_menu = request.POST.get('itm_menu', 'lnk1')

			with transaction.atomic():
				for product in products:
					product_obj = PurchasesProductsDetails.objects.get(pk=product)

					product_obj.in_store = None
					product_obj.stored = False
					product_obj.save()

				context = {
					'level': 'success',
					'msg': _('The products has been removed from their stores'),
					'itm_menu': itm_menu,
					'can_edit': False,
					'can_delete': True
				}

				return render(request, 'products-stores/delete.html', context=context)
			#return JsonResponse({'status': 'success', 'msg': context['msg']})
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('The product you are trying to remove from its store does not exists')})
			#return redirect('/')

	return redirect('/')
'''
def __get_products_in_stores_created_by_user__(request):
	products = ProductsInStores.objects.filter(created_by_user=request.user, dropped=False)

	return products

def add(request):
	context = {}
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	context['itm_menu'] = itm_menu

	if get_products_created_by_user(request) < 1:
		return render(request, 'products-stores/user-have-no-products-created.html', context={'itm_menu': itm_menu})

	if len(get_brands_created_by_user(request)) < 1:
		return render(request, 'products-stores/user-have-no-brands-created.html', context={'itm_menu': itm_menu})

	if len(get_stores_created_by_user(request)) < 1:
		return render(request, 'products-stores/user-have-no-stores-created.html', context={'itm_menu': itm_menu})

	if request.method == 'GET':
		frm = FrmProductsInStores(title=_('Add product in store'), action='/products-stores/do-add', btn_label=_('Save'), icon_btn_submit='save')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['app_version'] = app_version

	return render(request, 'products-stores/add.html', context=context)

def find(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(__get_products_in_stores_created_by_user__(request)) < 1:
			return render(request, 'products-stores/user-have-no-products-in-stores-created.html', context={'itm_menu': itm_menu})

		frm = FrmProductsInStores(title=_('Find product in store'), action='/products-stores/do-find', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'products-stores/find.html', context=context)

def do_add(request):
	frm = FrmProductsInStores(title=_('Add product in store'), action='/products-stores/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The product can not be saved')
	context['level'] = 'error'

	if request.method == 'POST':
		try:
			app_version = request.POST['app_version']
			itm_menu = request.POST.get('itm_menu', '')
			context['itm_menu'] = itm_menu
			context['app_version'] = app_version

			# Retrieve the user who is creating the product
			#user = User.objects.get(email=request.POST.get('user', None))
			my_user = Users.objects.get(pk=request.user)

			product = request.POST.get('product_obj', None)
			product = Products.objects.get(pk=product)

			brand = request.POST.get('brand_obj', None)
			brand = Brands.objects.get(pk=brand)

			store = request.POST.get('store_obj', None)
			store = Stores.objects.get(pk=store)

			sku = request.POST.get('sku', None)
			quantity = request.POST.get('quantity', 0)
			price = request.POST.get('price', 0.00)
			photo = request.FILES.get('photo', None)

			# Check if the products does not exist
			# (same product = product_name)

			try:
				obj = ProductsInStores.objects.get(product=product, brand=brand, store=store, created_by_user=my_user)

				if not obj.dropped:
					context['msg'] = _('The product already exist')
					context['level'] = 'error'
				else:
					obj.quantity = quantity
					obj.price = price
					obj.photo = photo
					obj.sku = sku
					obj.undrop()
					context['msg'] = _('The product has been successfully saved')
					context['level'] = 'success'

				return render(request, 'products-stores/add.html', context=context)
			except ObjectDoesNotExist:
				pass

			obj = ProductsInStores(product=product, \
				brand=brand, store=store, \
				quantity=quantity, price=price, photo=photo,\
				created_by_user=my_user, sku=sku)

			obj.save()
			context['msg'] = _('The product has been successfully saved')
			context['level'] = 'success'
		except MultiValueDictKeyError:
			print('********ERROR1*******')
			return redirect('/')
		except ObjectDoesNotExist:
			print('********ERROR2*******')
			return redirect('/')

	return render(request, 'products-stores/add.html', context=context)

def __generic_find_view__(request, can_delete=False, can_edit=False, view_all=False):
	frm = FrmProductsInStores(title=_('Find product in store'), action='/products-stores/do-find', btn_label=_('Find'), icon_btn_submit='search')
	context = {}
	context['msg'] = _('We can not find any product matching with your query options')
	context['level'] = 'error'
	products = Products.objects.none()
	itm_menu = request.POST.get('itm_menu', request.GET.get('itm_menu', ''))
	context['itm_menu'] = itm_menu
	#context['url_view_all'] = '/products/list-all/'
	# Retrieve the user logged in
	my_user = Users.objects.get(pk=request.user)

	if request.method == 'POST':
		try:
			app_version = request.POST.get('app_version', _('Free version'))
			#itm_menu = request.POST.get('itm_menu', '')
			#context['itm_menu'] = itm_menu
			context['app_version'] = app_version

			search_by = {
				'product': False, 'brand': False,
				'store': False, 'quantity': False,
				'price': False, 'sku__iexact': False
			}

			product = request.POST.get('product_obj', None)
			if product and product is not None and len(product.strip()) > 0:
				search_by['product'] = product.strip()

			brand = request.POST.get('brand_obj', None)
			if brand and brand is not None and len(brand.strip()) > 0:
				search_by['brand'] = brand.strip()

			store = request.POST.get('store_obj', None)
			if store and store is not None and len(store.strip()) > 0:
				search_by['store'] = store.strip()

			quantity = request.POST.get('quantity', None)
			if quantity and quantity is not None and len(quantity.strip()) > 0:
				search_by['quantity'] = quantity.strip()

			price = request.POST.get('price', None)
			if price and price is not None and len(price.strip()) > 0:
				search_by['price'] = price.strip()

			sku = request.POST.get('sku', None)
			if sku and sku is not None and len(sku.strip()) > 0:
				search_by['sku__iexact'] = sku.strip()

			query = Q(created_by_user=my_user) & Q(dropped=False)

			final_search_by = {}

			for criteria in search_by:
				if search_by[criteria]:
					final_search_by[criteria] = search_by[criteria]

			# Build the query...
			# See https://stackoverflow.com/questions/38131563/django-filter-with-or-condition-using-dict-argument
			# for more details
			from functools import reduce
			import operator
			query &= reduce(operator.or_, (Q(**d) for d in [dict([i]) for i in final_search_by.items()]))

			products = ProductsInStores.objects.filter(query)
			#context['msg'] = _('We found {0} result(s) matching your query').format(len(products))
			#context['level'] = "success"
		except MultiValueDictKeyError:
			return redirect('/')
		except ObjectDoesNotExist:
			return redirect('/')
	elif view_all:
		app_version = request.GET.get('app_version', _('Free version'))
		itm_menu = request.GET.get('itm_menu', 'lnk1')
		context['itm_menu'] = itm_menu
		context['app_version'] = app_version

		query = Q(created_by_user=my_user) & Q(dropped=False)
		products = ProductsInStores.objects.filter(query)

	if len(products) > 0:
		context['products'] = products

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmProductsInStores(title=_('Edit product in store'), action='/products-stores/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmProductsInStores(title=_('Delete product in store'), action='/products-stores/do-delete', btn_label=_('Find'), icon_btn_submit='search')

	context['form'] = frm

	return render(request, 'products-stores/find.html', context=context)

def do_find(request):
	return __generic_find_view__(request)

def do_view_all(request):
	if request.method == 'GET':
		edit = request.GET.get('edit', False)
		delete = request.GET.get('delete', False)
		return __generic_find_view__(request, view_all=True, can_edit=edit, can_delete=delete)

	return __generic_find_view__(request, view_all=True, can_edit=False, can_delete=False)

def view_details(request):
	if request.method == 'GET':
		try:
			product = request.GET.get('obj', None)
			product = ProductsInStores.objects.get(pk=product)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'product': product, 'can_edit': can_edit, 
				'can_delete': can_delete, 'itm_menu': itm_menu
			}

			return render(request, 'products-stores/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def confirm_delete(request):
	if request.method == 'GET':
		try:
			product = request.GET.get('product', None)
			product = ProductsInStores.objects.get(pk=product)

			context = {
				'product': product, 
				'can_delete': True
			}

			return render(request, 'products-stores/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def delete_product(request):
	if request.method == 'POST':
		try:
			product = request.POST.get('product', None)
			product = ProductsInStores.objects.get(pk=product)
			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			product.drop(reason=reason)

			frm = FrmProductsInStores(title=_('Delete product in store'), action='/products-stores/do-delete', btn_label=_('Find'), icon_btn_submit='search')
			#app_version = request.GET['app_version']
			#context['form'] = frm
			#context['itm_menu'] = itm_menu

			context = {
				'level': 'success',
				'msg': _('The product has been deleted successfully'),
				'itm_menu': itm_menu,
				'form': frm
			}

			return render(request, 'products-stores/find.html', context=context)
			#return find(request)
			#return redirect('/products/find')
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def update(request):
	if request.method == 'POST':
		try:
			product = request.POST.get('product_obj', None)
			product = Products.objects.get(pk=product)

			brand = request.POST.get('brand_obj', None)
			brand = Brands.objects.get(pk=brand)

			store = request.POST.get('store_obj', None)
			store = Stores.objects.get(pk=store)

			sku = request.POST.get('sku', None)
			quantity = request.POST.get('quantity', 0)
			price = request.POST.get('price', 0.00)
			photo = request.FILES.get('photo', None)

			product_in_store = request.POST.get('productstore', None)
			product_in_store = ProductsInStores.objects.get(pk=product_in_store)

			product_in_store.product = product
			product_in_store.brand = brand
			product_in_store.store = store
			product_in_store.sku = sku
			product_in_store.quantity = quantity
			product_in_store.price = price
			product_in_store.photo = photo

			print('************voy')
			product.save()
			print('************voy2')
			msg = _('The product has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The product you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})
'''

class ProductsPurchasedView(ListView):
	user = None
	object_list = PurchasesProductsDetails.objects.none()

	def __init__(self, user=None, stored=False, all=False, *args, **kwargs):
		super(ProductsPurchasedView, self).__init__(*args, **kwargs)
		self.user = user
		if not all:
			self.object_list = PurchasesProductsDetails.objects.filter(created_by_user=user, stored=stored)
		else:
			self.object_list = PurchasesProductsDetails.objects.filter(created_by_user=user)