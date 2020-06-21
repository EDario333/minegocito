from django.shortcuts import render, redirect

#from django.contrib.auth.models import User

from django.db.models import Q

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from .forms import FrmPurchases
from .models import Purchases
from users.models import Users

from products.views import get_products_created_by_user
from products.models import Products

from brands.views import get_brands_created_by_user
from brands.models import Brands

from stores.views import get_stores_created_by_user
from stores.models import Stores

from datetime import datetime

def __get_purchases_created_by_user__(request):
	purchases = Purchases.objects.filter(created_by_user=request.user, dropped=False)

	return purchases

def add(request):
	context = {}
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	context['itm_menu'] = itm_menu

	if get_products_created_by_user(request) < 1:
		return render(request, 'purchases/user-have-no-products-created.html', context={'itm_menu': itm_menu})

	if len(get_brands_created_by_user(request)) < 1:
		return render(request, 'purchases/user-have-no-brands-created.html', context={'itm_menu': itm_menu})

	if request.method == 'GET':
		frm = FrmPurchases(title=_('Add purchase'), action='/purchases/do-add', btn_label=_('Save'), icon_btn_submit='save')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['app_version'] = app_version
		'''
		if app_version == _('Free version'):
			if __get_products_created_by_user__(request) > 0:
				return render(request, 'products/add-free-version-limited.html', context={'itm_menu': itm_menu})
		'''
	#html = render(request, 'products/add.html', context={'form': frm})
	#return JsonResponse({'result': True, 'html': html})
	return render(request, 'purchases/add.html', context=context)

def find(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(__get_purchases_created_by_user__(request)) < 1:
			return render(request, 'purchases/user-have-no-purchases-created.html', context={'itm_menu': itm_menu})

		frm = FrmPurchases(title=_('Find purchase'), action='/purchases/do-find', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'purchases/find.html', context=context)

def do_add(request):
	frm = FrmPurchases(title=_('Add purchase'), action='/purchases/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The purchase can not be saved')
	context['level'] = 'error'

	if request.method == 'POST':
		try:
			app_version = request.POST['app_version']
			itm_menu = request.POST.get('itm_menu', '')
			context['itm_menu'] = itm_menu
			'''
			if app_version == _('Free version'):
				if __get_products_created_by_user__(request) > 0:
					return render(request, 'products/add-free-version-limited.html', context={'itm_menu': itm_menu})
			'''
			context['app_version'] = app_version

			# Retrieve the user who is creating the product
			#user = User.objects.get(email=request.POST.get('user', None))
			my_user = Users.objects.get(pk=request.user)

			product = request.POST.get('product_obj', None)
			product = Products.objects.get(pk=product)

			brand = request.POST.get('brand_obj', None)
			brand = Brands.objects.get(pk=brand)

			quantity = request.POST.get('quantity', 0)
			purchase_price = request.POST.get('purchase_price', 0.00)

			#store = request.POST.get('store_obj', None)
			#store = Stores.objects.get(pk=store)

			purchased_at = request.POST.get('purchased_at', None)
			purchased_when = request.POST.get('purchased_when', None)

			identifier = request.POST.get('identifier', None)

			# Check if the purchase does not exist
			# (same purchase = product, brand, created_by_user, 
			# purchased_at, purchased_when see models for details)

			try:
				obj = Purchases.objects.get(product=product, brand=brand, created_by_user=my_user)

				if not obj.dropped:
					context['msg'] = _('The purchase already exist')
					context['level'] = 'error'
				else:
					obj.quantity = quantity
					obj.purchase_price = purchase_price
					obj.undrop()
					context['msg'] = _('The purchase has been successfully saved')
					context['level'] = 'success'

				return render(request, 'purchases/add.html', context=context)
			except ObjectDoesNotExist:
				# Verify also its owner identifier
				obj = Purchases.objects.get(identifier=identifier, created_by_user=my_user)
				if not obj.dropped:
					context['msg'] = _('The purchase already exist')
					context['level'] = 'error'
				else:
					obj.quantity = quantity
					obj.purchase_price = purchase_price
					obj.undrop()
					context['msg'] = _('The purchase has been successfully saved')
					context['level'] = 'success'

				return render(request, 'purchases/add.html', context=context)
			except ObjectDoesNotExist:
				pass

			obj = Purchases(product=product, \
				brand=brand, quantity=quantity, \
				purchase_price=purchase_price, \
				created_by_user=my_user, \
				purchased_at=purchased_at, \
				purchased_when=purchased_when)

			obj.save()
			context['msg'] = _('The purchase has been successfully saved')
			context['level'] = 'success'
		except MultiValueDictKeyError:
			print('********ERROR1*******')
			return redirect('/')
		except ObjectDoesNotExist:
			print('********ERROR2*******')
			return redirect('/')

	return render(request, 'purchases/add.html', context=context)

def __generic_find_view__(request, can_delete=False, can_edit=False, view_all=False):
	frm = FrmPurchases(title=_('Find purchase'), action='/purchases/do-find', btn_label=_('Find'), icon_btn_submit='search')
	context = {}
	context['msg'] = _('We can not find any purchase matching with your query options')
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
				'quantity': False, 'purchase_price': False,
				'purchased_at': False, 'purchased_when': False
			}

			product = request.POST.get('product_obj', None)
			if product and product is not None and len(product.strip()) > 0:
				search_by['product'] = product.strip()

			brand = request.POST.get('brand_obj', None)
			if brand and brand is not None and len(brand.strip()) > 0:
				search_by['brand'] = brand.strip()

			quantity = request.POST.get('quantity', None)
			if quantity and quantity is not None and len(quantity.strip()) > 0:
				search_by['quantity'] = quantity.strip()

			purchase_price = request.POST.get('purchase_price', None)
			if purchase_price and purchase_price is not None and len(purchase_price.strip()) > 0:
				search_by['purchase_price'] = purchase_price.strip()

			purchased_at = request.POST.get('purchased_at', None)
			if purchased_at and purchased_at is not None and len(purchased_at.strip()) > 0:
				search_by['purchased_at'] = purchased_at.strip()

			purchased_when = request.POST.get('purchased_when', None)
			if purchased_when and purchased_when is not None and len(purchased_when.strip()) > 0:
				search_by['purchased_when'] = purchased_when.strip()

			# Retrieve the user logged in
			#user = User.objects.get(email=request.GET.get('user', ''))
			#my_user = Users.objects.get(pk=user.id)
			#user = Users.objects.get(pk=request.user)
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

			purchases = Purchases.objects.filter(query)
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

		# Retrieve the user logged in
		#user = User.objects.get(email=request.GET.get('user', ''))
		#my_user = Users.objects.get(pk=user.id)
		query = Q(created_by_user=my_user) & Q(dropped=False)
		purchases = Purchases.objects.filter(query)

	if len(purchases) > 0:
		context['purchases'] = purchases

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmProductsInStores(title=_('Edit purchase'), action='/purchases/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmProductsInStores(title=_('Delete purchase'), action='/purchases/do-delete', btn_label=_('Find'), icon_btn_submit='search')

	context['form'] = frm

	return render(request, 'purchases/find.html', context=context)

def do_find(request):
	return __generic_find_view__(request)

def do_view_all(request):
	if request.method == 'GET':
		edit = request.GET.get('edit', False)
		delete = request.GET.get('delete', False)
		return __generic_find_view__(request, view_all=True, can_edit=edit, can_delete=delete)

	return __generic_find_view__(request, view_all=True, can_edit=False, can_delete=False)

def edit(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(__get_purchases_created_by_user__(request)) < 1:
			return render(request, 'purchases/user-have-no-purchases-created.html', context={'itm_menu': itm_menu})

		frm = FrmPurchases(title=_('Edit purchase'), action='/purchases/do-edit', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'purchases/find.html', context=context)

def do_edit(request):
	return __generic_find_view__(request, can_edit=True)

def delete(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(__get_purchases_created_by_user__(request)) < 1:
			return render(request, 'purchases/user-have-no-purchases-created.html', context={'itm_menu': itm_menu})

		frm = FrmPurchases(title=_('Delete purchase'), action='/purchases/do-delete', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'purchases/find.html', context=context)

def do_delete(request):
	return __generic_find_view__(request, can_delete=True)

def view_details(request):
	if request.method == 'GET':
		try:
			purchase = request.GET.get('obj', None)
			purchase = Purchases.objects.get(pk=purchase)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'purchase': purchase, 'can_edit': can_edit, 
				'can_delete': can_delete, 'itm_menu': itm_menu
			}

			return render(request, 'purchases/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def confirm_delete(request):
	if request.method == 'GET':
		try:
			purchase = request.GET.get('purchase', None)
			purchase = Purchases.objects.get(pk=purchase)

			context = {
				'purchase': purchase, 
				'can_delete': True
			}

			return render(request, 'purchases/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def delete_purchase(request):
	if request.method == 'POST':
		try:
			purchase = request.POST.get('purchase', None)
			purchase = Purchases.objects.get(pk=purchase)
			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			purchase.drop(reason=reason)

			frm = FrmPurchases(title=_('Delete purchase'), action='/products-stores/do-delete', btn_label=_('Find'), icon_btn_submit='search')
			#app_version = request.GET['app_version']
			#context['form'] = frm
			#context['itm_menu'] = itm_menu

			context = {
				'level': 'success',
				'msg': _('The purchase has been deleted successfully'),
				'itm_menu': itm_menu,
				'form': frm
			}

			return render(request, 'purchases/find.html', context=context)
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

			price = request.POST.get('price', 0.00)
			today = datetime.now()
			purchased_at = request.POST.get('purchased_at', today)
			purchased_when = request.POST.get('purchased_when', today)

			purchase = request.POST.get('purchase', None)
			purchase = Purchases.objects.get(pk=purchase)

			purchase.product = product
			purchase.brand = brand
			purchase.quantity = quantity
			purchase.price = price
			purchase.purchased_at = purchased_at
			purchase.purchased_when = purchased_when

			product.save()
			msg = _('The purchase has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The purchase you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

'''
def add_product_details(request):
	if request.method == 'GET':
		item_counter = request.GET.get('item_counter', 0)

		if int(item_counter) < 1:
			msg = _('Invalid value to perform this request')
			return JsonResponse({'status': 'error', 'msg': msg})
		else:
			context = {'n_product': int(item_counter)}
			return render(request, 'purchases/product-details.html', context=context)

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})
'''

def product_details(request):
	if request.method == 'GET':
		product = request.GET.get('product', None)
		product_obj = request.GET.get('product_obj', None)
		brand = request.GET.get('brand', None)
		brand_obj = request.GET.get('brand_obj', None)
		purchase_price = request.GET.get('purchase_price', None)
		quantity = request.GET.get('quantity', None)
		description = request.GET.get('description', None)
		notes = request.GET.get('notes', None)
		row_number = request.GET.get('row_number', None)
		enter_and_edit = request.GET.get('enter_and_edit', False)
		skus = request.GET.get('skus', None)
		imgs = request.GET.get('images', None)

		context = {
			'product': product,
			'product_obj': product_obj,
			'brand': brand,
			'brand_obj': brand_obj,
			'purchase_price': purchase_price,
			'quantity': quantity,
			'description': description,
			'notes': notes,
			'row_number': row_number,
			'enter_and_edit': enter_and_edit,
			'skus': skus, 'images': imgs
		}

		return render(request, 'purchases/dlg-product-details.html', context=context)

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def sku_products(request):
	if request.method == 'GET':
		products_quantity = request.GET.get('quantity', 0)
		with_data = request.GET.get('with_data', False)
		editting = request.GET.get('enter_and_edit', True)

		if with_data:
			skus = request.GET.get('skus', None)
			imgs = request.GET.get('images', None)
			skus = skus.split(',')
			if imgs is not None:
				imgs = imgs.split(',')
			products_quantity = len(skus)

		products = []

		if not with_data:
			for x in range(int(products_quantity)):
				product = {
					'counter': x + 1,
					'sku': '',
					'image': ''
				}
				#products.append(x+1)
				products.append(product)
		else:
			print('*********imgs********')
			print(imgs)
			for x in range(int(products_quantity)):
				product = {
					'counter': x + 1,
					'sku': skus[x]
					#'image': imgs[x]
				}
				if imgs is not None and len(imgs) > 0:
					try:
						product['image'] = imgs[x]
					except IndexError:
						product['image'] = ''
				else:
					product['image'] = ''
				products.append(product)

		context = {
			'products': products,
			'products_total': len(products),
			'with_data': with_data,
			'editting': editting
		}

		#if with_data:
			#context['skus'] = skus

		return render(request, 'purchases/products-details.html', context=context)

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})
