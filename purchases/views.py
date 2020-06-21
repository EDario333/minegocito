from django.shortcuts import render, redirect

#from django.contrib.auth.models import User

from django.db.models import Q

from django.db import transaction

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from .forms import FrmPurchases
from .models import Purchases, PurchasesDetails, PurchasesProductsDetails
from users.models import Users

from products.views import get_products_created_by_user
from products.models import Products

from brands.views import get_brands_created_by_user
from brands.models import Brands

from stores.views import get_stores_created_by_user
from stores.models import Stores

from providers.views import get_providers_created_by_user
from providers.models import Providers

from datetime import datetime

import json

dummy = _('Please add at least one product to this purchase')
dummy = _('Please enter a valid number')

dummy = _('Please enter a valid purchase price')
dummy = _('Please enter a valid quantity')
dummy = _('Product was added to the current purchase')
dummy = _('The product already was added to the purchase')
dummy = _('Msg specified identifier already exists with dropped purchase')

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

	if len(get_providers_created_by_user(request)) < 1:
		return render(request, 'purchases/user-have-no-providers-created.html', context={'itm_menu': itm_menu})

	if request.method == 'GET':
		frm = FrmPurchases(user=request.user, title=_('Add purchase'), action='/purchases/do-add', btn_label=_('Save'), icon_btn_submit='save')
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
	frm = FrmPurchases(user=request.user, title=_('Add purchase'), action='/purchases/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The purchase can not be saved')
	context['level'] = 'error'

	if request.method == 'POST':
		try:
			app_version = request.POST.get('app_version', _('Free version'))
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

			purchase_identifier = request.POST.get('identifier', None)
			if purchase_identifier is not None and len(purchase_identifier.strip()) < 1:
				purchase_identifier = None

			purchased_at = request.POST.get('purchased_at', None)
			purchased_when = request.POST.get('purchased_when', None)

			description = request.POST.get('description', None)
			notes = request.POST.get('notes', None)

			products = request.POST.get('products', None)
			products = json.loads(products)
			#print('***********products*********')
			#print(products)

			#print('************files*******')
			#print(request.FILES)

			# Check if the purchase does not exist
			# (same purchase = created_by_user, identifier,
			# purchased_at, purchased_when see models for details)
			try:
				obj = Purchases.objects.get(created_by_user=my_user, identifier__iexact=purchase_identifier, purchased_at__iexact=purchased_at, purchased_when__iexact=purchased_when)

				if not obj.dropped:
					context['msg'] = _('One purchase was done at the specified date time and identifier already exists')
					context['level'] = 'error'
				else:
					# *****************************
					# *****************************
					# Componer!!!
					# *****************************
					# *****************************
					obj.quantity = quantity
					obj.purchase_price = purchase_price
					obj.undrop()
					context['msg'] = _('The purchase has been successfully saved')
					context['level'] = 'success'

				return render(request, 'purchases/add.html', context=context)
			except ObjectDoesNotExist:
				try:
					# Verify also its owner identifier
					obj = Purchases.objects.get(identifier__iexact=purchase_identifier, created_by_user=my_user)
					if not obj.dropped:
						context['msg'] = _('One purchase with the specified identifier already exists')
						context['level'] = 'error'
					else:
						# *****************************
						# *****************************
						# Componer!!!
						# *****************************
						# *****************************
						obj.quantity = quantity
						obj.purchase_price = purchase_price
						obj.undrop()
						context['msg'] = _('The purchase has been successfully saved')
						context['level'] = 'success'

					return render(request, 'purchases/add.html', context=context)
				except ObjectDoesNotExist:
				#except Purchases.DoesNotExist:
					pass

			all_products_in_same_store = request.POST.get('all-products-in-store', False)
			store = None

			if all_products_in_same_store:
				store = request.POST.get('store_obj', None)
				try:
					print('********store******')
					print(store)
					store = Stores.objects.get(pk=store)
				except ObjectDoesNotExist:
					pass

			provider=request.POST.get('provider_obj', None)
			try:
				provider=Providers.objects.get(pk=provider)
			except ObjectDoesNotExist:
				context['msg'] = _('The specified provider does not exists')
				context['level'] = 'error'
				return render(request, 'purchases/add.html', context=context)

			purchase = Purchases()
			purchase.provider=provider
			purchase.identifier = purchase_identifier
			purchase.purchased_at = purchased_at
			purchase.purchased_when = purchased_when[6:] + '-' + purchased_when[3:5] + '-' + purchased_when[0:2]
			purchase.purchased_date=purchase.purchased_when+' '+purchase.purchased_at
			purchase.description = description
			purchase.notes = notes
			purchase.created_by_user = my_user

			with transaction.atomic():
				purchase.save()

				'''
				print('**********purchase*******')
				print(purchase)
				'''

				#counter = -1
				for product in products:
					#counter += 1
					#print('********product******')
					#print(product)
					product_obj = Products.objects.get(pk=product['id'])
					brand = Brands.objects.get(pk=product['brand']['id'])
					pd = PurchasesDetails()
					pd.purchase = purchase
					pd.product = product_obj
					pd.brand = brand
					pd.quantity = product['quantity']
					pd.purchase_price = product['price']
					pd.sale_price = product['sale_price']
					pd.description = product['description']
					pd.notes = product['notes']
					pd.created_by_user = my_user
					pd.save()
					'''
					print('**********purchase details*******')
					print(pd)
					print('**********skus*******')
					print(product['skus'])
					'''
					skus = json.loads(product['skus'])
					#imgs = json.loads(product['images'])
					#print('**********skus*******')

					skus = list(skus.values())[0]

					stores = json.loads(product['store'])
					stores = list(stores.values())[0]
					#imgs = list(imgs.values())
					'''
					print(len(skus))
					for itm in skus.values():
						print('**********sku*******')
						print(itm)
					'''

					#products_lst = list(products)

					for x in range(len(skus)):
						sku = skus[x].strip()
						ppd = PurchasesProductsDetails()

						if 'DISCARD-ME' not in sku.upper():
							ppd.purchase_detail = pd
							#ppd.sku = skus[x]
							if len(sku)<1:
								sku=None

							ppd.sku = sku
							input_name = \
								'product-'  + str(product_obj.id) + '-' + \
								'image_product' + str(x+1)
							image = request.FILES.get(input_name, None)
							#print('*********image*****')
							#print(image)
							#if image.name in product_images:
							ppd.image = image
							ppd.created_by_user = my_user
							if all_products_in_same_store:
								ppd.stored = True
								ppd.in_store = store
							else:
								store_val = stores[x]
								store = None
								if store_val and store_val is not None and len(store_val) > 0:
									try:
										store = Stores.objects.get(pk=store_val)
									except ObjectDoesNotExist:
										pass
								if store is not None:
									ppd.stored = True
									ppd.in_store = store
						else:
							ppd = PurchasesProductsDetails()
							ppd.purchase_detail = pd
							ppd.sku = None
							ppd.image = None
							ppd.created_by_user = my_user

						ppd.save()

			context['msg'] = _('The purchase has been successfully saved')
			context['level'] = 'success'
		except MultiValueDictKeyError:
			print('********ERROR1*******')
			return redirect('/')
		except ObjectDoesNotExist:
			print('********ERROR2*******')
			#print(e.args[0])
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
				'provider__exact': False,
				'identifier__iexact': False, 
				'purchased_at__iexact': False,
				'purchased_when__iexact': False, 
				'description__icontains': False,
				'notes__icontains': False
			}

			provider=request.POST.get('provider_obj', None)

			if provider and provider is not None and len(provider.strip())>0:
				try:
					provider=Providers.objects.get(pk=provider)
				except ObjectDoesNotExist:
					context['msg'] = _('The specified provider does not exists')
					context['level'] = 'error'
					if can_edit:
						frm = FrmPurchases(title=_('Edit purchase'), action='/purchases/do-edit', btn_label=_('Find'), icon_btn_submit='search')
					elif can_delete:
						frm = FrmPurchases(title=_('Delete purchase'), action='/purchases/do-delete', btn_label=_('Find'), icon_btn_submit='search')

					context['form'] = frm
					return render(request, 'purchases/find.html', context=context)

			if provider and provider is not None:
				search_by['provider__exact'] = provider

			pi = request.POST.get('identifier', None)
			if pi and pi is not None and len(pi.strip()) > 0:
				search_by['identifier__iexact'] = pi.strip()

			p_at = request.POST.get('purchased_at', None)
			if p_at and p_at is not None and len(p_at.strip()) > 0:
				search_by['purchased_at__iexact'] = p_at.strip()

			p_when = request.POST.get('purchased_when', None)
			if p_when and p_when is not None and len(p_when.strip()) > 0:
				search_by['purchased_when__iexact'] = p_when.strip()

			description = request.POST.get('description', None)
			if description and description is not None and len(description.strip()) > 0:
				search_by['description__icontains'] = description.strip()

			notes = request.POST.get('notes', None)
			if notes and notes is not None and len(notes.strip()) > 0:
				search_by['notes__icontains'] = notes.strip()

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

			# (1) First search in purchases table...
			purchases = Purchases.objects.filter(query)

			all_purchases_matching = []
			products = request.POST.get('products', None)
			products = json.loads(products)
			quantities = []
			prices = []
			descriptions = []
			notes = []
			brands = []
			all_skus = []
			products_a = []

			# (2) Prepare and extract values for searching in
			# purchasesdetails and 
			# purchasesproductsdetails tables...

			# (2.1) purchasesdetails
			for product in products:
				# print('*******product*******')
				# print(product)
				quantities.append(int(product['quantity']))
				prices.append(float(product['price']))
				descriptions.append(product['description'])
				notes.append(product['notes'])
				products_a.append(product['id'])

				# (2.2) purchasesproductsdetails
				skus = json.loads(product['skus'])
				skus = list(skus.values())[0]

				for x in range(len(skus)):
					sku = skus[x]
					if 'DISCARD-ME' not in sku.strip().upper():
						all_skus.append(sku)

			# print('********all_skus********')
			# print(all_skus)

			# print('********quantities********')
			# print(quantities)

			# print('********prices********')
			# print(prices)

			# print('********descriptions********')
			# print(descriptions)

			# print('********notes********')
			# print(notes)

			# (3) Prepare queries for purchasesdetails and 
			# purchasesproductsdetails tables...

			# (3.1) purchasesdetails
			pd_results = []

			search_by = {
				'quantity__in': False, 
				'purchase_price__in': False,
				'description__in': False,
				'notes__in': False,
				'brand__in': False,
				'product__in': False,
			}

			if quantities and quantities is not None and len(quantities) > 0:
				search_by['quantity__in'] = quantities

			if prices and prices is not None and len(prices) > 0:
				search_by['purchase_price__in'] = prices

			if descriptions and descriptions is not None and len(descriptions) > 0:
				search_by['description__in'] = descriptions

			if notes and notes is not None and len(notes) > 0:
				search_by['notes__in'] = notes

			if brands and brands is not None and len(brands) > 0:
				search_by['brand__in'] = brands

			if products_a and products_a is not None and len(products_a) > 0:
				search_by['product__in'] = products_a

			final_search_by = {}

			for criteria in search_by:
				if search_by[criteria]:
					final_search_by[criteria] = search_by[criteria]

			if len(final_search_by) > 0:
				pd_query = Q(created_by_user=my_user) & Q(dropped=False)
				pd_query &= reduce(operator.or_, (Q(**d) for d in [dict([i]) for i in final_search_by.items()]))

				# (3.1.1) Execute the query for purchasesdetails and 
				# purchasesproductsdetails tables...
				pd_results = PurchasesDetails.objects.filter(pd_query)

			# (3.2) purchasesproductsdetails
			ppd_results=[]

			search_by = {
				'sku__in': False
			}

			if all_skus and all_skus is not None and len(all_skus) > 0:
				search_by['sku__in'] = all_skus

			final_search_by = {}

			for criteria in search_by:
				if search_by[criteria]:
					final_search_by[criteria] = search_by[criteria]

			if len(final_search_by) > 0:
				ppd_query = Q(created_by_user=my_user) & Q(dropped=False)
				ppd_query &= reduce(operator.or_, (Q(**d) for d in [dict([i]) for i in final_search_by.items()]))

				# (3.2.1) Execute the query for purchasesdetails and 
				# purchasesproductsdetails tables...
				ppd_results = PurchasesProductsDetails.objects.filter(ppd_query)

			# (4) Now we must to verify that the purchases
			# are not the same
			all_purchases_id = []

			# (4.1) First add all the purchases found
			# on table purchases...
			for purchase in purchases:
				all_purchases_matching.append(purchase)
				all_purchases_id.append(purchase.id)

			# (4.2) Now the results for purchasesdetails 
			# table. But excluding those are ready included
			# in all_purchases_id
			for pd in pd_results:
				if pd.purchase.id not in all_purchases_id:
					all_purchases_matching.append(pd.purchase)
					all_purchases_id.append(pd.purchase.id)

			# (4.3) The results for purchasesproductsdetails 
			# table. But excluding those are ready included
			# in all_purchases_id
			for ppd in ppd_results:
				if ppd.purchase_detail.purchase.id not in all_purchases_id:
					all_purchases_matching.append(ppd.purchase_detail.purchase)
					all_purchases_id.append(ppd.purchase_detail.purchase.id)

			# And that's all (I think so! :') )

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
		all_purchases_matching = Purchases.objects.filter(query)

	if len(all_purchases_matching) > 0:
		context['purchases'] = all_purchases_matching

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmPurchases(title=_('Edit purchase'), action='/purchases/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmPurchases(title=_('Delete purchase'), action='/purchases/do-delete', btn_label=_('Find'), icon_btn_submit='search')

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
			purchase=request.POST.get('purchase', None)
			identifier=request.POST.get('identifier', None)
			provider=request.POST.get('provider_obj', None)

			try:
				provider=Providers.objects.get(pk=provider)
			except ObjectDoesNotExist:
				msg = _('The specified provider does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})

			today = datetime.now()
			purchased_at = request.POST.get('purchased_at', today)
			purchased_when = request.POST.get('purchased_when', today)
			description = request.POST.get('description', None)
			notes = request.POST.get('notes', None)

			purchase = Purchases.objects.get(pk=purchase)

			purchase.identifier = identifier
			purchase.provider = provider
			purchase.purchased_at = purchased_at
			purchased_when=purchased_when[6:]+'-'+purchased_when[3:5]+'-'+purchased_when[0:2]
			purchase.purchased_when = purchased_when
			purchase.description=description
			purchase.notes=notes

			purchase.save()
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

def show_purchased_products(request):
	if request.method == 'GET':
		purchase = request.GET.get('purchase', None)
		can_edit = request.GET.get('can_edit', False)
		can_delete = request.GET.get('can_delete', False)
		can_edit = can_edit.upper() == 'TRUE'
		can_delete = can_delete.upper() == 'TRUE'

		try:
			purchase=Purchases.objects.get(pk=purchase)
			context = {
				'purchase': purchase,
				'can_edit': can_edit,
				'can_delete': can_delete
			}
			#purchase.refresh_from_db()
			return render(request, 'purchases/purchased-products.html', context=context)
		except ObjectDoesNotExist:
			msg = _('The purchase does not exists')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})