from django.shortcuts import render, redirect

from django.contrib.auth.models import User

from django.db.models import Q

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from .forms import FrmStores
from .models import Stores
from catalogues.models import City
from users.models import Users
from shops.models import Shops

from shops.views import get_shops_created_by_user

dummy=_('Please enter a valid store')

def get_stores_created_by_user(request):
	my_user = Users.objects.get(pk=request.user)
	stores = Stores.objects.filter(created_by_user=my_user, dropped=False)

	return stores

def add(request):
	context = {}
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	context['itm_menu'] = itm_menu
	url='stores/add.html'

	if len(get_shops_created_by_user(request)) < 1:
		return render(request, 'stores/user-have-no-shops-created.html', context={'itm_menu': itm_menu})

	if request.method == 'GET':
		frm = FrmStores(title=_('Add store'), action='/stores/do-add', btn_label=_('Save'), icon_btn_submit='save')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['app_version'] = app_version

		counter_stores=len(get_stores_created_by_user(request))
		limit=1

		if app_version==_('Free version'):
			if counter_stores>=limit:
				url='stores/add-free-version-limited.html'
		elif _('Basic version') in app_version:
			if counter_stores>=limit:
				url='stores/add-basic-version-limited.html'
		elif _('Pro version') in app_version:
			limit=2
			if counter_stores>=limit:
				url='stores/add-pro-version-limited.html'
		elif _('Advanced version') in app_version:
			limit=9
			if counter_stores>=limit:
				url='stores/add-advanced-version-limited.html'

	return render(request, url, context=context)

def find(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_stores_created_by_user(request)) < 1:
			return render(request, 'stores/user-have-no-stores-created.html', context={'itm_menu': itm_menu})

		frm = FrmStores(title=_('Find store'), action='/stores/do-find', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'stores/find.html', context=context)

def do_add(request):
	frm = FrmStores(title=_('Add store'), action='/stores/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The store can not be saved')
	context['level'] = 'error'

	if request.method == 'POST':
		try:
			app_version = request.POST['app_version']
			itm_menu = request.POST.get('itm_menu', '')
			context['itm_menu'] = itm_menu
			'''
			if app_version == _('Free version'):
				if get_stores_created_by_user(request) > 0:
					return render(request, 'stores/add-free-version-limited.html', context={'itm_menu': itm_menu})
			'''
			context['app_version'] = app_version
			city = request.POST.get('city_obj', None)
			admin = request.POST.get('user_obj', None)

			# Retrieve the city
			#city = City.objects.get(pk=request.POST['city'])
			#city = City.objects.get(display_name__iexact=request.POST['city'])
			city = City.objects.get(pk=city)

			# Retrieve the admin
			#admin = Users.objects.get(pk=request.POST['admin'])
			#admin = Users.objects.get(email=request.POST['email_store_admin'])
			admin = Users.objects.get(pk=admin)

			# Retrieve the shop
			shop_obj=request.POST.get('shop_obj', None)
			shop = Shops.objects.get(pk=shop_obj)

			# Retrieve the user who is creating the store
			#user = User.objects.get(email=request.POST['user'])
			#user = User.objects.get(email=request.POST.get('user', ''))
			user = User.objects.get(username=request.POST.get('user', ''))
			my_user = Users.objects.get(pk=user.id)

			store_name = request.POST.get('name', None)
			address_line1 = request.POST.get('address_line1', None)
			# Check if the stores does not exist
			# (same store = store_name, shop, city & address_line1)
			# see stores on model for more details
			try:
				objs = Stores.objects.get(name=store_name, shop=shop, city=city, address_line1=address_line1)

				context['msg'] = _('The store already exist')
				context['level'] = 'error'

				return render(request, 'stores/add.html', context=context)
				'''
				objs = Stores.objects.filter(name=store_name, city=city, address_line1=address_line1)
				
				if len(objs) > 0:
					context['msg'] = _('The store already exist')
					context['level'] = 'error'
					return render(request, 'stores/add.html', context=context)
				'''
			except ObjectDoesNotExist:
				pass

			obj = Stores(name=store_name, \
				city=city, \
				admin=admin, \
				shop=shop, \
				created_by_user=my_user, \
				address_line1=address_line1, \
				address_line2=request.POST['address_line2'], \
				cell_phone=request.POST['cell_phone'], \
				home_phone=request.POST['home_phone'], \
				other_phone=request.POST['other_phone'])

			obj.save()
			context['msg'] = _('The store has been successfully saved')
			context['level'] = 'success'
		except MultiValueDictKeyError:
			#print('******ERROR1*****')
			return redirect('/')
		except ObjectDoesNotExist:
			#print('******ERROR2*****')
			return redirect('/')

	return render(request, 'stores/add.html', context=context)

def __generic_find_view__(request, can_delete=False, can_edit=False, view_all=False):
	frm = FrmStores(title=_('Find store'), action='/stores/do-find', btn_label=_('Find'), icon_btn_submit='search')
	context = {}
	context['msg'] = _('We can not find any store matching with your query options')
	context['level'] = 'error'
	stores = Stores.objects.none()
	itm_menu = request.POST.get('itm_menu', request.GET.get('itm_menu', ''))
	context['itm_menu'] = itm_menu
	#context['url_view_all'] = '/stores/list-all/'

	if request.method == 'POST':
		try:
			app_version = request.POST.get('app_version', _('Free version'))
			#itm_menu = request.POST.get('itm_menu', '')
			#context['itm_menu'] = itm_menu
			context['app_version'] = app_version

			search_by = {
				'name__icontains': False, 
				'shop': False,
				'city': False, 'admin': False,
				'address_line1__icontains': False, 
				'address_line2__icontains': False,
				'cell_phone': False, 'home_phone': False, 
				'other_phone': False
			}
			
			store_name = request.POST.get('name', None)
			if store_name and store_name is not None and len(store_name.strip()) > 0:
				search_by['name__icontains'] = store_name.strip()

			shop = request.POST.get('shop_obj', None)
			if shop and shop is not None and len(shop.strip()) > 0:
				# Retrieve the city
				search_by['shop'] = Shops.objects.get(pk=shop)

			city = request.POST.get('city_obj', None)
			if city and city is not None and len(city.strip()) > 0:
				# Retrieve the city
				search_by['city'] = City.objects.get(pk=city)

			admin = request.POST.get('user_obj', None)
			if admin and admin is not None and len(admin.strip()) > 0:
				# Retrieve the admin
				search_by['admin'] = Users.objects.get(pk=admin)

			# Retrieve the user logged in
			#user = User.objects.get(email=request.POST.get('user', ''))
			user = User.objects.get(username=request.POST.get('user', ''))
			my_user = Users.objects.get(pk=user.id)

			address_line1 = request.POST.get('address_line1', None)
			if address_line1 and address_line1 is not None and len(address_line1.strip()) > 0:
				search_by['address_line1__icontains'] = address_line1.strip()

			address_line2 = request.POST.get('address_line2', None)
			if address_line2 and address_line2 is not None and len(address_line2.strip()) > 0:
				search_by['address_line2__icontains'] = address_line2.strip()

			cell_phone = request.POST.get('cell_phone', None)
			if cell_phone and cell_phone is not None and len(cell_phone.strip()) > 0:
				search_by['cell_phone'] = cell_phone.strip()

			home_phone = request.POST.get('home_phone', None)
			if home_phone and home_phone is not None and len(home_phone.strip()) > 0:
				search_by['home_phone'] = home_phone.strip()

			other_phone = request.POST.get('other_phone', None)
			if other_phone and other_phone is not None and len(other_phone.strip()) > 0:
				search_by['other_phone'] = other_phone.strip()

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

			stores = Stores.objects.filter(query)
			#context['msg'] = _('We found {0} result(s) matching your query').format(len(stores))
			#context['level'] = "success"
		except MultiValueDictKeyError:
			return redirect('/')
		except ObjectDoesNotExist:
			return redirect('/')
	elif view_all:
		app_version = request.GET.get('app_version', _('Free version'))
		itm_menu = request.GET.get('itm_menu', '')
		context['itm_menu'] = itm_menu
		context['app_version'] = app_version

		# Retrieve the user logged in
		#user = User.objects.get(email=request.GET.get('user', ''))
		user = User.objects.get(username=request.GET.get('user', ''))
		my_user = Users.objects.get(pk=user.id)
		query = Q(created_by_user=my_user) & Q(dropped=False)
		stores = Stores.objects.filter(query)

	if len(stores) > 0:
		context['stores'] = stores

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmStores(title=_('Edit store'), action='/stores/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmStores(title=_('Delete store'), action='/stores/do-delete', btn_label=_('Find'), icon_btn_submit='search')

	context['form'] = frm

	return render(request, 'stores/find.html', context=context)

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

		if len(get_stores_created_by_user(request)) < 1:
			return render(request, 'stores/user-have-no-stores-created.html', context={'itm_menu': itm_menu})

		frm = FrmStores(title=_('Edit store'), action='/stores/do-edit', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'stores/find.html', context=context)

def do_edit(request):
	return __generic_find_view__(request, can_edit=True)

def delete(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_stores_created_by_user(request)) < 1:
			return render(request, 'stores/user-have-no-stores-created.html', context={'itm_menu': itm_menu})

		frm = FrmStores(title=_('Delete store'), action='/stores/do-delete', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'stores/find.html', context=context)

def do_delete(request):
	return __generic_find_view__(request, can_delete=True)

def view_details(request):
	if request.method == 'GET':
		try:
			store = request.GET.get('obj', None)
			store = Stores.objects.get(pk=store)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'store': store, 'can_edit': can_edit, 
				'can_delete': can_delete, 'itm_menu': itm_menu
			}

			return render(request, 'stores/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def confirm_delete(request):
	if request.method == 'GET':
		try:
			store = request.GET.get('store', None)
			store = Stores.objects.get(pk=store)

			context = {
				'store': store, 
				'can_delete': True
			}

			return render(request, 'stores/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def delete_store(request):
	if request.method == 'POST':
		try:
			store = request.POST.get('store', None)
			store = Stores.objects.get(pk=store)
			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			from datetime import datetime
			full_time = datetime.now()

			store.dropped = True
			store.dropped_at = full_time
			store.dropped_when = full_time
			store.dropped_reason = reason
			store.save()

			frm = FrmStores(title=_('Delete store'), action='/stores/do-delete', btn_label=_('Find'), icon_btn_submit='search')
			#app_version = request.GET['app_version']
			#context['form'] = frm
			#context['itm_menu'] = itm_menu

			context = {
				'level': 'success',
				'msg': _('The store has been deleted successfully'),
				'itm_menu': itm_menu,
				'form': frm
			}

			return render(request, 'stores/find.html', context=context)
			#return find(request)
			#return redirect('/stores/find')
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def update(request):
	if request.method == 'POST':
		try:
			store = request.POST.get('store', None)
			store = Stores.objects.get(pk=store)
			name = request.POST.get('storename', None)
			address_line1 = request.POST.get('addressline1', None)
			address_line2 = request.POST.get('addressline2', None)
			city = request.POST.get('city_obj', None)
			admin = request.POST.get('useradmin_obj', None)
			cell_phone = request.POST.get('cellphone', None)
			home_phone = request.POST.get('homephone', None)
			other_phone = request.POST.get('otherphone', None)

			store.name = name
			store.address_line1 = address_line1
			store.address_line2 = address_line2
			store.city = City.objects.get(pk=city)
			store.admin = Users.objects.get(pk=admin)
			store.cell_phone = cell_phone
			store.home_phone = home_phone
			store.other_phone = other_phone

			store.save()
			msg = _('The store has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The store you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})