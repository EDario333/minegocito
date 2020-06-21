from django.http import HttpResponse#, JsonResponse

from .models import Brands

from users.models import Users

import json

def my_brands_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		user = Users.objects.get(pk=request.user)
		brands = Brands.objects.filter(name__icontains=query, created_by_user=user, dropped=False)
		results = []

		for brand in brands:
			results.append(brand.name)

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)