from django.shortcuts import render, redirect

from django.db.models import Q

from django.db import transaction

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from .forms import FrmSales
from .models import Sales, SalesDetails
from users.models import Users

from products.views import get_products_created_by_user
from products.models import Products

from brands.views import get_brands_created_by_user
from brands.models import Brands

from stores.views import get_stores_created_by_user
from stores.models import Stores

from customers.models import Customers

from purchases.models import \
PurchasesProductsDetails, \
PurchasesDetails

from datetime import datetime

import json

dummy = _('Please add at least one product to this sale')
dummy = _('Product was added to the current sale')
dummy = _('The product already was added to this sale')
dummy = _('Msg warning delete and prompt reason')
dummy = _('SKU or product name does not exists')
dummy = _('Please enter a valid customer')
dummy = _('The sale will be assigned to General Public')
dummy = _('Msg specified identifier already exists with dropped sale')
dummy = _('Wrong format for date')

def __get_sales_created_by_user__(request):
	sales = Sales.objects.filter(created_by_user=request.user, dropped=False)

	return sales

def add(request):
	context = {}
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	context['itm_menu'] = itm_menu

	if get_products_created_by_user(request) < 1:
		return render(request, 'sales/user-have-no-products-created.html', context={'itm_menu': itm_menu})

	if len(get_brands_created_by_user(request)) < 1:
		return render(request, 'sales/user-have-no-brands-created.html', context={'itm_menu': itm_menu})

	if request.method == 'GET':
		frm = FrmSales(user=request.user, title=_('Add sale'), action='/sales/do-add', btn_label=_('Save'), icon_btn_submit='save')
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
	return render(request, 'sales/add.html', context=context)

def find(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(__get_sales_created_by_user__(request)) < 1:
			return render(request, 'sales/user-have-no-sales-created.html', context={'itm_menu': itm_menu})

		frm = FrmSales(title=_('Find sale'), action='/sales/do-find', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'sales/find.html', context=context)

def do_add(request):
	frm = FrmSales(user=request.user, title=_('Add sale'), action='/sales/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The sale can not be saved')
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
			#my_user = Users.objects.get(pk=request.user)
			my_user = Users.objects.get(username=request.user)

			sale_identifier = request.POST.get('identifier', None)
			if sale_identifier is not None and len(sale_identifier.strip()) < 1:
				sale_identifier = None

			sold_at = request.POST.get('sold_at', None)
			sold_when = request.POST.get('sold_when', None)

			description = request.POST.get('description', None)
			notes = request.POST.get('notes', None)

			products = request.POST.get('products', None)
			products = json.loads(products)

			# Check if the sale does not exist
			# (same sale = created_by_user, identifier,
			# sold_at, sold_when see models for details)
			try:
				obj = Sales.objects.get(created_by_user=my_user, identifier__iexact=sale_identifier, sold_at__iexact=sold_at, sold_when__iexact=sold_when)

				if not obj.dropped:
					context['msg'] = _('One sale was done at the specified date time and identifier already exists')
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
					context['msg'] = _('The sale has been successfully saved')
					context['level'] = 'success'

				return render(request, 'sales/add.html', context=context)
			except ObjectDoesNotExist:
				try:
					# Verify also its owner identifier
					obj = Sales.objects.get(identifier__iexact=sale_identifier, created_by_user=my_user)
					if not obj.dropped:
						context['msg'] = _('One sale with the specified identifier already exists')
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
						context['msg'] = _('The sale has been successfully saved')
						context['level'] = 'success'

					return render(request, 'sales/add.html', context=context)
				except ObjectDoesNotExist:
					pass

			customer=request.POST.get('customer_obj', None)

			sale = Sales()
			sale.identifier = sale_identifier
			# print('**********identifier*********')
			# print(sale_identifier)
			sale.sold_at = sold_at
			sale.sold_when = sold_when[6:] + '-' + sold_when[3:5] + '-' + sold_when[0:2]
			sale.sold_date=sale.sold_when+' '+sale.sold_at
			sale.description = description
			sale.notes = notes
			sale.created_by_user = my_user

			if customer and customer is not None and len(customer.strip()) > 0:
				try:
					customer=Customers.objects.get(pk=customer)
				except ObjectDoesNotExist:
					context['msg'] = _('The customer does not exists')
					context['level'] = 'error'
					return render(request, 'sales/add.html', context=context)
			else:
				# Search for General Public...
				try:
					customer=Customers.objects.get(rfc='XXXXXXXXXXX'+str(my_user.id))					
				except ObjectDoesNotExist:
					msg=_('We did not found the customer named General Public')
					msg+='. '+_('Retry, and if the problem persist get in touch with the system administrator and report') + ': '
					msg+='Error 001 at do_add@users.views'
					context['msg'] = msg
					context['level'] = 'error'
					return render(request, 'sales/add.html', context=context)

			sale.customer=customer
			today=datetime.now()
			sale.saved_at = today
			sale.saved_when = today

			with transaction.atomic():
				sale.save()

				for product in products:
					ppd_obj = PurchasesProductsDetails.objects.get(pk=product)
					ppd_obj.sold=True
					sd = SalesDetails()
					sd.sale = sale
					sd.product = ppd_obj
					sd.created_by_user = my_user
					ppd_obj.save()
					sd.save()
					'''
					skus = json.loads(product['skus'])
					skus = list(skus.values())[0]

					stores = json.loads(product['store'])
					stores = list(stores.values())[0]

					for x in range(len(skus)):
						sku = skus[x].strip()
						ppd = PurchasesProductsDetails()

						if 'DISCARD-ME' not in sku.upper():
							ppd.purchase_detail = sd
							ppd.sku = sku
							input_name = \
								'product-'  + str(ppd_obj.id) + '-' + \
								'image_product' + str(x+1)
							image = request.FILES.get(input_name, None)
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
							ppd.purchase_detail = sd
							ppd.sku = None
							ppd.image = None
							ppd.created_by_user = my_user

						ppd.save()
					'''	

			context['msg'] = _('The sale has been successfully saved')
			context['level'] = 'success'
		except MultiValueDictKeyError:
			print('********ERROR1*******')
			return redirect('/')
		except ObjectDoesNotExist:
			print('********ERROR2*******')
			#print(e.args[0])
			return redirect('/')

	return render(request, 'sales/add.html', context=context)

def __generic_find_view__(request, can_delete=False, can_edit=False, view_all=False):
	frm = FrmSales(title=_('Find sale'), action='/sales/do-find', btn_label=_('Find'), icon_btn_submit='search')
	context = {}
	context['msg'] = _('We can not find any sale matching with your query options')
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
				'customer__exact': False,
				'identifier__iexact': False, 
				'sold_at__iexact': False,
				'sold_when__iexact': False, 
				'description__icontains': False,
				'notes__icontains': False
			}

			customer=request.POST.get('customer_obj', None)

			if customer and customer is not None and len(customer.strip())>0:
				try:
					customer=Customers.objects.get(pk=customer)
				except ObjectDoesNotExist:
					context['msg'] = _('The specified customer does not exists')
					context['level'] = 'error'
					if can_edit:
						frm = FrmSales(title=_('Edit sale'), action='/sales/do-edit', btn_label=_('Find'), icon_btn_submit='search')
					elif can_delete:
						frm = FrmSales(title=_('Delete sale'), action='/sales/do-delete', btn_label=_('Find'), icon_btn_submit='search')

					context['form'] = frm

					return render(request, 'sales/find.html', context=context)

			if customer and customer is not None:
				search_by['customer__exact'] = customer

			si = request.POST.get('identifier', None)
			if si and si is not None and len(si.strip()) > 0:
				search_by['identifier__iexact'] = si.strip()

			s_at = request.POST.get('sold_at', None)
			if s_at and s_at is not None and len(s_at.strip()) > 0:
				search_by['sold_at__iexact'] = s_at.strip()

			s_when = request.POST.get('sold_when', None)
			if s_when and s_when is not None and len(s_when.strip()) > 0:
				search_by['sold_when__iexact'] = s_when.strip()

			description = request.POST.get('description', None)
			if description and description is not None and len(description.strip()) > 0:
				search_by['description__icontains'] = description.strip()

			notes = request.POST.get('notes', None)
			if notes and notes is not None and len(notes.strip()) > 0:
				search_by['notes__icontains'] = notes.strip()

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

			# (1) First search in sales table...
			sales = Sales.objects.filter(query)

			all_sales_matching = []
			products = request.POST.get('products', None)
			products = json.loads(products)
			'''
			quantities = []
			prices = []
			descriptions = []
			notes = []
			brands = []
			all_skus = []
			'''
			products_a = []

			# (2) Prepare and extract values for searching in
			# salesdetails

			# (2.1) salesdetails
			for product in products:
				print('*******product*******')
				print(product)
				'''
				quantities.append(int(product['quantity']))
				prices.append(float(product['price']))
				descriptions.append(product['description'])
				notes.append(product['notes'])
				'''
				#products_a.append(product['id'])
				products_a.append(product)

				# (2.2) purchasesproductsdetails
				'''
				skus = json.loads(product['skus'])
				skus = list(skus.values())[0]

				for x in range(len(skus)):
					sku = skus[x]
					if 'DISCARD-ME' not in sku.strip().upper():
						all_skus.append(sku)
				'''
			'''
			print('********all_skus********')
			print(all_skus)

			print('********quantities********')
			print(quantities)

			print('********prices********')
			print(prices)

			print('********descriptions********')
			print(descriptions)

			print('********notes********')
			print(notes)
			'''

			# (3) Prepare queries for salesdetails

			# (3.1) salesdetails
			sd_results = []

			'''
			search_by = {
				'quantity__in': False, 
				'purchase_price__in': False,
				'description__in': False,
				'notes__in': False,
				'brand__in': False,
				'product__in': False,
			}
			'''
			search_by = {
				'product__in': False,
			}

			'''
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
			'''

			if products_a and products_a is not None and len(products_a) > 0:
				search_by['product__in'] = products_a

			final_search_by = {}

			for criteria in search_by:
				if search_by[criteria]:
					final_search_by[criteria] = search_by[criteria]

			if len(final_search_by) > 0:
				sd_query = Q(created_by_user=my_user) & Q(dropped=False)
				sd_query &= reduce(operator.or_, (Q(**d) for d in [dict([i]) for i in final_search_by.items()]))

				# (3.1.1) Execute the query for salesdetails
				sd_results = SalesDetails.objects.filter(sd_query)

			# (3.2) purchasesproductsdetails
			#ppd_results=[]
			'''
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

				# (3.2.1) Execute the query for salesdetails and 
				# purchasesproductsdetails tables...
				ppd_results = PurchasesProductsDetails.objects.filter(ppd_query)
			'''

			# (4) Now we must to verify that the sales
			# are not the same
			all_sales_id = []

			# (4.1) First add all the sales found
			# on table sales...
			for sale in sales:
				all_sales_matching.append(sale)
				all_sales_id.append(sale.id)

			# (4.2) Now the results for salesdetails 
			# table. But excluding those are ready included
			# in all_sales_id
			for sd in sd_results:
				if sd.sale.id not in all_sales_id:
					all_sales_matching.append(sd.sale)
					all_sales_id.append(sd.sale.id)

			# (4.3) The results for purchasesproductsdetails 
			# table. But excluding those are ready included
			# in all_sales_id
			'''
			for ppd in ppd_results:
				if ppd.purchase_detail.sale.id not in all_sales_id:
					all_sales_matching.append(ppd.purchase_detail.sale)
					all_sales_id.append(ppd.purchase_detail.sale.id)
			'''

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
		all_sales_matching = Sales.objects.filter(query)

	if len(all_sales_matching) > 0:
		context['sales'] = all_sales_matching

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmSales(title=_('Edit sale'), action='/sales/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmSales(title=_('Delete sale'), action='/sales/do-delete', btn_label=_('Find'), icon_btn_submit='search')

	context['form'] = frm

	return render(request, 'sales/find.html', context=context)

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

		if len(__get_sales_created_by_user__(request)) < 1:
			return render(request, 'sales/user-have-no-sales-created.html', context={'itm_menu': itm_menu})

		frm = FrmSales(title=_('Edit sale'), action='/sales/do-edit', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'sales/find.html', context=context)

def do_edit(request):
	return __generic_find_view__(request, can_edit=True)

def delete(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(__get_sales_created_by_user__(request)) < 1:
			return render(request, 'sales/user-have-no-sales-created.html', context={'itm_menu': itm_menu})

		frm = FrmSales(title=_('Delete sale'), action='/sales/do-delete', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'sales/find.html', context=context)

def do_delete(request):
	return __generic_find_view__(request, can_delete=True)

def view_details(request):
	if request.method == 'GET':
		try:
			sale = request.GET.get('obj', None)
			sale = Sales.objects.get(pk=sale)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'sale': sale, 'can_edit': can_edit, 
				'can_delete': can_delete, 
				'itm_menu': itm_menu
			}

			return render(request, 'sales/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def view_selected_product_details(request):
	if request.method == 'GET':
		try:
			ppd = request.GET.get('ppd', None)
			ppd = PurchasesProductsDetails.objects.get(pk=ppd)

			context = {
				'ppd': ppd
			}

			return render(request, 'sales/view-product-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def confirm_delete(request):
	if request.method == 'GET':
		try:
			sale = request.GET.get('sale', None)
			sale = Sales.objects.get(pk=sale)

			context = {
				'sale': sale, 
				'can_delete': True
			}

			return render(request, 'sales/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def delete_sale(request):
	if request.method == 'POST':
		try:
			sale = request.POST.get('sale', None)
			sale = Sales.objects.get(pk=sale)
			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			sale.drop(reason=reason)

			frm = FrmSales(title=_('Delete sale'), action='/products-stores/do-delete', btn_label=_('Find'), icon_btn_submit='search')
			#app_version = request.GET['app_version']
			#context['form'] = frm
			#context['itm_menu'] = itm_menu

			context = {
				'level': 'success',
				'msg': _('The sale has been deleted successfully'),
				'itm_menu': itm_menu,
				'form': frm
			}

			return render(request, 'sales/find.html', context=context)
			#return find(request)
			#return redirect('/products/find')
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def save_product_from_sale(request):
	if request.method == 'POST':
		product=request.POST.get('product', None)
		brand=request.POST.get('brand', None)
		sku=request.POST.get('sku', None)
		sp=request.POST.get('sale_price', None)
		store=request.POST.get('store', None)
		pk=request.POST.get('pk', None)
		image=request.FILES.get('image', None)

		print('*************image***********')
		print(image)

		try:
			sd=SalesDetails.objects.get(pk=pk)
			try:
				product=Products.objects.get(pk=product)
			except ObjectDoesNotExist:
				msg = _('The product does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})

			sd.product.purchase_detail.product=product

			try:
				brand=Brands.objects.get(pk=brand)
			except ObjectDoesNotExist:
				msg = _('The brand does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})

			sd.product.purchase_detail.brand=brand

			sd.product.sku=sku
			if sp is not None and len(sp.strip()) > 0:
				sp=sp.replace(',', '.')
			sd.product.purchase_detail.sale_price=sp

			try:
				store=Stores.objects.get(pk=store)
			except ObjectDoesNotExist:
				msg = _('The store does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})

			sd.product.in_store=store
			sd.product.stored=store is not None
			if image is None:
				if sd.product.image is None:
					sd.product.image=image
			else:
				sd.product.image=image

			with transaction.atomic():
				sd.save()
				sd.product.save()
				sd.product.purchase_detail.save()

				msg = _('The sold product details has been updated successfully')
				return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The sale you are trying to update does not exists')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def remove_product_from_sale(request):
	if request.method == 'POST':
		pk=request.POST.get('product', None)
		reason=request.POST.get('reason', None)
		if len(reason.strip()) < 1:
			reason=None

		try:
			sd=SalesDetails.objects.get(pk=pk)
			sd.drop(reason=reason)
			msg = _('The product has been removed successfully from the sale')
			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The product you are trying to remove from the sale does not exists')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def update(request):
	if request.method == 'POST':
		try:
			sale=request.POST.get('sale', None)
			identifier=request.POST.get('identifier', None)
			customer=request.POST.get('customer_obj', None)

			try:
				customer=Customers.objects.get(pk=customer)
			except ObjectDoesNotExist:
				msg = _('The specified customer does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})

			today = datetime.now()
			sold_at = request.POST.get('sold_at', today)
			sold_when = request.POST.get('sold_when', today)
			description = request.POST.get('description', None)
			notes = request.POST.get('notes', None)

			sale = Sales.objects.get(pk=sale)

			sale.identifier = identifier
			sale.customer = customer
			sale.sold_at = sold_at
			sold_when=sold_when[6:]+'-'+sold_when[3:5]+'-'+sold_when[0:2]
			sale.sold_when = sold_when
			sale.description=description
			sale.notes=notes

			sale.save()

			msg = _('The sale has been updated successfully')
			return JsonResponse({'status': 'success', 'msg': msg})

			# with transaction.atomic():
			# 	sale.save()
			# 	product.sold = True
			# 	product.save()
			# 	msg = _('The sale has been updated successfully')

			# 	return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The sale you are trying to update does not exists')
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
			return render(request, 'sales/product-details.html', context=context)

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})
'''

def product_details(request):
	if request.method == 'GET':
		product = request.GET.get('product', None)
		product_obj = request.GET.get('product_obj', None)
		'''
		brand = request.GET.get('brand', None)
		brand_obj = request.GET.get('brand_obj', None)
		purchase_price = request.GET.get('purchase_price', None)
		quantity = request.GET.get('quantity', None)
		description = request.GET.get('description', None)
		notes = request.GET.get('notes', None)
		'''
		row_number = request.GET.get('row_number', None)
		enter_and_edit = request.GET.get('enter_and_edit', False)
		'''
		skus = request.GET.get('skus', None)
		imgs = request.GET.get('images', None)
		'''

		context = {
			'product': product,
			'product_obj': product_obj,
			#'brand': brand,
			#'brand_obj': brand_obj,
			#'purchase_price': purchase_price,
			#'quantity': quantity,
			#'description': description,
			#'notes': notes,
			'row_number': row_number,
			'enter_and_edit': enter_and_edit,
			#'skus': skus, 'images': imgs
		}

		return render(request, 'sales/dlg-product-details.html', context=context)

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

'''
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

		return render(request, 'sales/products-details.html', context=context)

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})
'''

def show_sold_products(request):
	if request.method == 'GET':
		sale = request.GET.get('sale', None)
		can_edit = request.GET.get('can_edit', False)
		can_delete = request.GET.get('can_delete', False)
		can_edit = can_edit.upper() == 'TRUE'
		can_delete = can_delete.upper() == 'TRUE'

		try:
			#sale=Sales.objects.get(pk=sale)
			sales=SalesDetails.objects.filter(sale=sale,created_by_user=request.user,dropped=False)
			context = {
				'sales': sales,
				'can_edit': can_edit,
				'can_delete': can_delete
			}
			return render(request, 'sales/sold-products.html', context=context)
		except ObjectDoesNotExist:
			msg = _('The sale does not exists')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def view_product_details(request):
	if request.method == 'GET':
		context={}
		query = request.GET.get('info', None)
		sold = request.GET.get('sold', False)
		sold=sold.upper()=='TRUE'

		user=None
		products=[]
		found=False

		try:
			user=Users.objects.get(pk=request.user)
		except ObjectDoesNotExist:
			msg = _('Invalid request for the current user')
			return JsonResponse({'status': 'error', 'msg': msg})

		try:
			# First try with the SKU...
			product = PurchasesProductsDetails.objects.get(sku__iexact=query, dropped=False, created_by_user=user,stored=True,sold=sold)
			# print('*************product BY SKU**********')
			# print(product)
			products.append(product)
			context['search_by']='SKU'
			found=True
		except ObjectDoesNotExist:
			# Now try with its name...
			try:
				product = Products.objects.get(name__icontains=query,dropped=False,created_by_user=user)
				# print('*************product BY NAME**********')
				# print(product)

				pd=PurchasesDetails.objects.filter(product=product,dropped=False,created_by_user=user)
				# print('*************PurchasesDetails**********')
				# print(pd)

				ppd=PurchasesProductsDetails.objects.filter(purchase_detail__in=pd,created_by_user=user,dropped=False,stored=True,sold=sold).exclude(sku=None)
				# print('*************PurchasesProductsDetails**********')
				# print(ppd)

				found=True

				context['search_by']=_('Product name')
				products.extend(ppd)

				#for product in ppd:
					#products.append(product)
			except ObjectDoesNotExist as e:
				print(e.args[0])

		if found:
			context['products']=products
			context['query']=query
			return render(request, 'sales/dlg-info-product.html', context=context)
		else:
			context['status'] = 'error'
			context['msg'] = _('We can not find any product matching with your query options')
			return render(request, 'sales/dlg-info-product.html', context=context)
			#return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def show_dlg_help_add_sale(request):
	return render(request, 'sales/dlg-help-add-sale.html')