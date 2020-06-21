from django.http import HttpResponse#, JsonResponse

from django.db.models import Q

from django.utils.translation import gettext as _

from .models import Customers

from users.models import Users

import json

def my_customers_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		user = Users.objects.get(pk=request.user)
		query = \
			Q(created_by_user=user) & Q(dropped=False) & \
			Q(first_name__icontains=query) | \
			Q(middle_name__icontains=query) | \
			Q(last_name__icontains=query) | \
			Q(mothers_last_name__icontains=query) | \
			Q(rfc__icontains=query)

		customers = Customers.objects.filter(query)

		results = []

		for customer in customers:
			lbl=customer.full_name+' [' + _('RFC') + '='+customer.rfc+']'
			results.append(lbl)

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)