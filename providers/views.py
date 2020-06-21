from django.shortcuts import render, redirect

from django.contrib.auth.models import User

from django.db import transaction
from django.db.models import Q

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from .forms import FrmProviders, FrmContactPerson
from .models import Providers, ProvidersContactPersons

from users.models import Users
from catalogues.models import City, Person
'''

from shops.models import Shops

from shops.views import get_shops_created_by_user
'''
import json

dummy=_('Please enter a valid provider')
dummy=_('The contact person with the specified email already exists in the list of contact persons')
dummy=_('The contact person with the specified cell phone already exists in the list of contact persons')
dummy=_('Already exists one provider with the specified RFC')
dummy=_('Already exists one provider with the specified name')
dummy=_('Already exists one provider with the specified email')

def get_providers_created_by_user(request):
	my_user = Users.objects.get(pk=request.user)
	providers = Providers.objects.filter(created_by_user=my_user, dropped=False)
	return providers

def add(request):
	context = {}
	itm_menu = request.GET.get('itm_menu', 'lnk1')
	context['itm_menu'] = itm_menu

	if request.method == 'GET':
		frm = FrmProviders(title=_('Add provider'), action='/providers/do-add', btn_label=_('Save'), icon_btn_submit='save')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['app_version'] = app_version
		'''
		if app_version == _('Free version'):
			if get_providers_created_by_user(request) > 0:
				return render(request, 'providers/add-free-version-limited.html', context={'itm_menu': itm_menu})
		'''
	#html = render(request, 'providers/add.html', context={'form': frm})
	#return JsonResponse({'result': True, 'html': html})
	return render(request, 'providers/add.html', context=context)

def find(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_providers_created_by_user(request)) < 1:
			return render(request, 'providers/user-have-no-providers-created.html', context={'itm_menu': itm_menu})

		frm = FrmProviders(title=_('Find provider'), action='/providers/do-find', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'providers/find.html', context=context)

def do_add(request):
	frm = FrmProviders(title=_('Add provider'), action='/providers/do-add', btn_label=_('Save'), icon_btn_submit='save')
	context = {}
	context['form'] = frm
	context['msg'] = _('The provider can not be saved')
	context['level'] = 'error'

	if request.method == 'POST':
		try:
			app_version = request.POST['app_version']
			itm_menu = request.POST.get('itm_menu', '')
			context['itm_menu'] = itm_menu
			'''
			if app_version == _('Free version'):
				if get_providers_created_by_user(request) > 0:
					return render(request, 'providers/add-free-version-limited.html', context={'itm_menu': itm_menu})
			'''
			context['app_version'] = app_version

			email = request.POST.get('email', None)
			name = request.POST.get('name', None)

			# Check if the providers' email does not exist
			try:
				context['msg'] = _('A provider with the email specified already exists')
				context['level'] = 'error'
				Providers.objects.get(email__iexact=email)
				return render(request, 'providers/add.html', context=context)

				context['msg'] = _('The provider name already exists')
				Providers.objects.get(name__iexact=name)
				return render(request, 'providers/add.html', context=context)

				'''
				objs = Providers.objects.filter(name=provider_name, city=city, address_line1=address_line1)
				
				if len(objs) > 0:
					context['msg'] = _('The provider already exist')
					context['level'] = 'error'
					return render(request, 'providers/add.html', context=context)
				'''
			except ObjectDoesNotExist:
				pass

			rfc = request.POST.get('rfc', None)
			city = request.POST.get('city_obj', None)
			#admin = request.POST['admin']

			# Retrieve the city
			if city and city is not None and len(city.strip()) > 0:
				city = City.objects.get(pk=city)

			# Retrieve the user who is creating the provider
			#user = User.objects.get(email=request.POST['user'])
			#my_user = Users.objects.get(pk=request.user)
			my_user = Users.objects.get(username=request.user)

			address_line1 = request.POST.get('address_line1', None)
			address_line2 = request.POST.get('address_line2', None)

			cp = request.POST.get('cell_phone', None)
			hp = request.POST.get('home_phone', None)
			op = request.POST.get('other_phone', None)			

			contact_persons = request.POST.get('contact_persons', None)
			contact_persons = json.loads(contact_persons)

			obj = Providers(name=name, \
				rfc=rfc, \
				email=email, \
				city=city, \
				address_line1=address_line1, \
				address_line2=address_line2, \
				created_by_user=my_user, \
				cell_phone=cp, \
				home_phone=hp, \
				other_phone=op)

			with transaction.atomic():
				obj.save()

				for cp in contact_persons:
					person=Person()
					person.last_name=cp['last-name']
					person.mothers_last_name=cp['mothers-last-name']
					person.first_name=cp['first-name']
					person.middle_name=cp['middle-name']
					person.gender=cp['gender']
					dob=cp['dob']
					if len(dob.strip())>0:
						dob=dob[6:]+'-'+dob[3:5]+'-'+dob[0:2]
					else:
						dob=None
					person.dob=dob
					person.email=cp['email']
					city = cp['city']

					if len(city.strip())>0:
						try:
							city = City.objects.get(pk=city)
						except ObjectDoesNotExist:
							msg = _('The specified city does not exists')
							return JsonResponse({'status': 'error', 'msg': msg})
					else:
						city=None

					person.city=city
					person.address_line1=cp['addr1']
					person.address_line2=cp['addr2']
					person.cell_phone=cp['cp']
					person.home_phone=cp['hp']
					person.other_phone=cp['op']
					person.created_by_user=my_user
					person.save()

					pcp=ProvidersContactPersons()
					pcp.provider=obj
					pcp.contact_person=person
					pcp.created_by_user=my_user
					pcp.save()

				context['msg'] = _('The provider has been successfully saved')
				context['level'] = 'success'
		except MultiValueDictKeyError:
			#print('******ERROR1*****')
			return redirect('/')
		except ObjectDoesNotExist:
			#print('******ERROR2*****')
			return redirect('/')

	return render(request, 'providers/add.html', context=context)

def __generic_find_view__(request, can_delete=False, can_edit=False, view_all=False):
	frm = FrmProviders(title=_('Find provider'), action='/providers/do-find', btn_label=_('Find'), icon_btn_submit='search')
	context = {}
	context['msg'] = _('We can not find any provider matching with your query options')
	context['level'] = 'error'
	providers = Providers.objects.none()
	itm_menu = request.POST.get('itm_menu', request.GET.get('itm_menu', ''))
	context['itm_menu'] = itm_menu
	#context['url_view_all'] = '/providers/list-all/'

	# Retrieve the user logged in
	my_user = Users.objects.get(pk=request.user)

	if request.method == 'POST':
		try:
			app_version = request.POST.get('app_version', _('Free version'))
			#itm_menu = request.POST.get('itm_menu', '')
			#context['itm_menu'] = itm_menu
			context['app_version'] = app_version
			providers = []

			# (1) Search in providers table...
			search=False
			search_by = {
				'name__icontains': False, 
				'rfc__icontains': False,
				'city__iexact': False, 
				'address_line1__icontains': False, 
				'address_line2__icontains': False, 
				'email__iexact': False, 
				'cell_phone__iexact': False, 
				'home_phone__iexact': False, 
				'other_phone__iexact': False
			}
			
			name = request.POST.get('name', None)
			if name and name is not None and len(name.strip()) > 0:
				search=True
				search_by['name__icontains'] = name.strip()

			rfc = request.POST.get('rfc', None)
			if rfc and rfc is not None and len(rfc.strip()) > 0:
				search=True
				search_by['rfc__icontains'] = rfc.strip()

			city = request.POST.get('city_obj', None)
			if city and city is not None and len(city.strip()) > 0:
				search=True
				search_by['city__iexact'] = city.strip()

			address_line1 = request.POST.get('address_line1', None)
			if address_line1 and address_line1 is not None and len(address_line1.strip()) > 0:
				search=True
				search_by['address_line1__icontains'] = address_line1.strip()

			address_line2 = request.POST.get('address_line2', None)
			if address_line2 and address_line2 is not None and len(address_line2.strip()) > 0:
				search=True
				search_by['address_line2__icontains'] = address_line2.strip()

			email = request.POST.get('email', None)
			if email and email is not None and len(email.strip()) > 0:
				search=True
				search_by['email__iexact'] = email.strip()

			cell_phone = request.POST.get('cell_phone', None)
			if cell_phone and cell_phone is not None and len(cell_phone.strip()) > 0:
				search=True
				search_by['cell_phone__iexact'] = cell_phone.strip()

			home_phone = request.POST.get('home_phone', None)
			if home_phone and home_phone is not None and len(home_phone.strip()) > 0:
				search=True
				search_by['home_phone__iexact'] = home_phone.strip()

			other_phone = request.POST.get('other_phone', None)
			if other_phone and other_phone is not None and len(other_phone.strip()) > 0:
				search=True
				search_by['other_phone__iexact'] = other_phone.strip()

			# See https://stackoverflow.com/questions/38131563/django-filter-with-or-condition-using-dict-argument
			# for more details
			from functools import reduce
			import operator

			if search:
				query = Q(created_by_user=my_user) & Q(dropped=False)

				final_search_by = {}

				for criteria in search_by:
					if search_by[criteria]:
						final_search_by[criteria] = search_by[criteria]

				# Build the query...
				query &= reduce(operator.or_, (Q(**d) for d in [dict([i]) for i in final_search_by.items()]))

				providers_ = Providers.objects.filter(query)
				providers.extend(providers_)

			# (2) Prepare and extract values for searching
			# providerscontactpersons 
			# (in fact, is in catalogues_person. 
			# See providers.models.ProvidersContactPersons
			# for more details)
			cps = request.POST.get('contact_persons', None)
			cps = json.loads(cps)
			print('**********cps*********')
			print(cps)

			lns=[]
			mlns=[]
			fns=[]
			mns=[]
			genders=[]
			dobs=[]
			emails=[]
			cities=[]
			addrs1=[]
			addrs2=[]
			c_ps=[]
			hps=[]
			ops=[]

			for cp in cps:
				print('**********contact person*********')
				print(cp)
				lns.append(cp['last-name'])
				mlns.append(cp['mothers-last-name'])
				fns.append(cp['first-name'])
				mns.append(cp['middle-name'])
				genders.append(cp['gender'])
				dobs.append(cp['dob'])
				emails.append(cp['email'])
				cities.append(cp['city'])
				addrs1.append(cp['addr1'])
				addrs2.append(cp['addr2'])
				c_ps.append(cp['cp'])
				hps.append(cp['hp'])
				ops.append(cp['op'])

			# (3) Prepare query for providerscontactpersons
			pcp_results = []
			all_pcp_id = []
			tope=len(lns)

			search_by = {
				'last_name__icontains': False, 
				'mothers_last_name__icontains': False,
				'first_name__icontains': False,
				'middle_name__icontains': False,
				'gender__iexact': False,
				'dob': False,
				'email__iexact': False,
				'city': False,
				'address_line1__icontains': False,
				'address_line2__icontains': False,
				'cell_phone': False,
				'home_phone': False,
				'other_phone': False,
			}

			for x in range(tope):
				search_by['last_name__icontains'] = lns[x]
				search_by['mothers_last_name__icontains'] = mlns[x]
				search_by['first_name__icontains'] = fns[x]
				search_by['middle_name__icontains'] = mns[x]
				search_by['gender__iexact'] = genders[x]
				search_by['dob'] = dobs[x]
				search_by['email__iexact'] = emails[x]
				search_by['city'] = cities[x]
				search_by['address_line1__icontains'] = addrs1[x]
				search_by['address_line2__icontains'] = addrs2[x]
				search_by['cell_phone'] = c_ps[x]
				search_by['home_phone'] = hps[x]
				search_by['other_phone'] = ops[x]

				final_search_by = {}

				for criteria in search_by:
					if search_by[criteria]:
						final_search_by[criteria] = search_by[criteria]

				if len(final_search_by) > 0:
					query = Q(created_by_user=my_user) & Q(dropped=False)
					query &= reduce(operator.or_, (Q(**d) for d in [dict([i]) for i in final_search_by.items()]))

					# (3.1) Execute the query for 
					# providerscontactpersons (catalogues_person)
					results = Person.objects.filter(query)

					# (4) Now we must to verify that the persons
					# are not the same
					for result in results:
						if result.id not in all_pcp_id:
							all_pcp_id.append(result.id)
							pcp_results.append(result)

			# (5) Search the providers with the contact 
			# persons found...
			providers_=ProvidersContactPersons.objects.filter(contact_person__in=pcp_results,dropped=False)

			# (6) Add the results but excluding those 
			# are ready included in providers
			for provider in providers_:
				if provider.provider not in providers:
					providers.append(provider.provider)

			#context['msg'] = _('We found {0} result(s) matching your query').format(len(providers))
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

		providers = Providers.objects.filter(created_by_user=my_user, dropped=False)

	if len(providers) > 0:
		context['providers'] = providers

		context['show_modal'] = True
		context['modal_name'] = 'dlgSearchResults'
		context['can_delete'] = can_delete
		context['can_edit'] = can_edit

		context.pop('msg', None)
		context.pop('level', None)

	if can_edit:
		frm = FrmProviders(title=_('Edit provider'), action='/providers/do-edit', btn_label=_('Find'), icon_btn_submit='search')
	elif can_delete:
		frm = FrmProviders(title=_('Delete provider'), action='/providers/do-delete', btn_label=_('Find'), icon_btn_submit='search')

	context['form'] = frm

	return render(request, 'providers/find.html', context=context)

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

		if len(get_providers_created_by_user(request)) < 1:
			return render(request, 'providers/user-have-no-providers-created.html', context={'itm_menu': itm_menu})

		frm = FrmProviders(title=_('Edit provider'), action='/providers/do-edit', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'providers/find.html', context=context)

def do_edit(request):
	return __generic_find_view__(request, can_edit=True)

def delete(request):
	context = {}

	if request.method == 'GET':
		itm_menu = request.GET.get('itm_menu', '')

		if len(get_providers_created_by_user(request)) < 1:
			return render(request, 'providers/user-have-no-providers-created.html', context={'itm_menu': itm_menu})

		frm = FrmProviders(title=_('Delete provider'), action='/providers/do-delete', btn_label=_('Find'), icon_btn_submit='search')
		app_version = request.GET['app_version']
		context['form'] = frm
		context['itm_menu'] = itm_menu

	return render(request, 'providers/find.html', context=context)

def do_delete(request):
	return __generic_find_view__(request, can_delete=True)

def view_details(request):
	if request.method == 'GET':
		try:
			provider = request.GET.get('obj', None)
			provider = Providers.objects.get(pk=provider)
			cps=ProvidersContactPersons.objects.filter(provider=provider,dropped=False)

			can_edit = request.GET.get('can_edit', False)
			can_delete = request.GET.get('can_delete', False)
			itm_menu = request.GET.get('itm_menu', 'lnk1')

			context = {
				'provider': provider, 'can_edit': can_edit, 
				'can_delete': can_delete, 'itm_menu': itm_menu,
				'has_contact_persons': len(cps)>0
			}

			return render(request, 'providers/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def confirm_delete(request):
	if request.method == 'GET':
		try:
			provider = request.GET.get('provider', None)
			provider = Providers.objects.get(pk=provider)

			context = {
				'provider': provider, 
				'can_delete': True
			}

			return render(request, 'providers/view-details.html', context=context)
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def delete_provider(request):
	if request.method == 'POST':
		try:
			provider = request.POST.get('provider', None)
			provider = Providers.objects.get(pk=provider)
			reason = request.POST.get('reason', None)
			if len(reason.strip()) < 1:
				reason = None
			itm_menu = request.POST.get('itm_menu', 'lnk1')

			provider.drop(reason=reason)

			frm = FrmProviders(title=_('Delete provider'), action='/providers/do-delete', btn_label=_('Find'), icon_btn_submit='search')
			#app_version = request.GET['app_version']
			#context['form'] = frm
			#context['itm_menu'] = itm_menu

			context = {
				'level': 'success',
				'msg': _('The provider has been deleted successfully'),
				'itm_menu': itm_menu,
				'form': frm
			}

			return render(request, 'providers/find.html', context=context)
			#return find(request)
			#return redirect('/providers/find')
		except ObjectDoesNotExist:
			return redirect('/')

	return redirect('/')

def update(request):
	if request.method == 'POST':
		try:
			provider = request.POST.get('provider', None)
			provider = Providers.objects.get(pk=provider)

			name = request.POST.get('name', None)
			rfc = request.POST.get('rfc', None)
			city = request.POST.get('city_obj', None)

			address_line1 = request.POST.get('addressline1', None)
			address_line2 = request.POST.get('addressline2', None)

			email = request.POST.get('email', None)
			cp = request.POST.get('cellphone', None)
			hp = request.POST.get('homephone', None)
			op = request.POST.get('otherphone', None)

			# ln = request.POST.get('last_name', None)
			# mln = request.POST.get('mothers_last_name', None)
			# fn = request.POST.get('first_name', None)
			# mn = request.POST.get('middle_name', None)

			# provider.contact_person.last_name = ln
			# provider.contact_person.mothers_last_name = mln
			# provider.contact_person.first_name = fn
			# provider.contact_person.middle_name = mn
			#provider.gender = gender
			#provider.dob = dob
			provider.name=name
			provider.rfc=rfc
			provider.city = City.objects.get(pk=city)
			provider.address_line1 = address_line1
			provider.address_line2 = address_line2
			provider.email = email
			provider.cell_phone = cp
			provider.home_phone = hp
			provider.other_phone = op

			provider.save()
			msg = _('The provider has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The provider you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def new_contact_person(request):
	if request.method == 'GET':
		context={}
		module=request.GET.get('module', 'find')
		frm = FrmContactPerson(title=_('Contact person'), btn_label=_('Add'))
		if 'ADD' in module.upper():
			frm = FrmContactPerson(title=_('New contact person'), btn_label=_('Add'))
		context['form'] = frm
		return render(request, 'providers/contact-person.html',context=context)

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def view_details_contact_person(request):
	if request.method == 'GET':
		context={}
		data=request.GET.get('data', None)
		data=json.loads(data)

		context['first_name'] = data['fn']
		context['middle_name'] = data['mn']
		context['last_name'] = data['ln']
		context['mothers_last_name'] = data['mln']
		gender=data['gender']
		context['gender'] = gender
		if gender == '':
			context['gender_as_long_string'] = _('Prefer not to say')
		elif gender == 'M':
			context['gender_as_long_string'] = _('Male')
		else:
			context['gender_as_long_string'] = _('Female')

		context['dob'] = data['dob']
		context['email'] = data['email']
		city=data['city']

		if len(city.strip()) > 0:
			try:
				city=City.objects.get(pk=city)
				context['city'] = city.display_name
				context['city_id'] = city.id
			except ObjectDoesNotExist:
				msg = _('The specified city does not exists')
				return JsonResponse({'status': 'error', 'msg': msg})
		else:
			context['city'] = ''
			context['city_id'] = ''

		# context['city'] = data['city']
		context['addr1'] = data['addr1']
		context['addr2'] = data['addr2']
		context['cell_phone'] = data['cp']
		context['home_phone'] = data['hp']
		context['other_phone'] = data['op']
		context['can_edit'] = data['can_edit']
		context['can_delete'] = data['can_delete']
		context['enter_and_edit'] = data['enter_and_edit']
		context['row_id'] = data['row_id']
		return render(request, 'providers/view-details-contact-person.html',context=context)

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def show_contact_persons(request):
	if request.method == 'GET':
		context={}
		provider=request.GET.get('provider', None)
		can_edit = request.GET.get('can_edit', False)
		can_delete = request.GET.get('can_delete', False)
		can_edit = can_edit.upper() == 'TRUE'
		can_delete = can_delete.upper() == 'TRUE'

		try:
			pcp=ProvidersContactPersons.objects.filter(provider=provider,dropped=False)
			context = {
				'contact_persons': pcp,
				'provider': provider,
				'can_edit': can_edit,
				'can_delete': can_delete
			}
			return render(request, 'providers/contact-persons-provider.html', context=context)
		except ObjectDoesNotExist:
			msg = _('The provider does not exists')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})