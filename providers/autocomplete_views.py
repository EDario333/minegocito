from django.http import HttpResponse#, JsonResponse

from django.db.models import Q

from django.utils.translation import gettext as _

from .models import Providers

from users.models import Users

import json

def my_providers_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		user = Users.objects.get(pk=request.user)
		query = \
			Q(created_by_user=user) & Q(dropped=False) & \
			(Q(name__icontains=query) | \
			Q(rfc__icontains=query))

		providers = Providers.objects.filter(query)

		results = []

		for provider in providers:
			lbl=provider.name+' [' + _('RFC') + '='+provider.rfc+']'
			results.append(lbl)

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)