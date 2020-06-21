from django.shortcuts import render, redirect

from django.contrib.auth.models import User

from django.db.models import Q

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from .forms import FrmProducts
from .models import Products
from users.models import Users

dummy=_('The product already exists')
dummy=_('Please enter a valid product')

def get_products_created_by_user(request):
	try:
		products = Products.objects.filter(created_by_user=request.user, dropped=False)

		return len(products)

	except ObjectDoesNotExist:
		msg = _('We can not retrieve the number of products created by this user')
		msg += '. ' + _('Retry, and if the problem persist get in touch with the system administrator and report') + ': '
		msg += 'error at products.views@get_products_created_by_user'
		context = {'level': 'error', 'msg': msg}

		return render(request, 'dashboard/index.html', context=context)

def add(request):
	context = {}
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	context['itm_menu'] = itm_menu
	url='products/add.html'

	if request.method == 'GET':
		frm = FrmProducts(title=_('Add product'), action='/products/do-add', btn_label=_('Save'), icon_btn_submit='save')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['app_version'] = app_version

		counter_products=get_products_created_by_user(request)
		limit=100

		if app_version==_('Free version'):
			if counter_products>=limit:
				url='products/add-free-version-limited.html'
		elif _('Basic version') in app_version:
			if counter_products>=limit:
				url='products/add-basic-version-limited.html'
		elif _('Pro version') in app_version:
			limit=1000
			if counter_products>=limit:
				url='products/add-pro-version-limited.html'
		elif _('Advanced version') in app_version:
			limit=10000
			if counter_products>=limit:
				url='products/add-advanced-version-limited.html'

	return render(request, url, context=context)

def find(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if get_products_created_by_user(request) < 1:
			return render(request, 'products/user-have-no-products-created.html', context={'itm_menu': itm_menu})

		frm = FrmProducts(title=_('Find product'), action='/products/do-find', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'products/find.html', context=context)

def do_add(request):
	frm = FrmProducts(title=_('Add product'), action='/products/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The product can not be saved')
	context['level'] = 'error'

	if request.method == 'POST':
		try:
			app_version = request.POST['app_version']
			itm_menu = request.POST.get('itm_menu', '')
			context['itm_menu'] = itm_menu
			'''
			if app_version == _('Free version'):
				if get_products_created_by_user(request) > 0:
					return render(request, 'products/add-free-version-limited.html', context={'itm_menu': itm_menu})
			'''
			context['app_version'] = app_version

			# Retrieve the user who is creating the product
			#user = User.objects.get(email=request.POST.get('user', None))
			user = User.objects.get(username=request.POST.get('user', None))
			my_user = Users.objects.get(pk=user.id)

			product_name = request.POST.get('name', None)

			# Check if the products does not exist
			# (same product = product_name)

			try:
				user = Users.objects.get(pk=request.user)
				#objs = Products.objects.filter(name=product_name, created_by_user=user)

				'''
				if len(objs) > 0:
					context['msg'] = _('The product already exist')
					context['level'] = 'error'
					return render(request, 'products/add.html', context=context)
				'''
				obj = Products.objects.get(name=product_name, created_by_user=user)

				if not obj.dropped:
					context['msg'] = _('The product already exist')
					context['level'] = 'error'
				else:
					obj.undrop()
					context['msg'] = _('The product has been successfully saved')
					context['level'] = 'success'

				return render(request, 'products/add.html', context=context)
			except ObjectDoesNotExist:
				pass

			obj = Products(name=product_name, \
				created_by_user=my_user)

			obj.save()
			context['msg'] = _('The product has been successfully saved')
			context['level'] = 'success'
		except MultiValueDictKeyError:
			return redirect('/')
		except ObjectDoesNotExist:
			return redirect('/')

	return render(request, 'products/add.html', context=context)

def __generic_find_view__(request, can_delete=False, can_edit=False, view_all=False):
	frm = FrmProducts(title=_('Find product'), action='/products/do-find', btn_label=_('Find'), icon_btn_submit='search')
	context = {}
	context['msg'] = _('We can not find any product matching with your query options')
	context['level'] = 'error'
	products = Products.objects.none()
	itm_menu = request.POST.get('itm_menu', request.GET.get('itm_menu', ''))
	context['itm_menu'] = itm_menu
	#context['url_view_all'] = '/products/list-all/'

	if request.method == 'POST':
		try:
			app_version = request.POST.get('app_version', _('Free version'))
			#itm_menu = request.POST.get('itm_menu', '')
			#context['itm_menu'] = itm_menu
			context['app_version'] = app_version

			search_by = {
				'name__icontains': False
			}

			product_name = request.POST.get('name', None)
			if product_name and product_name is not None and len(product_name.strip()) > 0:
				search_by['name__icontains'] = product_name.strip()

			# Retrieve the user logged in
			#user = User.objects.get(email=request.GET.get('user', ''))
			#my_user = Users.objects.get(pk=user.id)
			user = Users.objects.get(pk=request.user)
			query = Q(created_by_user=user) & Q(dropped=False)

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

			products = Products.objects.filter(query)
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
		user = User.objects.get(username=request.GET.get('user', ''))
		my_user = Users.objects.get(pk=user.id)
		query = Q(created_by_user=my_user) & Q(dropped=False)
		products = Products.objects.filter(query)

	if len(products) > 0:
		context['products'] = products

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmProducts(title=_('Edit product'), action='/products/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmProducts(title=_('Delete product'), action='/products/do-delete', btn_label=_('Find'), icon_btn_submit='search')

	context['form'] = frm

	return render(request, 'products/find.html', context=context)

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

		if get_products_created_by_user(request) < 1:
			return render(request, 'products/user-have-no-products-created.html', context={'itm_menu': itm_menu})

		frm = FrmProducts(title=_('Edit product'), action='/products/do-edit', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'products/find.html', context=context)

def do_edit(request):
	return __generic_find_view__(request, can_edit=True)

def delete(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if get_products_created_by_user(request) < 1:
			return render(request, 'products/user-have-no-products-created.html', context={'itm_menu': itm_menu})

		frm = FrmProducts(title=_('Delete product'), action='/products/do-delete', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'products/find.html', context=context)

def do_delete(request):
	return __generic_find_view__(request, can_delete=True)

def view_details(request):
	if request.method == 'GET':
		try:
			product = request.GET.get('obj', None)
			product = Products.objects.get(pk=product)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'product': product, 'can_edit': can_edit, 
				'can_delete': can_delete, 'itm_menu': itm_menu
			}

			return render(request, 'products/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def confirm_delete(request):
	if request.method == 'GET':
		try:
			product = request.GET.get('product', None)
			product = Products.objects.get(pk=product)

			context = {
				'product': product, 
				'can_delete': True
			}

			return render(request, 'products/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def delete_product(request):
	if request.method == 'POST':
		try:
			product = request.POST.get('product', None)
			product = Products.objects.get(pk=product)
			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			product.drop(reason=reason)
			'''
			from datetime import datetime
			full_time = datetime.now()

			product.dropped = True
			product.dropped_at = full_time
			product.dropped_when = full_time
			product.dropped_reason = reason
			product.save()
			'''

			frm = FrmProducts(title=_('Delete product'), action='/products/do-delete', btn_label=_('Find'), icon_btn_submit='search')
			#app_version = request.GET['app_version']
			#context['form'] = frm
			#context['itm_menu'] = itm_menu

			context = {
				'level': 'success',
				'msg': _('The product has been deleted successfully'),
				'itm_menu': itm_menu,
				'form': frm
			}

			return render(request, 'products/find.html', context=context)
			#return find(request)
			#return redirect('/products/find')
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def update(request):
	if request.method == 'POST':
		try:
			product = request.POST.get('product', None)
			product = Products.objects.get(pk=product)
			name = request.POST.get('productname', None)

			product.name = name
			product.save()
			msg = _('The product has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The product you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})