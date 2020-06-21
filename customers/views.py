from django.shortcuts import render, redirect

from django.contrib.auth.models import User

from django.db.models import Q

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from django.utils.datastructures import MultiValueDictKeyError

from .forms import FrmCustomers
from .models import Customers

from users.models import Users

from catalogues.models import City
'''
from shops.models import Shops

from shops.views import get_shops_created_by_user

dummy=_('Please enter a valid customer')
'''
import json

dummy=_('Already exists one customer with the specified RFC')
dummy=_('Already exists one customer with the specified email')

def get_customers_created_by_user(request):
	#my_user = Users.objects.get(pk=request.user)
	my_user = Users.objects.get(username=request.user)
	customers = Customers.objects.filter(created_by_user=my_user, dropped=False)

	return customers

def add(request):
	context = {}
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	context['itm_menu'] = itm_menu

	if request.method == 'GET':
		frm = FrmCustomers(title=_('Add customer'), action='/customers/do-add', btn_label=_('Save'), icon_btn_submit='save')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['app_version'] = app_version
		'''
		if app_version == _('Free version'):
			if get_customers_created_by_user(request) > 0:
				return render(request, 'customers/add-free-version-limited.html', context={'itm_menu': itm_menu})
		'''
	#html = render(request, 'customers/add.html', context={'form': frm})
	#return JsonResponse({'result': True, 'html': html})
	return render(request, 'customers/add.html', context=context)

def find(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_customers_created_by_user(request)) < 1:
			return render(request, 'customers/user-have-no-customers-created.html', context={'itm_menu': itm_menu})

		frm = FrmCustomers(title=_('Find customer'), action='/customers/do-find', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'customers/find.html', context=context)

def do_add(request):
	frm = FrmCustomers(title=_('Add customer'), action='/customers/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The customer can not be saved')
	context['level'] = 'error'

	if request.method == 'POST':
		try:
			app_version = request.POST['app_version']
			itm_menu = request.POST.get('itm_menu', '')
			context['itm_menu'] = itm_menu
			'''
			if app_version == _('Free version'):
				if get_customers_created_by_user(request) > 0:
					return render(request, 'customers/add-free-version-limited.html', context={'itm_menu': itm_menu})
			'''
			context['app_version'] = app_version
			city = request.POST.get('city_obj', None)
			#admin = request.POST['admin']

			# Retrieve the city
			if city and city is not None and len(city.strip()) > 0:
				city = City.objects.get(pk=city)
			else:
				city=None

			# Retrieve the user who is creating the customer
			#user = User.objects.get(email=request.POST['user'])
			#my_user = Users.objects.get(pk=request.user)
			my_user = Users.objects.get(username=request.user)

			email = request.POST.get('email', None)
			rfc = request.POST.get('rfc', None)

			# Check if the customers' email does not exist
			from customers.search_views import search_by_email
			result=search_by_email(email, request)
			result=json.loads(result.content)
			if result['exist']:
				context['msg'] = _('Already exists one customer with the specified email')
				context['level'] = 'error'
				return render(request, 'customers/add.html', context=context)

			#Check if the customers' RFC does not exist
			from customers.search_views import search_by_rfc
			result=search_by_rfc(rfc, request)
			result=json.loads(result.content)
			if result['exist']:
				context['msg'] = _('Already exists one customer with the RFC specified')
				context['level'] = 'error'
				return render(request, 'customers/add.html', context=context)

			# try:
				# Check if the customers' email does not exist
				# Customers.objects.get(email__iexact=email)
				# context['msg'] = _('Already exists one customer with the specified email')
				# context['level'] = 'error'
				# return render(request, 'customers/add.html', context=context)
				'''
				objs = Customers.objects.filter(name=customer_name, city=city, address_line1=address_line1)
				
				if len(objs) > 0:
					context['msg'] = _('The customer already exist')
					context['level'] = 'error'
					return render(request, 'customers/add.html', context=context)
				'''
			# except ObjectDoesNotExist:
				# pass
				# Check if the customers' RFC does not exist
				# from customers.search_views import search_by_rfc
				# result=search_by_rfc(rfc, request)
				# result=json.loads(result.content)
				# if result['exist']:
				# 	context['msg'] = _('Already exists one customer with the RFC specified')
				# 	context['level'] = 'error'
				# 	return render(request, 'customers/add.html', context=context)

			ln = request.POST.get('last_name', None)
			mln = request.POST.get('mothers_last_name', None)
			fn = request.POST.get('first_name', None)
			mn = request.POST.get('middle_name', None)
			gender = request.POST.get('gender', None)
			dob = request.POST.get('dob', None)
			address_line1 = request.POST.get('address_line1', None)
			address_line2 = request.POST.get('address_line2', None)
			cp = request.POST.get('cell_phone', None)
			hp = request.POST.get('home_phone', None)
			op = request.POST.get('other_phone', None)

			if dob and dob is not None and len(dob.strip()) > 0:
				dob=dob[6:]+'-'+dob[3:5]+'-'+dob[:2]

			obj = Customers(rfc=rfc, \
				last_name=ln, \
				mothers_last_name=mln, \
				first_name=fn, \
				middle_name=mn, \
				gender=gender, \
				dob=dob, \
				email=email, \
				city=city, \
				address_line1=address_line1, \
				address_line2=address_line2, \
				created_by_user=my_user, \
				cell_phone=cp, \
				home_phone=hp, \
				other_phone=op)

			obj.save()
			context['msg'] = _('The customer has been successfully saved')
			context['level'] = 'success'
		except MultiValueDictKeyError as e:
			#print('******ERROR1*****')
			print(e.args[0])
			return redirect('/')
		except ObjectDoesNotExist as e:
			#print('******ERROR2*****')
			print(e.args[0])
			return redirect('/')
		except IntegrityError as e:
			if 'catalogues_person.email, catalogues_person.created_by_user' in e.args[0]:
				customer=Customers.objects.get(email__iexact=email)
				customer.rfc=rfc
				customer.last_name=ln
				customer.first_name=fn
				customer.middle_name=mn
				customer.gender=gender
				customer.dob=dob
				customer.city=city
				customer.address_line1=address_line1
				customer.address_line2=address_line2
				customer.cell_phone=cp
				customer.home_phone=hp
				customer.other_phone=op
				customer.undrop()
				context['msg'] = _('The customer has been successfully saved')
				context['level'] = 'success'

	return render(request, 'customers/add.html', context=context)

def __generic_find_view__(request, can_delete=False, can_edit=False, view_all=False):
	frm = FrmCustomers(title=_('Find customer'), action='/customers/do-find', btn_label=_('Find'), icon_btn_submit='search')
	context = {}
	context['msg'] = _('We can not find any customer matching with your query options')
	context['level'] = 'error'
	context['form'] = frm
	customers = Customers.objects.none()
	itm_menu = request.POST.get('itm_menu', request.GET.get('itm_menu', ''))
	context['itm_menu'] = itm_menu
	#context['url_view_all'] = '/customers/list-all/'

	if request.method == 'POST':
		try:
			# Retrieve the user logged in
			my_user = Users.objects.get(pk=request.user)

			app_version = request.POST.get('app_version', _('Free version'))
			#itm_menu = request.POST.get('itm_menu', '')
			#context['itm_menu'] = itm_menu
			context['app_version'] = app_version

			search_by = {
				'rfc__iexact': False, 
				'last_name__icontains': False, 
				'mothers_last_name__icontains': False, 
				'first_name__icontains': False, 
				'middle_name__icontains': False, 
				'gender__iexact': False,
				'dob__iexact': False,
				'email__iexact': False, 
				'city__iexact': False,
				'address_line1__icontains': False, 
				'address_line2__icontains': False, 
				'cell_phone__iexact': False, 
				'home_phone__iexact': False, 
				'other_phone__iexact': False
			}

			rfc = request.POST.get('rfc', None)
			if rfc and rfc is not None and len(rfc.strip()) > 0:
				if 'XXXXXXXXXXX'+str(my_user.id) in rfc:
					if can_edit:
						frm = FrmCustomers(title=_('Edit customer'), action='/customers/do-edit', btn_label=_('Find'), icon_btn_submit='search')
					elif can_delete:
						frm = FrmCustomers(title=_('Delete customer'), action='/customers/do-delete', btn_label=_('Find'), icon_btn_submit='search')
					context['form'] = frm
					return render(request, 'customers/find.html', context=context)
				search_by['rfc__iexact'] = rfc.strip()

			ln = request.POST.get('last_name', None)
			if ln and ln is not None and len(ln.strip()) > 0:
				search_by['last_name__icontains'] = ln.strip()

			mln = request.POST.get('mothers_last_name', None)
			if mln and mln is not None and len(mln.strip()) > 0:
				search_by['mothers_last_name__icontains'] = mln.strip()

			fn = request.POST.get('first_name', None)
			if fn and fn is not None and len(fn.strip()) > 0:
				search_by['first_name__icontains'] = fn.strip()

			mn = request.POST.get('middle_name', None)
			if mn and mn is not None and len(mn.strip()) > 0:
				search_by['middle_name__icontains'] = mn.strip()

			gender = request.POST.get('gender', None)
			if gender and gender is not None and len(gender.strip()) > 0:
				search_by['gender__iexact'] = gender.strip()

			dob = request.POST.get('dob', None)
			if dob and dob is not None and len(dob.strip()) > 0:
				search_by['dob__iexact'] = dob.strip()

			email = request.POST.get('email', None)
			if email and email is not None and len(email.strip()) > 0:
				search_by['email__iexact'] = email.strip()

			city = request.POST.get('city_obj', None)
			if city and city is not None and len(city.strip()) > 0:
				# Retrieve the city
				search_by['city__iexact'] = City.objects.get(pk=city)

			address_line1 = request.POST.get('address_line1', None)
			if address_line1 and address_line1 is not None and len(address_line1.strip()) > 0:
				search_by['address_line1__icontains'] = address_line1.strip()

			address_line2 = request.POST.get('address_line2', None)
			if address_line2 and address_line2 is not None and len(address_line2.strip()) > 0:
				search_by['address_line2__icontains'] = address_line2.strip()

			cell_phone = request.POST.get('cell_phone', None)
			if cell_phone and cell_phone is not None and len(cell_phone.strip()) > 0:
				search_by['cell_phone__iexact'] = cell_phone.strip()

			home_phone = request.POST.get('home_phone', None)
			if home_phone and home_phone is not None and len(home_phone.strip()) > 0:
				search_by['home_phone__iexact'] = home_phone.strip()

			other_phone = request.POST.get('other_phone', None)
			if other_phone and other_phone is not None and len(other_phone.strip()) > 0:
				search_by['other_phone__iexact'] = other_phone.strip()

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

			customers = Customers.objects.filter(query)
			#context['msg'] = _('We found {0} result(s) matching your query').format(len(customers))
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
		#my_user = Users.objects.get(pk=user.id)
		my_user = Users.objects.get(pk=request.user)
		query = \
			Q(created_by_user=my_user) & Q(dropped=False) & \
			~Q(rfc__icontains='XXXXXXXXXXX'+str(my_user.id))
		#customers = Customers.objects.filter(query)
		customers = Customers.objects.filter(query)

	if len(customers) > 0:
		context['customers'] = customers

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmCustomers(title=_('Edit customer'), action='/customers/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmCustomers(title=_('Delete customer'), action='/customers/do-delete', btn_label=_('Find'), icon_btn_submit='search')

	context['form'] = frm

	return render(request, 'customers/find.html', context=context)

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

		if len(get_customers_created_by_user(request)) < 1:
			return render(request, 'customers/user-have-no-customers-created.html', context={'itm_menu': itm_menu})

		frm = FrmCustomers(title=_('Edit customer'), action='/customers/do-edit', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'customers/find.html', context=context)

def do_edit(request):
	return __generic_find_view__(request, can_edit=True)

def delete(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_customers_created_by_user(request)) < 1:
			return render(request, 'customers/user-have-no-customers-created.html', context={'itm_menu': itm_menu})

		frm = FrmCustomers(title=_('Delete customer'), action='/customers/do-delete', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'customers/find.html', context=context)

def do_delete(request):
	return __generic_find_view__(request, can_delete=True)

def view_details(request):
	if request.method == 'GET':
		try:
			customer = request.GET.get('obj', None)
			customer = Customers.objects.get(pk=customer)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'customer': customer, 'can_edit': can_edit, 
				'can_delete': can_delete, 'itm_menu': itm_menu
			}

			return render(request, 'customers/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def confirm_delete(request):
	if request.method == 'GET':
		try:
			customer = request.GET.get('customer', None)
			customer = Customers.objects.get(pk=customer)

			context = {
				'customer': customer, 
				'can_delete': True
			}

			return render(request, 'customers/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def delete_customer(request):
	if request.method == 'POST':
		try:
			customer = request.POST.get('customer', None)
			#print('*******customer******')
			#print(customer)
			customer = Customers.objects.get(pk=customer)
			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			customer.drop(reason=reason)

			frm = FrmCustomers(title=_('Delete customer'), action='/customers/do-delete', btn_label=_('Find'), icon_btn_submit='search')
			#app_version = request.GET['app_version']
			#context['form'] = frm
			#context['itm_menu'] = itm_menu

			context = {
				'level': 'success',
				'msg': _('The customer has been deleted successfully'),
				'itm_menu': itm_menu,
				'form': frm
			}

			return render(request, 'customers/find.html', context=context)
			#return find(request)
			#return redirect('/customers/find')
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def update(request):
	if request.method == 'POST':
		try:
			customer = request.POST.get('customer', None)
			customer = Customers.objects.get(pk=customer)

			rfc = request.POST.get('rfc', None)
			ln = request.POST.get('last_name', None)
			mln = request.POST.get('mothers_last_name', None)
			fn = request.POST.get('first_name', None)
			mn = request.POST.get('middle_name', None)
			gender = request.POST.get('gender', None)
			dob = request.POST.get('dob', None)
			email = request.POST.get('email', None)
			city = request.POST.get('city_obj', None)
			address_line1 = request.POST.get('address_line1', '')
			address_line2 = request.POST.get('address_line2', '')
			cp = request.POST.get('cellphone', '')
			hp = request.POST.get('homephone', '')
			op = request.POST.get('otherphone', '')

			customer.rfc=rfc
			customer.last_name = ln
			customer.mothers_last_name = mln
			customer.first_name = fn
			customer.middle_name = mn
			customer.gender = gender
			customer.dob = dob[6:]+'-'+dob[3:5]+'-'+dob[0:2]
			customer.email = email
			if city and city is not None and len(city.strip())>0:
				try:
					city=City.objects.get(pk=city)
				except ObjectDoesNotExist:
					msg = _('The specified city does not exists')
					return JsonResponse({'status': 'error', 'msg': msg})
			else:
				city=None

			customer.city = city
			customer.address_line1 = address_line1
			customer.address_line2 = address_line2
			customer.cell_phone = cp
			customer.home_phone = hp
			customer.other_phone = op

			customer.save()
			msg = _('The customer has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The customer you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})
		except ValidationError as e:
			if 'AAAA-MM-DD' or 'YYYY-MM-DD' in e.args[0]:
				msg = _('Wrong format for date of birth')
				return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})