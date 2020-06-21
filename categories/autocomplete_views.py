from django.http import HttpResponse#, JsonResponse

#from django.contrib.auth.models import ContentType

from taggit.models import Tag

from django.utils.translation import gettext as _

#from users.models import Users

from shops.models import Shops
#from brands.models import Brands

import json

def shops_categories_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		#categories = Tag.objects.filter(name__icontains=query).exclude(brands__in=Brands.objects.all())
		categories = Tag.objects.filter(name__icontains=query)
		results = []

		for category in categories:
			results.append(category.name)

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)