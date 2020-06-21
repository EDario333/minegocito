from django.shortcuts import render, redirect

# from django.contrib.auth.models import User

# from django.db import transaction
# from django.db.models import Q

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist
# from django.utils.datastructures import MultiValueDictKeyError

# from .forms import FrmProviders, FrmContactPerson
# from .models import Providers, ProvidersContactPersons
from .models import ProvidersContactPersons

from users.models import Users
# from catalogues.models import City, Person
from catalogues.models import City

def edit(request):
	if request.method == 'GET':
		try:
			context={}
			cp = request.GET.get('cp', None)
			can_edit=request.GET.get('can_edit', False)
			can_delete=request.GET.get('can_delete', False)
			enter_and_edit=request.GET.get('enter_and_edit', None)
			cp=ProvidersContactPersons.objects.get(pk=cp)
			context['cp']=cp.contact_person
			context['can_edit']=can_edit
			context['can_delete']=can_delete
			context['enter_and_edit']=enter_and_edit

			return render(request, 'providers/edit-contact-person.html',context=context)
		except ObjectDoesNotExist:
			msg = _('The contact person you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def delete_all(request):
	if request.method == 'GET':
		try:
			provider = request.GET.get('provider', None)
			cps=ProvidersContactPersons.objects.filter(provider=provider)

			for cp in cps:
				cp.drop()

			return JsonResponse({'status': 'success'})
		except ObjectDoesNotExist:
			msg = _('The contact person you are trying to update does not exist')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def delete_contact_person(request):
	if request.method == 'POST':
		try:
			cp=request.POST.get('contact_person', None)
			cp=ProvidersContactPersons.objects.get(contact_person=cp)
			reason=request.POST.get('reason', None)
			cp.drop(reason=reason)
			msg=_('The contact person has been deleted successfully'),
			return JsonResponse({'status': 'success', 'msg': msg, 'cp': cp.id})
		except ObjectDoesNotExist:
			msg = _('The contact person you are trying to delete does not exists')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def update(request):
	if request.method == 'POST':
		try:
			cp=request.POST.get('contact_person', None)
			cp=ProvidersContactPersons.objects.get(contact_person=cp)

			fn=request.POST.get('first_name', None)
			mn=request.POST.get('middle_name', None)
			ln=request.POST.get('last_name', None)
			mln=request.POST.get('mothers_last_name', None)
			gender=request.POST.get('gender', None)
			dob=request.POST.get('dob', None)
			dob=dob[6:]+'-'+dob[3:5]+'-'+dob[0:2]

			email = request.POST.get('email', None)
			city = request.POST.get('city_obj', None)

			address_line1 = request.POST.get('addressline1', None)
			address_line2 = request.POST.get('addressline2', None)

			c_p = request.POST.get('cellphone', None)
			hp = request.POST.get('homephone', None)
			op = request.POST.get('otherphone', None)

			cp.contact_person.first_name=fn
			cp.contact_person.middle_name=mn
			cp.contact_person.last_name=ln
			cp.contact_person.mothers_last_name=mln
			cp.contact_person.gender=gender
			cp.contact_person.dob=dob
			cp.contact_person.email=email
			cp.contact_person.city=None
			if city and city is not None:
				cp.contact_person.city = City.objects.get(pk=city)

			cp.contact_person.address_line1 = address_line1
			cp.contact_person.address_line2 = address_line2			
			cp.contact_person.cell_phone = c_p
			cp.contact_person.home_phone = hp
			cp.contact_person.other_phone = op

			cp.contact_person.save()
			msg = _('The contact person has been updated successfully')

			return JsonResponse({'status': 'success', 'msg': msg})
		except ObjectDoesNotExist:
			msg = _('The contact person you are trying to update does not exists')
			return JsonResponse({'status': 'error', 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})