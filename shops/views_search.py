#from django.shortcuts import render, redirect

from django.http import JsonResponse
from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from .models import Shops
from users.models import Users

def search_by_name(request):
	if request.method == 'GET':
		shopname = request.GET.get('shopname', None)

		try:
			user = Users.objects.get(pk=request.user)

			users=Users.objects.filter(created_by_user=user)
			my_users=[]
			my_users.extend(users)
			my_users.append(user)

			shop = Shops.objects.get(name=shopname, created_by_user__in=my_users)
			return JsonResponse({'status': 'success', 'exist': True, 'dropped': shop.dropped, 'shop': shop.id})
		except ObjectDoesNotExist:
			msg = _('The object does not exist')
			return JsonResponse({'status': 'error', 'exist': False, 'msg': msg})

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})