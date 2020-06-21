from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q

from django.http import HttpResponse, JsonResponse

from django.utils.translation import gettext as _

from users.models import Users

import json

def my_shops_autocomplete(request):
	if not request.user.is_authenticated:
		return User.objects.none()

	results = []

	if request.is_ajax():
		term = request.GET.get('term', '')

		from shops.models import Shops

		try:
			user = Users.objects.get(pk=request.user)

			users=Users.objects.filter(created_by_user=user)
			my_users=[]
			my_users.extend(users)
			my_users.append(user)

			shops = Shops.objects.filter(created_by_user__in=my_users, name__icontains=term, dropped=False)

			# This will add also the objects created by users
			# that I've created

			for shop in shops:
				label = shop.name + ' [' + _('City') + '='
				label += shop.city.display_name + '; '
				label += _('Address line 1') + '='
				label += shop.address_line1 + '; '
				label += _('Admin') + '='
				label += shop.admin.first_name + ' '
				label += shop.admin.last_name + ' ('
				label += shop.admin.email + ')]'
				if label not in results:
					results.append(label)
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': _('There are not records matching your query')})

	#return JsonResponse(results)

	data = json.dumps(results)
	mimetype = "application/json"
	return HttpResponse(data, mimetype)