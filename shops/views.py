from django.shortcuts import render, redirect

from django.db import transaction

from django.contrib.auth.models import User, ContentType

from django.db.models import Q

from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from .forms import FrmShops
from .models import Shops
from catalogues.models import City
from users.models import Users

from brands.models import Brands
from purchases.models import PurchasesDetails, PurchasesProductsDetails
from products.models import Products
from shops.models import Shops

from taggit.models import Tag, TaggedItem

from enum import Enum, unique

dummy = _('Show')
dummy = _('entries')
dummy = _('Showing')
dummy = _('to')
dummy = _('of')
dummy = _('Previous')
dummy = _('Next')
dummy = _('Copy')
dummy = _('Print')
dummy = _('Please enter at least one search criteria')
dummy = _('Please enter a valid user')
dummy = _('Please enter a valid city')
dummy = _('Make a click on the field to edit its value')
dummy = _('Please enter a valid shop')

@unique
class Ordering(Enum):
	NONE=0
	ASCENDING=1
	DESCENDING=2

current_shops_ids=[]

def get_shops_created_by_user(request):
	my_user = Users.objects.get(pk=request.user)
	shops = Shops.objects.filter(created_by_user=my_user, dropped=False)

	return shops

def add(request):
	context = {}
	url='shops/add.html'

	if request.method == 'GET':
		frm = FrmShops(title=_('Add shop'), action='/shops/do-add', btn_label=_('Save'), icon_btn_submit='save')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['app_version'] = app_version
		itm_menu = request.GET.get('itm_menu', '')
		context['itm_menu'] = itm_menu

		counter_shops=len(get_shops_created_by_user(request))
		limit=1

		if app_version==_('Free version'):
			if counter_shops>=limit:
				url='shops/add-free-version-limited.html'
		elif _('Basic version') in app_version:
			if counter_shops>=limit:
				url='shops/add-basic-version-limited.html'
		elif _('Pro version') in app_version:
			if counter_shops>=limit:
				url='shops/add-pro-version-limited.html'
		elif _('Advanced version') in app_version:
			limit=3
			if counter_shops>=limit:
				url='shops/add-advanced-version-limited.html'

	return render(request, url, context=context)

def find(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_shops_created_by_user(request)) < 1:
			return render(request, 'shops/user-have-no-shops-created.html', context={'itm_menu': itm_menu})

		frm = FrmShops(title=_('Find shop'), action='/shops/do-find', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'shops/find.html', context=context)

def do_add(request):
	frm = FrmShops(title=_('Add shop'), action='/shops/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The shop can not be saved')
	context['level'] = 'error'

	if request.method == 'POST':
		try:
			app_version = request.POST['app_version']
			itm_menu = request.POST.get('itm_menu', '')
			context['itm_menu'] = itm_menu
			'''
			if app_version == _('Free version'):
				if get_shops_created_by_user(request) > 0:
					return render(request, 'shops/add-free-version-limited.html', context={'itm_menu': itm_menu})
			'''
			context['app_version'] = app_version
			city = request.POST['city']
			admin = request.POST['admin']

			# Retrieve the city
			#city = City.objects.get(pk=request.POST['city'])
			#city = City.objects.get(display_name__iexact=request.POST['city'])
			city = City.objects.get(pk=request.POST['city_obj'])

			# Retrieve the admin
			#admin = Users.objects.get(pk=request.POST['admin'])
			#admin = Users.objects.get(email=request.POST['email_shop_admin'])
			admin = Users.objects.get(pk=request.POST['user_obj'])

			# Retrieve the user who is creating the shop
			#user = User.objects.get(email=request.POST['user'])
			user = User.objects.get(username=request.POST.get('user', ''))
			my_user = Users.objects.get(pk=user.id)

			shop_name = request.POST.get('name', None)
			address_line1 = request.POST.get('address_line1', None)
			# Check if the shops does not exist
			# (same shop = shop_name, city & address_line1)
			# see Shops on model for more details
			try:
				#obj = Shops.objects.filter(name=shop_name, city=city, address_line1=address_line1)
				obj = Shops.objects.get(name=shop_name, city=city, address_line1=address_line1)
				context['msg'] = _('The shop already exist')
				context['level'] = 'error'

				return render(request, 'shops/add.html', context=context)
			except ObjectDoesNotExist:
				pass

			obj = Shops(name=shop_name, \
				city=city, \
				admin=admin, \
				created_by_user=my_user, \
				address_line1=address_line1, \
				address_line2=request.POST['address_line2'], \
				cell_phone=request.POST['cell_phone'], \
				home_phone=request.POST['home_phone'], \
				other_phone=request.POST['other_phone'])

			categories = request.POST.get('categories', None)
			categories = categories.split(',')

			with transaction.atomic():
				obj.save()

				for category in categories:
					if len(category.strip()) > 0:
						obj.categories.add(category.strip())

				context['msg'] = _('The shop has been successfully saved')
				context['level'] = 'success'

		except MultiValueDictKeyError:
			#print('******ERROR1*****')
			return redirect('/')
		except ObjectDoesNotExist:
			#print('******ERROR2*****')
			return redirect('/')

	return render(request, 'shops/add.html', context=context)

def __generic_find_view__(request, can_delete=False, can_edit=False, view_all=False):
	frm = FrmShops(title=_('Find shop'), action='/shops/do-find', btn_label=_('Find'), icon_btn_submit='search')
	context = {}
	context['msg'] = _('We can not find any shop matching with your query options')
	context['level'] = 'error'
	shops = Shops.objects.none()
	itm_menu = request.POST.get('itm_menu', request.GET.get('itm_menu', ''))
	context['itm_menu'] = itm_menu
	#context['url_view_all'] = '/shops/list-all/'

	if request.method == 'POST':
		try:
			app_version = request.POST.get('app_version', _('Free version'))
			#itm_menu = request.POST.get('itm_menu', '')
			#context['itm_menu'] = itm_menu
			context['app_version'] = app_version

			search_by = {
				'name__icontains': False, 'city': False, 'admin': False,
				'address_line1__icontains': False, 
				'address_line2__icontains': False,
				'cell_phone': False, 'home_phone': False, 
				'other_phone': False, 
				'categories__name__in': False
			}
			
			shop_name = request.POST.get('name', None)
			if shop_name and shop_name is not None and len(shop_name.strip()) > 0:
				search_by['name__icontains'] = shop_name.strip()
			
			city = request.POST.get('city_obj', None)
			if city and city is not None and len(city.strip()) > 0:
				# Retrieve the city
				search_by['city'] = City.objects.get(pk=city)

			admin = request.POST.get('user_obj', None)
			if admin and admin is not None and len(admin.strip()) > 0:
				# Retrieve the admin
				search_by['admin'] = Users.objects.get(pk=admin)

			# Retrieve the user logged in
			user = User.objects.get(email=request.POST.get('user', ''))
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

			categories = request.POST.get('categories', None)
			if categories and categories is not None and len(categories.strip()) > 0:
				categories = categories.split(',')
				search_by['categories__name__in'] = categories

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

			#print('********query******')
			#print(query)
			shops = Shops.objects.filter(query)
			#context['msg'] = _('We found {0} result(s) matching your query').format(len(shops))
			#context['level'] = "success"
		except MultiValueDictKeyError:
			print('******ERROR1*****')
			return redirect('/')
		except ObjectDoesNotExist:
			print('******ERROR2*****')
			return redirect('/')
	elif view_all:
		app_version = request.GET.get('app_version', _('Free version'))
		itm_menu = request.GET.get('itm_menu', '')
		context['itm_menu'] = itm_menu
		context['app_version'] = app_version

		# Retrieve the user logged in
		user = User.objects.get(email=request.GET.get('user', ''))
		my_user = Users.objects.get(pk=user.id)
		query = Q(created_by_user=my_user) & Q(dropped=False)
		shops = Shops.objects.filter(query)

	if len(shops) > 0:
		context['shops'] = shops

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmShops(title=_('Edit shop'), action='/shops/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmShops(title=_('Delete shop'), action='/shops/do-delete', btn_label=_('Find'), icon_btn_submit='search')

	context['form'] = frm

	return render(request, 'shops/find.html', context=context)

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

		if len(get_shops_created_by_user(request)) < 1:
			return render(request, 'shops/user-have-no-shops-created.html', context={'itm_menu': itm_menu})

		frm = FrmShops(title=_('Edit shop'), action='/shops/do-edit', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'shops/find.html', context=context)

def do_edit(request):
	return __generic_find_view__(request, can_edit=True)

def delete(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_shops_created_by_user(request)) < 1:
			return render(request, 'shops/user-have-no-shops-created.html', context={'itm_menu': itm_menu})

		frm = FrmShops(title=_('Delete shop'), action='/shops/do-delete', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'shops/find.html', context=context)

def do_delete(request):
	return __generic_find_view__(request, can_delete=True)

def view_details(request):
	if request.method == 'GET':
		try:
			shop = request.GET.get('shop', None)
			shop = Shops.objects.get(pk=shop)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'shop': shop, 'can_edit': can_edit, 
				'can_delete': can_delete, 'itm_menu': itm_menu
			}

			return render(request, 'shops/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def confirm_delete(request):
	if request.method == 'GET':
		try:
			shop = request.GET.get('shop', None)
			shop = Shops.objects.get(pk=shop)

			context = {
				'shop': shop, 
				'can_delete': True
			}

			return render(request, 'shops/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def delete_shop(request):
	if request.method == 'POST':
		try:
			shop = request.POST.get('shop', None)
			shop = Shops.objects.get(pk=shop)
			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			from datetime import datetime
			full_time = datetime.now()

			shop.dropped = True
			shop.dropped_at = full_time
			shop.dropped_when = full_time
			shop.dropped_reason = reason
			shop.save()

			frm = FrmShops(title=_('Delete shop'), action='/shops/do-delete', btn_label=_('Find'), icon_btn_submit='search')
			#app_version = request.GET['app_version']
			#context['form'] = frm
			#context['itm_menu'] = itm_menu

			context = {
				'level': 'success',
				'msg': _('The shop has been deleted successfully'),
				'itm_menu': itm_menu,
				'form': frm
			}

			return render(request, 'shops/find.html', context=context)
			#return find(request)
			#return redirect('/shops/find')
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def update(request):
	if request.method == 'POST':
		try:
			shop = request.POST.get('shop', None)
			shop = Shops.objects.get(pk=shop)
			name = request.POST.get('shopname', None)
			address_line1 = request.POST.get('addressline1', None)
			address_line2 = request.POST.get('addressline2', None)
			city = request.POST.get('city_obj', None)
			admin = request.POST.get('useradmin_obj', None)
			cell_phone = request.POST.get('cellphone', None)
			home_phone = request.POST.get('homephone', None)
			other_phone = request.POST.get('otherphone', None)

			shop.name = name
			shop.address_line1 = address_line1
			shop.address_line2 = address_line2
			shop.city = City.objects.get(pk=city)
			shop.admin = Users.objects.get(pk=admin)
			shop.cell_phone = cell_phone
			shop.home_phone = home_phone
			shop.other_phone = other_phone

			shop.save()
			msg = _('The shop has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The shop you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def __retrieve_shops_home_filters__(categories=None, brands=None, products=None, match_all_filters=False, city=None, news_first=False, ordering=Ordering.NONE):
	categories_array = []
	tags=[]
	shops=[]
	shops_ids=[]
	global current_shops_ids

	ct=ContentType.objects.get(app_label__icontains='icon',model='shops')
	tis=TaggedItem.objects.filter(content_type=ct)

	for ti in tis:
		if ti.tag.id not in tags or (categories is not None and ti.tag.id in categories):
			counter=len(TaggedItem.objects.filter(content_type=ct,tag=ti.tag))
			categories_array.append({'category': ti.tag, 'counter': counter})
			tags.append(ti.tag.id)
			# ti=TaggedItem.objects.filter()

	if ordering is not Ordering.NONE:
		if ordering is Ordering.ASCENDING:
			shops_array=Shops.objects.filter(pk__in=current_shops_ids).order_by('name', 'created_when', 'created_at')
		else:
			shops_array=Shops.objects.filter(pk__in=current_shops_ids).order_by('-name', 'created_when', 'created_at')

		return ct, categories_array, None, None, shops_array
	elif categories is not None and len(categories)>0 and categories[0] is not None:
		categories=[int(i) for i in categories]
		if news_first:
			shops=Shops.objects.filter(dropped=False).order_by('created_when', 'created_at', 'name')
		else:
			shops=Shops.objects.filter(dropped=False).order_by('name')

		shops_array=[]
		shops_ids=[]
		current_shops_ids.clear()

		for shop in shops:
			tis=TaggedItem.objects.filter(content_type=ct,object_id=shop.id)
			for ti in tis:
				if ti.tag_id in categories and shop.id not in shops_ids:
					shops_array.append(shop)
					current_shops_ids.append(shop.id)

		return ct, categories_array, None, None, shops_array
	elif not match_all_filters:
		if brands is not None:
			brands=[int(i) for i in brands]
			brands=Brands.objects.filter(dropped=False, pk__in=brands).order_by('name')
		else:
			brands=Brands.objects.filter(dropped=False).order_by('name')

		brands_array=[]
		pds_array=[]

		for brand in brands:
			pds=PurchasesDetails.objects.filter(dropped=False,brand=brand)
			for pd in pds:
				if pd.id not in pds_array:
					ppds=PurchasesProductsDetails.objects.filter(dropped=False,purchase_detail=pd,sold=False,stored=True)
					counter=0
					shops_array=[]
					for ppd in ppds:
						if ppd.in_store.shop.id not in shops_array:
							counter+=1
							shops_array.append(ppd.in_store.shop.id)
							shops.append(ppd.in_store.shop)
							shops_ids.append(ppd.in_store.shop.id)
					brands_array.append({'brand': brand, 'counter': counter})
					pds_array.append(pd.id)

		if products is not None:
			products=[int(i) for i in products]
			products=Products.objects.filter(dropped=False, pk__in=products).order_by('name')
		else:
			products=Products.objects.filter(dropped=False).order_by('name')

		products_array=[]
		pds_array=[]

		for product in products:
			pds=PurchasesDetails.objects.filter(dropped=False,product=product)
			for pd in pds:
				if pd.id not in pds_array:
					ppds=PurchasesProductsDetails.objects.filter(dropped=False,purchase_detail=pd,sold=False,stored=True)
					counter=0
					shops_array=[]
					for ppd in ppds:
						if ppd.in_store.shop.id not in shops_array:
							counter+=1
							shops_array.append(ppd.in_store.shop.id)
							if ppd.in_store.shop.id not in shops_ids:
								shops.append(ppd.in_store.shop)
					products_array.append({'product': product, 'counter': counter})
					pds_array.append(pd.id)

		shops_=[]
		current_shops_ids.clear()

		if city is not None:
			for shop in shops:
				current_shops_ids.append(shop.id)
				if shop.city.id == city.id:
					shops_.append(shop)
		else:
			shops_.extend(shops)
			current_shops_ids=[shop.id for shop in shops_]

		return ct, categories_array, brands_array, products_array, shops_
	else:
		if brands is not None:
			brands=[int(i) for i in brands]
			brands=Brands.objects.filter(dropped=False, pk__in=brands).order_by('name')
		else:
			brands=Brands.objects.filter(dropped=False).order_by('name')

		if products is not None:
			products=[int(i) for i in products]
			products=Products.objects.filter(dropped=False, pk__in=products).order_by('name')
		else:
			products=Products.objects.filter(dropped=False).order_by('name')

		# brands_array=[]
		# products_array=[]
		pds_array=[]
		if len(brands)>0 and len(products)>0:
			pds=PurchasesDetails.objects.filter(dropped=False,brand__in=brands,product__in=products)
		elif len(brands)>0:
			pds=PurchasesDetails.objects.filter(dropped=False,brand__in=brands)
		elif len(products)>0:
			pds=PurchasesDetails.objects.filter(dropped=False,product__in=products)
		else:
			pds=PurchasesDetails.objects.filter(dropped=False)

		for pd in pds:
			if pd.id not in pds_array:
				ppds=PurchasesProductsDetails.objects.filter(dropped=False,purchase_detail=pd,sold=False,stored=True)
				counter=0
				shops_array=[]
				for ppd in ppds:
					if ppd.in_store.shop.id not in shops_array:
						counter+=1
						shops_array.append(ppd.in_store.shop.id)
						shops.append(ppd.in_store.shop)
						shops_ids.append(ppd.in_store.shop.id)
				# brands_array.append({'brand': brand, 'counter': counter})
				pds_array.append(pd.id)

		# products_array.extend(products)

		shops_=[]
		current_shops_ids.clear()

		if city is not None:
			for shop in shops:
				current_shops_ids.append(shop.id)
				if shop.city.id == city.id:
					shops_.append(shop)
		else:
			shops_.extend(shops)
			current_shops_ids=[shop.id for shop in shops_]

		return ct, categories_array, None, None, shops_

def home(request):
	#categories = Tag.objects.all()
	context={}

	data=__retrieve_shops_home_filters__()
	ct=data[0]
	context['categories']=data[1]
	context['brands']=data[2]
	context['products']=data[3]

	shops=Shops.objects.filter(dropped=False).order_by('name')

	shops_array=[]

	for shop in shops:
		tis=TaggedItem.objects.filter(content_type=ct,object_id=shop.id)
		categories_=[]
		for ti in tis:
			categories_.append(ti.tag)
		shops_array.append({'shop': shop, 'categories': categories_})
		current_shops_ids.append(shop.id)

	context['shops']=shops_array

	return render(request, 'shops/index.html', context=context)

def apply_filters_shops_home(request):
	if request.method == 'GET':
		try:
			context = {}
			category=request.GET.get('category', None)
			city=request.GET.get('city', None)
			brands=request.GET.getlist('brands[]')
			products=request.GET.getlist('products[]')
			match_all=request.GET.get('match_all', True)
			news_first=request.GET.get('news_first', False)
			ordering=request.GET.get('ordering', Ordering.NONE)

			match_all=match_all=='true'
			news_first=news_first=='true'
			
			if ordering and ordering is not None and ordering is not Ordering.NONE:
				if 'ascending' in ordering:
					ordering=Ordering.ASCENDING
				else:
					ordering=Ordering.DESCENDING

			if city and city is not None:
				if int(city)>0:
					city=City.objects.get(pk=city)
					shops=Shops.objects.filter(dropped=False,city=city).order_by('name')
				else:
					city=None
					shops=Shops.objects.filter(dropped=False).order_by('name')
			else:
				city=None
				shops=Shops.objects.filter(dropped=False).order_by('name')

			data=__retrieve_shops_home_filters__(brands=brands,products=products,categories=[category],match_all_filters=match_all,city=city,news_first=news_first,ordering=ordering)
			ct=data[0]
			shops=data[4]
			# context['categories']=data[1]
			# context['brands']=data[2]
			# context['products']=data[3]

			# context['shops']=data[4]
			# print(data[4])

			# if not match_all:
			# 	if brands and brands is not None and len(brands)>0 or \
			# 	products and products is not None and len(products)>0:
			# 		shops=data[4]

			shops_array=[]
			for shop in shops:
				if category and category is not None:
					tis=TaggedItem.objects.filter(content_type=ct,object_id=shop.id,tag_id=category)
				else:
					tis=TaggedItem.objects.filter(content_type=ct,object_id=shop.id)
				categories_=[]
				categories_ids=[]
				for ti in tis:
					categories_.append(ti.tag)
					categories_ids.append(ti.tag.id)
				if category and category is not None:
					if int(category) in categories_ids:
						shops_array.append({'shop': shop, 'categories': categories_})
				else:
					shops_array.append({'shop': shop, 'categories': categories_})

			context['shops']=shops_array

			return render(request, 'shops/filtered-shops.html', context=context)
			# return shops_array
		except ObjectDoesNotExist:
			msg=_('The specified city does not exists')
			return JsonResponse({'status': 'error', 'msg': msg})
			# html='<script type="text/javascript">'
			# html+='show_msg_with_toastr("error", "' + msg + '");'
			# html+='</script>'
			# return HttpResponse(html, 'text/html; charset=utf-8')

	msg=_('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})
	# html='<script type="text/javascript">'
	# html+='show_msg_with_toastr("error", "' + msg + '");'
	# html+='</script>'
	# return HttpResponse(html, 'text/html; charset=utf-8')

def new_visit(request):
	if request.method == 'GET':
		try:
			shop=request.GET.get('shop', None)
			shop=Shops.objects.get(pk=shop)

			shop.visits_number=shop.visits_number+1
			shop.save()

			msg=_('One visit was added to the specified shop')
			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg=_('The specified shop does not exists')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg=_('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})