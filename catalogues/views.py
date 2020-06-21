from django.shortcuts import render

from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse
import json

from .models import City

def cities_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		cities = City.objects.filter(name__icontains=query)
		results = []
		for city in cities:
			place_json = city.display_name
			results.append(place_json)

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)

def search_city_by_name(request):
	if request.is_ajax():
		query = request.GET.get('name', '')
		#query = query.replace('+', ' ')

		result = {}

		try:
			city = City.objects.get(display_name__iexact=query)
			result['exist'] = True
			result['city'] = city.id
		except ObjectDoesNotExist:
			result['exist'] = False

		data = json.dumps(result)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)