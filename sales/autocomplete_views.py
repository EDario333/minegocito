from django.http import HttpResponse

from django.core.exceptions import ObjectDoesNotExist

from products.models import Products
from purchases.models import PurchasesProductsDetails
from users.models import Users

import json

def my_sales_query_product_autocomplete(request):
	if request.is_ajax():
		query = request.GET.get('term', '')

		user = Users.objects.get(pk=request.user)
		results = []

		# First search and add all the SKUs matching...
		ppds=PurchasesProductsDetails.objects.filter(sku__icontains=query,created_by_user=user,dropped=False,stored=True)

		for ppd in ppds:
			results.append(ppd.purchase_detail.product.name)

		# Now search and add all the products name matching...
		products = Products.objects.filter(name__icontains=query,created_by_user=user,dropped=False)

		for product in products:
			results.append(product.name)

		data = json.dumps(results)

	mimetype = "application/json"

	return HttpResponse(data, mimetype)