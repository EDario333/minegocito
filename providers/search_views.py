from django.shortcuts import render, redirect

#from django.db.models import Q

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from .models import Providers
from users.models import Users

def by_rfc(request):
	if request.method == 'GET':
		rfc = request.GET.get('rfc', None)

		try:
			#user = Users.objects.get(pk=request.user)
			user = Users.objects.get(username=request.user)
			provider = Providers.objects.get(rfc__iexact=rfc,created_by_user=user,dropped=False)

			#from django.core.serializers import serialize
			#product = serialize('json', [product])

			#return JsonResponse({'exist': True, 'status': 'info', 'product': product})
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': provider.dropped, 'provider': provider.id})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})

def by_name(request):
	if request.method == 'GET':
		name = request.GET.get('name', None)

		try:
			user = Users.objects.get(pk=request.user)
			provider = Providers.objects.get(name__iexact=name,created_by_user=user,dropped=False)

			#from django.core.serializers import serialize
			#product = serialize('json', [product])

			#return JsonResponse({'exist': True, 'status': 'info', 'product': product})
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': provider.dropped, 'provider': provider.id})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})

def by_email(request):
	if request.method == 'GET':
		email = request.GET.get('email', None)

		try:
			user = Users.objects.get(pk=request.user)
			provider = Providers.objects.get(email__iexact=email,created_by_user=user,dropped=False)
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': provider.dropped, 'provider': provider.id})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})