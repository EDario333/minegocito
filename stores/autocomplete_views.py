from django.http import HttpResponse#, JsonResponse

from django.utils.translation import gettext as _

from .models import Stores

from users.models import Users

import json

def my_stores_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		user = Users.objects.get(pk=request.user)

		# Add next lines to all the autocomplete
		# This will add also the objects created by users
		# that I've created
		users=Users.objects.filter(created_by_user=user)
		my_users=[]
		my_users.extend(users)
		my_users.append(user)
		# Ends

		# Also ensure that created_by_user=user
		# will be changed by created_by_user__in=my_users
		stores = Stores.objects.filter(name__icontains=query, created_by_user__in=my_users, dropped=False)
		results = []

		for store in stores:
			label = store.name + ' [' + _('Belongs to shop')
			label += '=' + store.shop.name 
			label += '; ' + _('User admin') + '='
			'''
			label += store.created_by_user.first_name + ' '
			label += store.created_by_user.last_name + ' ('
			label += store.created_by_user.email + ')]'
			'''
			label += store.admin.first_name + ' '
			label += store.admin.last_name + ' ('
			label += store.admin.email + ')]'
			results.append(label)

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)