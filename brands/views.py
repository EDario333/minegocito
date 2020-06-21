from django.shortcuts import render, redirect

from django.contrib.auth.models import User

from django.db.models import Q

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from .forms import FrmBrands
from .models import Brands
from users.models import Users

dummy=_('Please enter a valid brand')
dummy=_('The brand already exists')

def get_brands_created_by_user(request):
	'''
	try:
		if request.method == 'GET':
			user = request.GET.get('user', None)
		else:
			user = request.POST.get('user', None)
	except MultiValueDictKeyError:
		return redirect('/')
	'''
	'''
	try:
		#user = User.objects.get(email=user)
		#my_user = Users.objects.get(pk=user.id)
		brands = Brands.objects.filter(created_by_user=request.user, dropped=False)

		return len(brands)

	except ObjectDoesNotExist:
		msg = _('We can not retrieve the number of products in stores created by this user')
		msg += '. ' + _('Retry, and if the problem persist get in touch with the system administrator and report') + ': '
		msg += 'error at products_stores.views@__get_products_in_stores_created_by_user__'
		context = {'level': 'error', 'msg': msg}
	'''
	brands = Brands.objects.filter(created_by_user=request.user, dropped=False)
	return brands

def add(request):
	context = {}
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	context['itm_menu'] = itm_menu
	url='brands/add.html'

	if request.method == 'GET':
		frm = FrmBrands(title=_('Add Brand'), action='/brands/do-add', btn_label=_('Save'), icon_btn_submit='save')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['app_version'] = app_version

		counter_brands=len(get_brands_created_by_user(request))
		limit=10

		if app_version==_('Free version'):
			if counter_brands>=limit:
				url='brands/add-free-version-limited.html'
		elif _('Basic version') in app_version:
			if counter_brands>=limit:
				url='brands/add-basic-version-limited.html'
		elif _('Pro version') in app_version:
			limit=100
			if counter_brands>=limit:
				url='brands/add-pro-version-limited.html'
		elif _('Advanced version') in app_version:
			limit=1000
			if counter_brands>=limit:
				url='brands/add-advanced-version-limited.html'

	return render(request, url, context=context)

def find(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_brands_created_by_user(request)) < 1:
			return render(request, 'brands/user-have-no-brands-created.html', context={'itm_menu': itm_menu})

		frm = FrmBrands(title=_('Find Brand'), action='/brands/do-find', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'brands/find.html', context=context)

def do_add(request):
	print('********ENTRO***********')
	frm = FrmBrands(title=_('Add Brand'), action='/brands/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The brand can not be saved')
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

			# Retrieve the user who is creating the brand
			#my_user = Users.objects.get(pk=request.user)
			my_user = Users.objects.get(username=request.user)
			#user = User.objects.get(email=request.POST.get('user', None))
			#my_user = Users.objects.get(pk=user.id)

			brand = request.POST.get('name', None)

			# Check if the products does not exist
			# (same product = product_name)

			try:
				#objs = Products.objects.filter(name=product_name, created_by_user=user)

				'''
				if len(objs) > 0:
					context['msg'] = _('The product already exist')
					context['level'] = 'error'
					return render(request, 'products/add.html', context=context)
				'''
				obj = Brands.objects.get(name__iexact=brand, created_by_user=my_user)

				if not obj.dropped:
					context['msg'] = _('The brand already exist')
					context['level'] = 'error'
				else:
					obj.undrop()
					context['msg'] = _('The brand has been successfully saved')
					context['level'] = 'success'

				return render(request, 'brands/add.html', context=context)
			except ObjectDoesNotExist:
				pass

			obj = Brands(name=brand, \
				created_by_user=my_user)

			obj.save()
			'''
			categories = request.POST.get('categories', None)
			categories = categories.split(',')

			from django.db import transaction
			with transaction.atomic():
				obj.save()

				for category in categories:
					obj.categories.add(category.strip())
			'''

			context['msg'] = _('The brand has been successfully saved')
			context['level'] = 'success'
		except MultiValueDictKeyError:
			return redirect('/')
		except ObjectDoesNotExist:
			return redirect('/')

	return render(request, 'brands/add.html', context=context)

def __generic_find_view__(request, can_delete=False, can_edit=False, view_all=False):
	frm = FrmBrands(title=_('Find Brand'), action='/brands/do-find', btn_label=_('Find'), icon_btn_submit='search')
	context = {}
	context['msg'] = _('We can not find any brand matching with your query options')
	context['level'] = 'error'
	brands = Brands.objects.none()
	itm_menu = request.POST.get('itm_menu', request.GET.get('itm_menu', ''))
	context['itm_menu'] = itm_menu
	#context['url_view_all'] = '/products/list-all/'

	# Retrieve the user logged in
	user = Users.objects.get(pk=request.user)

	if request.method == 'POST':
		try:
			app_version = request.POST.get('app_version', _('Free version'))
			#itm_menu = request.POST.get('itm_menu', '')
			#context['itm_menu'] = itm_menu
			context['app_version'] = app_version

			search_by = {
				'name__icontains': False
			}

			brand = request.POST.get('name', None)
			if brand and brand is not None and len(brand.strip()) > 0:
				search_by['name__icontains'] = brand.strip()

			# Retrieve the user logged in
			#user = User.objects.get(email=request.GET.get('user', ''))
			#my_user = Users.objects.get(pk=user.id)
			#user = Users.objects.get(pk=request.user)
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

			brands = Brands.objects.filter(query)
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
		query = Q(created_by_user=user) & Q(dropped=False)
		brands = Brands.objects.filter(query)

	if len(brands) > 0:
		context['brands'] = brands

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmBrands(title=_('Edit Brand'), action='/brands/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmBrands(title=_('Delete Brand'), action='/brands/do-delete', btn_label=_('Find'), icon_btn_submit='search')

	context['form'] = frm

	return render(request, 'brands/find.html', context=context)

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

		if len(get_brands_created_by_user(request)) < 1:
			return render(request, 'brands/user-have-no-brands-created.html', context={'itm_menu': itm_menu})

		frm = FrmBrands(title=_('Edit Brand'), action='/brands/do-edit', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'brands/find.html', context=context)

def do_edit(request):
	return __generic_find_view__(request, can_edit=True)

def delete(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_brands_created_by_user(request)) < 1:
			return render(request, 'brands/user-have-no-brands-created.html', context={'itm_menu': itm_menu})

		frm = FrmBrands(title=_('Delete Brand'), action='/brands/do-delete', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'brands/find.html', context=context)

def do_delete(request):
	return __generic_find_view__(request, can_delete=True)

def view_details(request):
	if request.method == 'GET':
		try:
			brand = request.GET.get('obj', None)
			brand = Brands.objects.get(pk=brand)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'brand': brand, 'can_edit': can_edit, 
				'can_delete': can_delete, 'itm_menu': itm_menu
			}

			return render(request, 'brands/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def confirm_delete(request):
	if request.method == 'GET':
		try:
			brand = request.GET.get('brand', None)
			brand = Brands.objects.get(pk=brand)

			context = {
				'brand': brand, 
				'can_delete': True
			}

			return render(request, 'brands/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def delete_brand(request):
	if request.method == 'POST':
		try:
			brand = request.POST.get('brand', None)
			brand = Brands.objects.get(pk=brand)
			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			brand.drop(reason=reason)

			frm = FrmBrands(title=_('Delete Brand'), action='/brands/do-delete', btn_label=_('Find'), icon_btn_submit='search')
			#app_version = request.GET['app_version']
			#context['form'] = frm
			#context['itm_menu'] = itm_menu

			context = {
				'level': 'success',
				'msg': _('The brand has been deleted successfully'),
				'itm_menu': itm_menu,
				'form': frm
			}

			return render(request, 'brands/find.html', context=context)
			#return find(request)
			#return redirect('/products/find')
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def update(request):
	if request.method == 'POST':
		try:
			brand = request.POST.get('brand', None)
			brand = Brands.objects.get(pk=brand)
			name = request.POST.get('brandname', None)

			brand.name = name
			brand.save()
			msg = _('The brand has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The brand you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})