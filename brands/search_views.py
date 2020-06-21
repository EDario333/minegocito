from django.shortcuts import render, redirect

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from .models import Brands
from users.models import Users

def by_name(request):
	if request.method == 'GET':
		brand = request.GET.get('brand', None)

		try:
			user = Users.objects.get(pk=request.user)
			brand = Brands.objects.get(name__iexact=brand, created_by_user=user)

			#from django.core.serializers import serialize
			#product = serialize('json', [product])

			#return JsonResponse({'exist': True, 'status': 'info', 'product': product})
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': brand.dropped, 'brand': brand.id})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})