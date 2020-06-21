from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from purchases.models import Purchases, \
PurchasesDetails, PurchasesProductsDetails

from datetime import datetime, timedelta

from providers.models import Providers

from users.models import Users

#from stores.models import Stores
from shops.models import Shops

from products.models import Products

from brands.models import Brands

import dateutil.parser

import json

# https://www.chartjs.org/samples/latest/scales/time/financial.html
# view-source:https://www.chartjs.org/samples/latest/scales/time/financial.html
dummy=_('Please select at least one user')
dummy=_('Please select at least one provider')

def __purchases_of_the_day__(request, itm_menu):
	try:
		today=datetime.today()
		purchases=Purchases.objects.filter(purchased_when=today,dropped=False).order_by('purchased_at')

		if len(purchases) < 1:
			msg=_('There are not any purchase today')
			html_='<p class="label label-default">'
			html_+=msg + '</p> '
			html='$("#secPurchasesOfTheDay").html(\''+html_+'\');'
			html+='$("#secPurchasesOfTheDay").parent().css("height", "375.6px");'
			html+='$("#secPurchasesOfTheDay #purchases_of_the_day").remove();'
			# html+='$("#menuSalesOfTheDay").hide();'
			return html

		my_users=[]
		user=Users.objects.get(pk=request.user)
		users=Users.objects.filter(created_by_user=user)
		my_users.extend(users)
		my_users.append(user)

		shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
		products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
		brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)

		purchases_id_array=[]
		purchases_array=[]
		stores_id_array=[]
		stores_array=[]

		details='<div class="table-responsive">'
		details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
		details+=_('Purchase ID')
		details+='</th><th>'
		details+=_('Purchased when')
		details+='</th><th>'
		details+=_('Purchased at')
		details+='</th><th>'
		details+=_('Options')
		details+='</th></tr></thead><tbody>'

		for purchase in purchases:
			if purchase.id not in purchases_id_array:
				pds=PurchasesDetails.objects.filter(purchase=purchase)
				# print('********pds*********')
				# print(pds)

				for pd in pds:
					product=pd.product
					# print('*****product*******')
					# print(product)

					# distinct not supported by SQLite. Error:
					# django.db.utils.NotSupportedError: DISTINCT
					# on fields is not supported by this database
					# backend
					# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
					ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)
					# print('*****ppds*******')
					# print(ppds)

					for ppd in ppds:
						if ppd.in_store.id not in stores_id_array:
							stores_array.append(ppd.in_store)
							stores_id_array.append(ppd.in_store.id)

					for store in stores_array:
						# store=ppd.in_store
						# print('*****store*******')
						# print(store)
						shop=store.shop
						# print('*****shop*******')
						# print(shop)

						if shop in shops and \
						product in products and \
						pd.brand in brands and \
						purchase.id not in purchases_id_array:
							purchases_array.append(purchase)
							purchases_id_array.append(purchase.id)
							details+='<tr><td>'
							details+=purchase.identifier+'</td><td>'
							details+=purchase.purchased_when_fmt_mx+'</td><td>'
							details+=str(purchase.purchased_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetailsPurchasesAnalytics(' + str(purchase.id)
							details+=', itm_menu);'
							details+=' return false;">'
							# details+='onclick="alert(tst);">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

		if len(purchases_array) < 1:
			msg=_('There are not any purchase matching with your query options')
			html_='<p class="label label-default">'
			html_+=msg + '</p> '
			html='<script type="text/javascript">$("#secPurchasesByRange #msg").html(\''+html_+'\');'
			# html+='$("#menuSalesByRange").hide();'
			html+='$("#secPurchasesByRange #purchases_by_range").hide();'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

		details += '</table></div>'

		# data='<script type="text/javascript"> '
		data='var itm_menu = "' + itm_menu + '"; '
		data+='var module = "purchases"; '

		data+='var data = ['

		for purchase in purchases:
			data+='{t: new Date('
			data+=str(today.year)+','+str(today.month)+','+str(today.day)
			data+=','+str(purchase.purchased_at.hour)+','
			data+=str(purchase.purchased_at.minute)+','
			data+=str(purchase.purchased_at.second)
			data+='), y: ' + str(purchase.purchased_products_counter) + '},'
		data=data[:len(data)-1]
		data+='];'
	except ObjectDoesNotExist:
		msg=_('There are not any purchase today')
		html='show_msg_with_toastr("warning", "' + msg + '");'
		return html

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_of_the_day").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesOfTheDay #secDetails").html(\''
	html += details
	html += '\');'

	return html

def index(request):
	context={}
	if request.method == 'GET':
		itm_menu=request.GET.get('itm_menu', 'lnk1')
		form = {
			'title': _('Purchases analytics')
		}
		context['form']=form
		context['itm_menu']=itm_menu
		context['purchases_of_the_day_chart']=__purchases_of_the_day__(request, itm_menu)
		return render(request,'analytics/purchases/index.html',context=context)

	context['app_version']=_('Free version')
	context['itm_menu']='lnkHome'
	return render(request,'dashboard/index.html',context=context)

def by_range(request):
	if request.method=='POST':
		starting_when=request.POST.get('starting_when', None)
		starting_when=starting_when[6:]+'-'+starting_when[3:5]+'-'+starting_when[0:2]
		starting_at=request.POST.get('starting_at', None)

		ending_when=request.POST.get('ending_when', None)
		ending_when=ending_when[6:]+'-'+ending_when[3:5]+'-'+ending_when[0:2]
		ending_at=request.POST.get('ending_at', None)

		itm_menu=request.POST.get('itm_menu', 'lnk1')

		shops=request.POST.get('shops', None)
		shops = json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.POST.get('products', None)
		products = json.loads(products)

		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.POST.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		users=request.POST.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		providers=request.POST.get('providers', None)
		providers=json.loads(providers)
		providers=Providers.objects.filter(dropped=False, pk__in=providers)

		try:
			# sales=Sales.objects.filter(sold_when__range=(starting_when, ending_when), sold_at__range=(starting_at, ending_at), dropped=False).order_by('sold_at')
			starts=dateutil.parser.parse(starting_when+' '+starting_at)
			ends=dateutil.parser.parse(ending_when+' '+ending_at)

			purchases=Purchases.objects.filter(purchased_date__range=(starts, ends), dropped=False, provider__in=providers,created_by_user__in=users).order_by('purchased_date')
			#sales=Sales.objects.filter(sold_when__range=(starting_when, ending_when), dropped=False)
			# sales=sales.filter(sold_at__range=(starting_at, ending_at)).order_by('sold_at')
			# print('*********sales******')
			# print(sales)

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByRange #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByRange").hide();'
				html+='$("#secPurchasesByRange #purchases_by_range").hide();'
				html+='$("#secPurchasesByRange #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase)
					# print('********pds*********')
					# print(pds)

					for pd in pds:
						product=pd.product
						# print('*****product*******')
						# print(product)

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)
						# print('*****ppds*******')
						# print(ppds)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							# store=ppd.in_store
							# print('*****store*******')
							# print(store)
							shop=store.shop
							# print('*****shop*******')
							# print(shop)

							if shop in shops and \
							product in products and \
							pd.brand in brands and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								# details+='onclick="alert(tst);">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByRange #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByRange").hide();'
				html+='$("#secPurchasesByRange #purchases_by_range").hide();'
				html+='$("#secPurchasesByRange #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_range").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByRange #purchases_by_range").show();'
	html += '$("#secPurchasesByRange #msg").empty();'
	html += '$("#secPurchasesByRange #secDetails").html(\''
	html += details
	html += '\');'
	# html += '$("#menuSalesByRange").show();'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	# return html
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def by_provider(request):
	if request.method=='POST':
		provider=request.POST.get('provider_obj', None)

		shops=request.POST.get('shops', None)
		shops=json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.POST.get('products', None)
		products=json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.POST.get('brands', None)
		brands=json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		users=request.POST.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		itm_menu=request.POST.get('itm_menu', 'lnk1')

		try:
			provider=Providers.objects.get(pk=provider)
		except ObjectDoesNotExist:
			msg=_('The specified provider does not exists')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("error", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

		try:
			purchases=Purchases.objects.filter(provider=provider, dropped=False, created_by_user__in=users).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByProviders #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByproviders").hide();'
				html+='$("#secPurchasesByProviders #purchases_by_providers").hide();'
				html+='$("#secPurchasesByProviders #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase)

					for pd in pds:
						product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							shop=store.shop

							if shop in shops and \
							product in products and \
							pd.brand in brands and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								# details+='onclick="alert(tst);">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByProviders #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByproviders").hide();'
				html+='$("#secPurchasesByProviders #purchases_by_providers").hide();'
				html+='$("#secPurchasesByProviders #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_providers").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByProviders #purchases_by_providers").show();'
	html += '$("#secPurchasesByProviders #msg").empty();'
	html += '$("#secPurchasesByProviders #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def all_providers(request):
	if request.method=='GET':
		shops=request.GET.get('shops', None)
		shops=json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.GET.get('products', None)
		products=json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.GET.get('brands', None)
		brands=json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		users=request.GET.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			purchases=Purchases.objects.filter(dropped=False, created_by_user__in=users).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByProviders #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByproviders").hide();'
				html+='$("#secPurchasesByProviders #purchases_by_providers").hide();'
				html+='$("#secPurchasesByProviders #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase)

					for pd in pds:
						product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							shop=store.shop

							if shop in shops and \
							product in products and \
							pd.brand in brands and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								# details+='onclick="alert(tst);">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByProviders #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByproviders").hide();'
				html+='$("#secPurchasesByProviders #purchases_by_providers").hide();'
				html+='$("#secPurchasesByProviders #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_providers").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByProviders #purchases_by_providers").show();'
	html += '$("#secPurchasesByProviders #msg").empty();'
	html += '$("#secPurchasesByProviders #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def by_user(request):
	if request.method=='POST':
		user=request.POST.get('user_obj', None)
		itm_menu=request.POST.get('itm_menu', 'lnk1')

		try:
			user=Users.objects.get(pk=user)
		except ObjectDoesNotExist:
			msg=_('The specified user does not exists')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("error", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

		shops=request.POST.get('shops', None)
		shops=json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.POST.get('products', None)
		products=json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.POST.get('brands', None)
		brands=json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		providers=request.POST.get('providers', None)
		providers=json.loads(providers)
		providers=Providers.objects.filter(dropped=False, pk__in=providers)

		try:
			purchases=Purchases.objects.filter(created_by_user=user, dropped=False, provider__in=providers).order_by('purchased_date')

			if len(purchases)<1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByUsers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secPurchasesByUsers #purchases_by_users").hide();'
				html+='$("#secPurchasesByUsers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase)

					for pd in pds:
						product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							shop=store.shop

							if shop in shops and \
							product in products and \
							pd.brand in brands and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								# details+='onclick="alert(tst);">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByUsers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secPurchasesByUsers #purchases_by_users").hide();'
				html+='$("#secPurchasesByUsers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_users").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByUsers #purchases_by_users").show();'
	html += '$("#secPurchasesByUsers #msg").empty();'
	html += '$("#secPurchasesByUsers #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def all_users(request):
	if request.method=='GET':
		shops=request.GET.get('shops', None)
		shops=json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.GET.get('products', None)
		products=json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.GET.get('brands', None)
		brands=json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		providers=request.GET.get('providers', None)
		providers=json.loads(providers)
		providers=Providers.objects.filter(dropped=False, pk__in=providers)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			purchases=Purchases.objects.filter(dropped=False, provider__in=providers).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByUsers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secPurchasesByUsers #purchases_by_users").hide();'
				html+='$("#secPurchasesByUsers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase)

					for pd in pds:
						product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							shop=store.shop

							if shop in shops and \
							product in products and \
							pd.brand in brands and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								# details+='onclick="alert(tst);">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByUsers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secPurchasesByUsers #purchases_by_users").hide();'
				html+='$("#secPurchasesByUsers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_users").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByUsers #purchases_by_users").show();'
	html += '$("#secPurchasesByUsers #msg").empty();'
	html += '$("#secPurchasesByUsers #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def by_product(request):
	if request.method=='POST':
		product=request.POST.get('product_obj', None)

		shops=request.POST.get('shops', None)
		shops = json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		# products=request.POST.get('products', None)
		# products = json.loads(products)
		# products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.POST.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		users=request.POST.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		providers=request.POST.get('providers', None)
		providers=json.loads(providers)
		providers=Providers.objects.filter(dropped=False, pk__in=providers)

		itm_menu=request.POST.get('itm_menu', 'lnk1')

		try:
			product=Products.objects.get(pk=product)
		except ObjectDoesNotExist:
			msg=_('The specified product does not exists')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("error", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

		try:
			purchases=Purchases.objects.filter(dropped=False,provider__in=providers,created_by_user__in=users).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByProducts #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByProducts #purchases_by_products").hide();'
				html+='$("#secPurchasesByProducts #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase,product=product)

					for pd in pds:
						# product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							shop=store.shop

							if shop in shops and \
							pd.brand in brands and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByProducts #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByProducts #purchases_by_products").hide();'
				html+='$("#secPurchasesByProducts #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_products").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByProducts #purchases_by_products").show();'
	html += '$("#secPurchasesByProducts #msg").empty();'
	html += '$("#secPurchasesByProducts #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def all_products(request):
	if request.method=='GET':
		shops=request.GET.get('shops', None)
		shops = json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.GET.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.GET.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		users=request.GET.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		providers=request.GET.get('providers', None)
		providers=json.loads(providers)
		providers=Providers.objects.filter(dropped=False, pk__in=providers)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			purchases=Purchases.objects.filter(dropped=False,provider__in=providers,created_by_user__in=users).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByProducts #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByProducts #purchases_by_products").hide();'
				html+='$("#secPurchasesByProducts #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase, product__in=products)

					for pd in pds:
						product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							shop=store.shop

							if shop in shops and \
							pd.brand in brands and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByProducts #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByProducts #purchases_by_products").hide();'
				html+='$("#secPurchasesByProducts #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_products").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByProducts #purchases_by_products").show();'
	html += '$("#secPurchasesByProducts #msg").empty();'
	html += '$("#secPurchasesByProducts #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def by_brand(request):
	if request.method=='POST':
		brand=request.POST.get('brand_obj', None)

		shops=request.POST.get('shops', None)
		shops = json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.POST.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		# brands=request.POST.get('brands', None)
		# brands = json.loads(brands)
		# brands=Brands.objects.filter(dropped=False, pk__in=brands)

		users=request.POST.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		providers=request.POST.get('providers', None)
		providers=json.loads(providers)
		providers=Providers.objects.filter(dropped=False, pk__in=providers)

		itm_menu=request.POST.get('itm_menu', 'lnk1')

		try:
			brand=Brands.objects.get(pk=brand)
		except ObjectDoesNotExist:
			msg=_('The specified brand does not exists')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("error", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

		try:
			purchases=Purchases.objects.filter(dropped=False,provider__in=providers,created_by_user__in=users).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByBrands #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByBrands #purchases_by_brands").hide();'
				html+='$("#secPurchasesByBrands #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase,brand=brand,product__in=products)

					for pd in pds:
						# product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							shop=store.shop

							if shop in shops and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByBrands #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByBrands #purchases_by_brands").hide();'
				html+='$("#secPurchasesByBrands #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_brands").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByBrands #purchases_by_brands").show();'
	html += '$("#secPurchasesByBrands #msg").empty();'
	html += '$("#secPurchasesByBrands #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def all_brands(request):
	if request.method=='GET':
		shops=request.GET.get('shops', None)
		shops=json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.GET.get('products', None)
		products=json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.GET.get('brands', None)
		brands=json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		users=request.GET.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		providers=request.GET.get('providers', None)
		providers=json.loads(providers)
		providers=Providers.objects.filter(dropped=False, pk__in=providers)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			purchases=Purchases.objects.filter(dropped=False,provider__in=providers,created_by_user__in=users).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByBrands #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByBrands #purchases_by_brands").hide();'
				html+='$("#secPurchasesByBrands #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase, brand__in=brands)

					for pd in pds:
						product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							shop=store.shop

							if shop in shops and \
							product in products and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByBrands #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByBrands #purchases_by_brands").hide();'
				html+='$("#secPurchasesByBrands #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_brands").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByBrands #purchases_by_brands").show();'
	html += '$("#secPurchasesByBrands #msg").empty();'
	html += '$("#secPurchasesByBrands #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def by_shop(request):
	if request.method=='POST':
		shop=request.POST.get('shop_obj', None)

		# shops=request.POST.get('shops', None)
		# shops = json.loads(shops)
		# shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.POST.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.POST.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		users=request.POST.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		providers=request.POST.get('providers', None)
		providers=json.loads(providers)
		providers=Providers.objects.filter(dropped=False, pk__in=providers)

		itm_menu=request.POST.get('itm_menu', 'lnk1')

		try:
			shop=Shops.objects.get(pk=shop)
		except ObjectDoesNotExist:
			msg=_('The specified shop does not exists')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("error", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

		try:
			purchases=Purchases.objects.filter(dropped=False,provider__in=providers,created_by_user__in=users).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByShops #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByShops #purchases_by_shops").hide();'
				html+='$("#secPurchasesByShops #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase, product__in=products)

					for pd in pds:
						# product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array and \
							ppd.in_store.shop.id == shop.id:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							# shop_=store.shop

							if pd.brand in brands and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByShops #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByShops #purchases_by_shops").hide();'
				html+='$("#secPurchasesByShops #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_shops").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByShops #purchases_by_shops").show();'
	html += '$("#secPurchasesByShops #msg").empty();'
	html += '$("#secPurchasesByShops #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def all_shops(request):
	if request.method=='GET':
		shops=request.GET.get('shops', None)
		shops = json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.GET.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.GET.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		users=request.GET.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		providers=request.GET.get('providers', None)
		providers=json.loads(providers)
		providers=Providers.objects.filter(dropped=False, pk__in=providers)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			purchases=Purchases.objects.filter(dropped=False,provider__in=providers,created_by_user__in=users).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByShops #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByShops #purchases_by_shops").hide();'
				html+='$("#secPurchasesByShops #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Purchase ID')
			details+='</th><th>'
			details+=_('Purchased when')
			details+='</th><th>'
			details+=_('Purchased at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for purchase in purchases:
				if purchase.id not in purchases_id_array:
					pds=PurchasesDetails.objects.filter(purchase=purchase)

					for pd in pds:
						product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array and \
							ppd.in_store.shop in shops:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							# shop=store.shop

							# if shop in shops and \
							if product in products and \
							pd.brand in brands and \
							purchase.id not in purchases_id_array:
								purchases_array.append(purchase)
								purchases_id_array.append(purchase.id)
								details+='<tr><td>'
								details+=purchase.identifier+'</td><td>'
								details+=purchase.purchased_when_fmt_mx+'</td><td>'
								details+=str(purchase.purchased_at)+'</td><td>'
								details+='<a href="#" data-placement="bottom" '
								details+='data-toggle="tooltip" '
								details+='title="' + _('Details') + '" '
								details+='data-original-title="' + _('Details') + '" '
								details+='onclick="showDetails(' + str(purchase.id)
								details+=', module, false, false, false, false, itm_menu);'
								details+=' return false;">'
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secPurchasesByShops #msg").html(\''+html_+'\');'
				html+='$("#secPurchasesByShops #purchases_by_shops").hide();'
				html+='$("#secPurchasesByShops #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			for purchase in purchases_array:
				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(purchase.purchased_products_counter) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

	ds_lbl=_('Purchased products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("purchases_by_shops").getContext("2d");'

	html += 'var color = Chart.helpers.color;'
	html += 'var cfg = {'
	html += 	'type: "bar",'
	html += 	'data: {'
	html += 		'datasets: [{'
	html += 			'label: "' + ds_lbl + '",'
	html +=				'backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),'
	html +=				'borderColor: window.chartColors.blue,'
	html +=				'data: data,'
	html +=				'type: "line",'
	html +=				'pointRadius: 3,'
	html +=				'fill: false,'
	html +=				'lineTension: 0,'
	html +=				'borderWidth: 2'
	html +=			'}]'
	html +=		'},'

	html +=		'options: {'
	html +=			'scales: {'
	html +=				'xAxes: [{'
	html +=					'type: "time",'
	html +=					'distribution: "series",'
	html +=					'ticks: {'
	html +=						'source: "data",'
	html +=						'autoSkip: true'
	html +=					'},'
	html +=					'time: {'
	html +=						'unit: "minute"'
	html +=					'}'
	html +=				'}],'
	
	html +=				'yAxes: [{'
	html +=					'scaleLabel: {'
	html +=						'display: true,'
	html +=						'labelString: "' + _('Sold products amount') + '"'
	html +=					'}'
	html +=				'}]'
	html +=			'},'

	html +=			'tooltips: {'
	html +=				'intersect: false,'
	html +=				'mode: "index",'
	html +=				'callbacks: {'
	html +=					'label: function(tooltipItem, myData) {'
	html +=						'var label = myData.datasets[tooltipItem.datasetIndex].label || "";'
	html +=						'if (label) {'
	html +=							'label += ": ";'
	html +=						'}'
	html +=						'label += parseInt(tooltipItem.value);'
	html +=						'return label;'
	html +=					'}'
	html +=				'}'
	html +=			'}'
	html +=		'}'
	html +=	'};'

	html +=	'var chart = new Chart(ctx, cfg);'

	html += '$("#secPurchasesByShops #purchases_by_shops").show();'
	html += '$("#secPurchasesByShops #msg").empty();'
	html += '$("#secPurchasesByShops #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def advanced_cfg_by_range(request):
	context={}
	if request.method == 'GET':
		try:
			my_users=[]
			user=Users.objects.get(pk=request.user)
			users=Users.objects.filter(created_by_user=user)
			my_users.extend(users)
			my_users.append(user)

			shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)
			providers=Providers.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['users']=my_users
			context['providers']=providers

			return render(request,'analytics/purchases/advanced-cfg-by-range.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def advanced_cfg_by_providers(request):
	context={}
	if request.method == 'GET':
		try:
			my_users=[]
			user=Users.objects.get(pk=request.user)
			users=Users.objects.filter(created_by_user=user)
			my_users.extend(users)
			my_users.append(user)

			shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['users']=my_users

			return render(request,'analytics/purchases/advanced-cfg-by-providers.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def advanced_cfg_by_users(request):
	context={}
	if request.method == 'GET':
		try:
			my_users=[]
			user=Users.objects.get(pk=request.user)
			users=Users.objects.filter(created_by_user=user)
			my_users.extend(users)
			my_users.append(user)

			shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)
			providers=Providers.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['providers']=providers

			return render(request,'analytics/purchases/advanced-cfg-by-users.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def advanced_cfg_by_products(request):
	context={}
	if request.method == 'GET':
		try:
			my_users=[]
			user=Users.objects.get(pk=request.user)
			users=Users.objects.filter(created_by_user=user)
			my_users.extend(users)
			my_users.append(user)

			shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)
			providers=Providers.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['users']=my_users
			context['providers']=providers

			return render(request,'analytics/purchases/advanced-cfg-by-products.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def advanced_cfg_by_brands(request):
	context={}
	if request.method == 'GET':
		try:
			my_users=[]
			user=Users.objects.get(pk=request.user)
			users=Users.objects.filter(created_by_user=user)
			my_users.extend(users)
			my_users.append(user)

			shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)
			providers=Providers.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['users']=my_users
			context['providers']=providers

			return render(request,'analytics/purchases/advanced-cfg-by-brands.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def advanced_cfg_by_shops(request):
	context={}
	if request.method == 'GET':
		try:
			my_users=[]
			user=Users.objects.get(pk=request.user)
			users=Users.objects.filter(created_by_user=user)
			my_users.extend(users)
			my_users.append(user)

			shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)
			providers=Providers.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['users']=my_users
			context['providers']=providers

			return render(request,'analytics/purchases/advanced-cfg-by-shops.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})