from django.shortcuts import render, redirect

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from .models import Stores
from users.models import Users

def by_name(request):
	if request.method == 'GET':
		store = request.GET.get('store', None)

		try:
			#user = Users.objects.get(pk=request.user)
			user = Users.objects.get(username=request.user)
			store = Stores.objects.get(name__iexact=store, created_by_user=user,dropped=False)

			#from django.core.serializers import serialize
			#product = serialize('json', [product])

			#return JsonResponse({'exist': True, 'status': 'info', 'product': product})
			return JsonResponse({'exist': True, 'status': 'info', 'dropped': store.dropped, 'store': store.id, 'belongs_to_shop': store.shop.id, 'shop_name': store.shop.name})
		except ObjectDoesNotExist:
			return JsonResponse({'exist': False, 'status': 'info', 'msg': _('The object does not exist')})

	return JsonResponse({'exist': False, 'status': 'error', 'msg': _('You do not have permission to perform this request'),'exist': None})