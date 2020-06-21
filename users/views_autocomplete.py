from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q

from django.http import HttpResponse#, JsonResponse
import json

from .models import Users

def users_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		users = User.objects.filter(email__icontains=query)
		results = []

		for user in users:
			label = user.first_name + ' ' + user.last_name
			label += ' [email=' + user.email + ']'
			results.append(label)

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)

def my_users_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		users = User.objects.filter(email__icontains=query)
		results = []

		for user in users:
			try:
				# my_user = Users.objects.get(pk=user.id)
				my_user = Users.objects.get(pk=user.id,created_by_user=request.user)
				label = user.first_name + ' ' + user.last_name
				label += ' [email=' + user.email + ']'
				results.append(label)
			except ObjectDoesNotExist:
				pass

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)

def my_users_analytics_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		even_me=[]
		me=Users.objects.get(pk=request.user)
		my_users=Users.objects.filter(created_by_user=me)
		even_me.extend(my_users)
		even_me.append(me)

		users=Users.objects.filter(email__icontains=query,created_by_user__in=even_me)
		results=[]

		label = me.first_name + ' ' + me.last_name
		label += ' [email=' + me.email + ']'
		results.append(label)

		for user in users:
			try:
				# my_user = Users.objects.get(pk=user.id)
				label = user.first_name + ' ' + user.last_name
				label += ' [email=' + user.email + ']'
				results.append(label)
			except ObjectDoesNotExist:
				pass

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)

def users_shop_admins_autocomplete(request):
	if not request.user.is_authenticated:
		return User.objects.none()

	results = []

	if request.is_ajax():
		term = request.GET.get('term', '')

		from shops.models import Shops

		try:
			# We only must to show the rows where the current user
			# is the show "owner" (at least who created the shop)
			shops = Shops.objects.filter(created_by_user=request.user)

			for shop in shops:
				query = \
					Q(id=shop.admin_id) & \
					Q(email__icontains=term)

				users = User.objects.filter(query)

				for user in users:
					label = user.first_name + ' ' + user.last_name
					label += ' [email=' + user.email + ']'
					if label not in results:
						results.append(label)
		except ObjectDoesNotExist:
			return redirect('/')

	data = json.dumps(results)
	mimetype = "application/json"
	return HttpResponse(data, mimetype)

def users_store_admins_autocomplete(request):
	if not request.user.is_authenticated:
		return User.objects.none()

	results = []

	if request.is_ajax():
		term = request.GET.get('term', '')

		from stores.models import Stores

		try:
			# We only must to show the rows where the current user
			# is the "owner" (at least who created the record)
			stores = Stores.objects.filter(created_by_user=request.user)

			for store in stores:
				query = \
					Q(pk=store.admin_id) & \
					Q(email__icontains=term)

				users = User.objects.filter(query)

				for user in users:
					label = user.first_name + ' ' + user.last_name
					label += ' [email=' + user.email + ']'
					if label not in results:
						results.append(label)
		except ObjectDoesNotExist:
			return redirect('/')

	# Trying with JsonResponse() results in:
	# In order to allow non-dict objects to be serialized set the safe parameter to False.
	#return JsonResponse(results)

	data = json.dumps(results)
	mimetype = "application/json"
	return HttpResponse(data, mimetype)