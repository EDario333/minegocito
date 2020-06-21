from django.http import HttpResponse#, JsonResponse

from .models import Products

from users.models import Users

import json

def my_products_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		user = Users.objects.get(pk=request.user)
		products = Products.objects.filter(name__icontains=query, created_by_user=user, dropped=False)
		results = []

		for product in products:
			results.append(product.name)

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)