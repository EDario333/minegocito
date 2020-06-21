from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from purchases.models import Purchases, \
PurchasesDetails, PurchasesProductsDetails

from datetime import datetime, timedelta

from products.models import Products

from users.models import Users

from stores.models import Stores
from shops.models import Shops

from products.models import Products

from brands.models import Brands

import dateutil.parser

import json

# https://www.chartjs.org/samples/latest/scales/time/financial.html
# view-source:https://www.chartjs.org/samples/latest/scales/time/financial.html

def __products_stored_today__(request,itm_menu):
	try:
		today=datetime.today()
		purchases=Purchases.objects.filter(purchased_when=today,dropped=False).order_by('purchased_at')

		if len(purchases) < 1:
			msg=_('There are not any product stored today')
			html_='<p class="label label-default">'
			html_+=msg + '</p> '
			html='$("#secProductsStoredToday").html(\''+html_+'\');'
			html+='$("#secProductsStoredToday").parent().css("height", "375.6px");'
			html+='$("#secProductsStoredToday #products_stored_today").remove();'
			# html+='$("#menuSalesOfTheDay").hide();'
			return html

		purchases_id_array=[]
		purchases_array=[]
		stores_id_array=[]
		stores_array=[]

		my_users=[]
		user=Users.objects.get(pk=request.user)
		users=Users.objects.filter(created_by_user=user)
		my_users.extend(users)
		my_users.append(user)

		# shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
		stores=Stores.objects.filter(dropped=False,created_by_user__in=my_users)
		products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
		brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)

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
					# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True).distinct('in_store')
					ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True)

					for ppd in ppds:
						if ppd.in_store.id not in stores_id_array and \
						ppd.in_store in stores:
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
							details+='onclick="showDetailsPurchasesAnalytics(' + str(purchase.id)
							details+=', itm_menu);'
							details+=' return false;">'
							# details+='onclick="alert(tst);">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any product stored today')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByRange #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByRange").hide();'
				html+='$("#secProductsStoresByRange #products_stored_by_range").hide();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			# data='<script type="text/javascript"> '
			data='var itm_menu = "' + itm_menu + '"; '
			# data+='var module = "purchases"; '
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
		msg=_('There are not any product stored today')
		html='show_msg_with_toastr("warning", "' + msg + '");'
		return html

	ds_lbl=_('Products stored amount')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("products_stored_today").getContext("2d");'

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
	html +=						'labelString: "' + _('Products stored amount') + '"'
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

	html += '$("#secProductsStoredToday #secDetails").html(\''
	html += details
	html += '\');'

	return html

def index(request):
	context={}
	if request.method == 'GET':
		itm_menu=request.GET.get('itm_menu', 'lnk1')
		form = {
			'title': _('Products stored analytics')
		}
		context['form']=form
		context['itm_menu']=itm_menu
		context['products_stored_today_chart']=__products_stored_today__(request, itm_menu)
		return render(request,'analytics/products-stores/index.html',context=context)

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

		# shops=request.POST.get('shops', None)
		# shops = json.loads(shops)
		# shops=Shops.objects.filter(dropped=False, pk__in=shops)
		stores=request.POST.get('stores', None)
		stores=json.loads(stores)
		stores=Stores.objects.filter(dropped=False, pk__in=stores)

		products=request.POST.get('products', None)
		products = json.loads(products)

		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.POST.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		try:
			# sales=Sales.objects.filter(sold_when__range=(starting_when, ending_when), sold_at__range=(starting_at, ending_at), dropped=False).order_by('sold_at')
			starts=dateutil.parser.parse(starting_when+' '+starting_at)
			ends=dateutil.parser.parse(ending_when+' '+ending_at)

			purchases=Purchases.objects.filter(purchased_date__range=(starts, ends), dropped=False).order_by('purchased_date')
			#sales=Sales.objects.filter(sold_when__range=(starting_when, ending_when), dropped=False)
			# sales=sales.filter(sold_at__range=(starting_at, ending_at)).order_by('sold_at')
			# print('*********sales******')
			# print(sales)

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByRange #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByRange #products_stored_by_range").hide();'
				html+='$("#secProductsStoresByRange #secDetails").empty();'
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
					# print('********pds*********')
					# print(pds)

					for pd in pds:
						product=pd.product
						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							# shop=store.shop

							# if shop in shops and \
							if store in stores and \
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
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByRange #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByRange #products_stored_by_range").hide();'
				html+='$("#secProductsStoresByRange #secDetails").empty();'
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

	ds_lbl=_('Products stored amount')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("products_stored_by_range").getContext("2d");'

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
	html +=						'labelString: "' + _('Products stored amount') + '"'
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

	html += '$("#secProductsStoresByRange #products_stored_by_range").show();'
	html += '$("#secProductsStoresByRange #msg").empty();'
	html += '$("#secProductsStoresByRange #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def by_product(request):
	if request.method=='POST':
		product=request.POST.get('product_obj', None)

		stores=request.POST.get('stores', None)
		stores=json.loads(stores)
		stores=Stores.objects.filter(dropped=False, pk__in=stores)

		# shops=request.POST.get('shops', None)
		# shops = json.loads(shops)
		# shops=Shops.objects.filter(dropped=False, pk__in=shops)

		# products=request.POST.get('products', None)
		# products = json.loads(products)
		# products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.POST.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

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
			purchases=Purchases.objects.filter(dropped=False).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByProducts #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByProducts #products_stored_by_products").hide();'
				html+='$("#secProductsStoresByProducts #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			purchases_id_array=[]
			purchases_array=[]
			stores_id_array=[]
			stores_array=[]
			counters_selected_product=[]

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
						# product_=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True)

						counters_selected_product.append(0)
						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)
							if ppd.purchase_detail.product.id == product.id:
								counters_selected_product[len(counters_selected_product)-1]+=1

						for store in stores_array:
							# shop=store.shop

							# if shop in shops and \
							if store in stores and \
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
				html='<script type="text/javascript">$("#secProductsStoresByProducts #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByProducts #products_stored_by_products").hide();'
				html+='$("#secProductsStoresByProducts #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "purchases"; '
			data+='var data = ['

			x=0
			for purchase in purchases_array:
				# total_amount_products=purchase.purchased_products_counter
				# amount_selected_product=total_amount_products-counter_selected_product
				# print('******total_amount_products******')
				# print(total_amount_products)
				# print('******amount_selected_product*****')
				# print(amount_selected_product)

				purchased_when=purchase.purchased_when
				purchased_at=purchase.purchased_at
				data+='{t: new Date('
				data+=str(purchased_when.year)+','+str(purchased_when.month)+','+str(purchased_when.day)
				data+=','+str(purchased_at.hour)+','
				data+=str(purchased_at.minute)+','
				data+=str(purchased_at.second)
				data+='), y: ' + str(counters_selected_product[x]) + '},'
				x+=1

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any purchase matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

	ds_lbl=_('Products stored amount')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("products_stored_by_products").getContext("2d");'

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
	html +=						'labelString: "' + _('Products stored amount') + '"'
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

	html += '$("#secProductsStoresByProducts #products_stored_by_products").show();'
	html += '$("#secProductsStoresByProducts #msg").empty();'
	html += '$("#secProductsStoresByProducts #secDetails").html(\''
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
		# shops=request.GET.get('shops', None)
		# shops = json.loads(shops)
		# shops=Shops.objects.filter(dropped=False, pk__in=shops)

		stores=request.GET.get('stores', None)
		stores=json.loads(stores)
		stores=Stores.objects.filter(dropped=False, pk__in=stores)

		products=request.GET.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.GET.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			purchases=Purchases.objects.filter(dropped=False).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByProducts #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByProducts #products_stored_by_products").hide();'
				html+='$("#secProductsStoresByProducts #secDetails").empty();'
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
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							# shop=store.shop

							# if shop in shops and \
							if store in stores and \
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
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByProducts #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByProducts #products_stored_by_products").hide();'
				html+='$("#secProductsStoresByProducts #secDetails").empty();'
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

	ds_lbl=_('Products stored amount')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("products_stored_by_products").getContext("2d");'

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
	html +=						'labelString: "' + _('Products stored amount') + '"'
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

	html += '$("#secProductsStoresByProducts #products_stored_by_products").show();'
	html += '$("#secProductsStoresByProducts #msg").empty();'
	html += '$("#secProductsStoresByProducts #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
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

		# shops=request.POST.get('shops', None)
		# shops = json.loads(shops)
		# shops=Shops.objects.filter(dropped=False, pk__in=shops)
		stores=request.POST.get('stores', None)
		stores=json.loads(stores)
		stores=Stores.objects.filter(dropped=False, pk__in=stores)

		products=request.POST.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.POST.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		try:
			purchases=Purchases.objects.filter(created_by_user=user, dropped=False).order_by('purchased_date')

			if len(purchases)<1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByUsers #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByUsers #products_stores_by_users").hide();'
				html+='$("#secProductsStoresByUsers #secDetails").empty();'
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
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							# shop=store.shop

							# if shop in shops and \
							if store in stores and \
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
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByUsers #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByUsers #products_stores_by_users").hide();'
				html+='$("#secProductsStoresByUsers #secDetails").empty();'
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

	ds_lbl=_('Products stored amount')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("products_stores_by_users").getContext("2d");'

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
	html +=						'labelString: "' + _('Products stored amount') + '"'
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

	html += '$("#secProductsStoresByUsers #products_stores_by_users").show();'
	html += '$("#secProductsStoresByUsers #msg").empty();'
	html += '$("#secProductsStoresByUsers #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def all_users(request):
	if request.method=='GET':
		# shops=request.GET.get('shops', None)
		# shops = json.loads(shops)
		# shops=Shops.objects.filter(dropped=False, pk__in=shops)

		stores=request.GET.get('stores', None)
		stores = json.loads(stores)
		stores=Stores.objects.filter(dropped=False, pk__in=stores)

		products=request.GET.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.GET.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			purchases=Purchases.objects.filter(dropped=False).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByUsers #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByUsers #products_stores_by_users").hide();'
				html+='$("#secProductsStoresByUsers #secDetails").empty();'
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
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							# shop=store.shop

							# if shop in shops and \
							if store in stores and \
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
								details+='<i class="material-icons">zoom_in</i>'
								details+='</a></td></tr>'

			if len(purchases_array) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByUsers #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByUsers #products_stores_by_users").hide();'
				html+='$("#secProductsStoresByUsers #secDetails").empty();'
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

	ds_lbl=_('Products stored amount')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("products_stores_by_users").getContext("2d");'

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
	html +=						'labelString: "' + _('Products stored amount') + '"'
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

	html += '$("#secProductsStoresByUsers #products_stores_by_users").show();'
	html += '$("#secProductsStoresByUsers #msg").empty();'
	html += '$("#secProductsStoresByUsers #secDetails").html(\''
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

		# shops=request.POST.get('shops', None)
		# shops = json.loads(shops)
		# shops=Shops.objects.filter(dropped=False, pk__in=shops)
		stores=request.POST.get('stores', None)
		stores = json.loads(stores)
		stores=Stores.objects.filter(dropped=False, pk__in=stores)

		products=request.POST.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		# brands=request.POST.get('brands', None)
		# brands = json.loads(brands)
		# brands=Brands.objects.filter(dropped=False, pk__in=brands)

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
			purchases=Purchases.objects.filter(dropped=False).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByBrands #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByBrands #products_stored_by_brands").hide();'
				html+='$("#secProductsStoresByBrands #secDetails").empty();'
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
					pds=PurchasesDetails.objects.filter(purchase=purchase,brand=brand)

					for pd in pds:
						product=pd.product

						# distinct not supported by SQLite. Error:
						# django.db.utils.NotSupportedError: DISTINCT
						# on fields is not supported by this database
						# backend
						# ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd).distinct('in_store')
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							# shop=store.shop

							# if shop in shops and \
							if store in stores and \
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
				html='<script type="text/javascript">$("#secProductsStoresByBrands #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByBrands #products_stored_by_brands").hide();'
				html+='$("#secProductsStoresByBrands #secDetails").empty();'
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

	ds_lbl=_('Products stored amount')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("products_stored_by_brands").getContext("2d");'

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
	html +=						'labelString: "' + _('Products stored amount') + '"'
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

	html += '$("#secProductsStoresByBrands #products_stored_by_brands").show();'
	html += '$("#secProductsStoresByBrands #msg").empty();'
	html += '$("#secProductsStoresByBrands #secDetails").html(\''
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
		# shops=request.GET.get('shops', None)
		# shops = json.loads(shops)
		# shops=Shops.objects.filter(dropped=False, pk__in=shops)
		stores=request.GET.get('stores', None)
		stores = json.loads(stores)
		stores=Stores.objects.filter(dropped=False, pk__in=stores)

		products=request.GET.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.GET.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			purchases=Purchases.objects.filter(dropped=False).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByBrands #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByBrands #products_stored_by_brands").hide();'
				html+='$("#secProductsStoresByBrands #secDetails").empty();'
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
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							# shop=store.shop

							# if shop in shops and \
							if store in stores and \
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
				html='<script type="text/javascript">$("#secProductsStoresByBrands #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByBrands #products_stored_by_products").hide();'
				html+='$("#secProductsStoresByBrands #secDetails").empty();'
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

	ds_lbl=_('Products stored amount')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("products_stored_by_brands").getContext("2d");'

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
	html +=						'labelString: "' + _('Products stored amount') + '"'
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

	html += '$("#secProductsStoresByBrands #products_stored_by_brands").show();'
	html += '$("#secProductsStoresByBrands #msg").empty();'
	html += '$("#secProductsStoresByBrands #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def by_store(request):
	if request.method=='POST':
		store=request.POST.get('store_obj', None)

		# shops=request.POST.get('shops', None)
		# shops = json.loads(shops)
		# shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.POST.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.POST.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		itm_menu=request.POST.get('itm_menu', 'lnk1')

		try:
			store=Stores.objects.get(pk=store)
		except ObjectDoesNotExist:
			msg=_('The specified store does not exists')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("error", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

		try:
			purchases=Purchases.objects.filter(dropped=False).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByStores #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByStores #products_stored_by_stores").hide(); '
				html+='$("#secProductsStoresByStores #secDetails").empty();'
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
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array and \
							ppd.in_store.id == store.id:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							#shop_=store.shop

							#if shop_.id = shop.id and \
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
				html='<script type="text/javascript">$("#secProductsStoresByStores #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByStores #products_stored_by_stores").hide();'
				html+='$("#secProductsStoresByStores #secDetails").empty();'
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

	ds_lbl=_('Products stored amount')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("products_stored_by_stores").getContext("2d");'

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
	html +=						'labelString: "' + _('Products stored amount') + '"'
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

	html += '$("#secProductsStoresByStores #products_stored_by_stores").show();'
	html += '$("#secProductsStoresByStores #msg").empty();'
	html += '$("#secProductsStoresByStores #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def all_stores(request):
	if request.method=='GET':
		stores=request.GET.get('stores', None)
		stores=json.loads(stores)
		stores=Stores.objects.filter(dropped=False, pk__in=stores)

		products=request.GET.get('products', None)
		products = json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.GET.get('brands', None)
		brands = json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			purchases=Purchases.objects.filter(dropped=False).order_by('purchased_date')

			if len(purchases) < 1:
				msg=_('There are not any purchase matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secProductsStoresByStores #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByStores #products_stored_by_stores").hide();'
				html+='$("#secProductsStoresByStores #secDetails").empty();'
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
						ppds=PurchasesProductsDetails.objects.filter(purchase_detail=pd,stored=True)

						for ppd in ppds:
							if ppd.in_store.id not in stores_id_array: #and \
							# ppd.in_store.shop.id in shops:
								stores_array.append(ppd.in_store)
								stores_id_array.append(ppd.in_store.id)

						for store in stores_array:
							# shop=store.shop

							#if shop in shops and \
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
				html='<script type="text/javascript">$("#secProductsStoresByStores #msg").html(\''+html_+'\');'
				html+='$("#secProductsStoresByStores #products_stored_by_stores").hide();'
				html+='$("#secProductsStoresByStores #secDetails").empty();'
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

	ds_lbl=_('Products stored amount')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("products_stored_by_stores").getContext("2d");'

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
	html +=						'labelString: "' + _('Products stored amount') + '"'
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

	html += '$("#secProductsStoresByStores #products_stored_by_stores").show();'
	html += '$("#secProductsStoresByStores #msg").empty();'
	html += '$("#secProductsStoresByStores #secDetails").html(\''
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

			# shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			stores=Stores.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)

			# context['shops']=shops
			context['stores']=stores
			context['products']=products
			context['brands']=brands

			return render(request,'analytics/products-stores/advanced-cfg-by-range.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def advanced_cfg_by_product(request):
	context={}
	if request.method == 'GET':
		try:
			my_users=[]
			user=Users.objects.get(pk=request.user)
			users=Users.objects.filter(created_by_user=user)
			my_users.extend(users)
			my_users.append(user)

			# shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			stores=Stores.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)

			# context['shops']=shops
			context['stores']=stores
			context['products']=products
			context['brands']=brands

			return render(request,'analytics/products-stores/advanced-cfg-by-product.html',context=context)
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

			# shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			stores=Stores.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)

			# context['shops']=shops
			context['stores']=stores
			context['products']=products
			context['brands']=brands

			return render(request,'analytics/products-stores/advanced-cfg-by-users.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def advanced_cfg_by_brand(request):
	context={}
	if request.method == 'GET':
		try:
			my_users=[]
			user=Users.objects.get(pk=request.user)
			users=Users.objects.filter(created_by_user=user)
			my_users.extend(users)
			my_users.append(user)

			# shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			stores=Stores.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)

			# context['shops']=shops
			context['stores']=stores
			context['products']=products
			context['brands']=brands

			return render(request,'analytics/products-stores/advanced-cfg-by-brand.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def advanced_cfg_by_store(request):
	context={}
	if request.method == 'GET':
		try:
			my_users=[]
			user=Users.objects.get(pk=request.user)
			users=Users.objects.filter(created_by_user=user)
			my_users.extend(users)
			my_users.append(user)

			# shops=Shops.objects.filter(dropped=False,created_by_user__in=my_users)
			stores=Stores.objects.filter(dropped=False,created_by_user__in=my_users)
			products=Products.objects.filter(dropped=False,created_by_user__in=my_users)
			brands=Brands.objects.filter(dropped=False,created_by_user__in=my_users)

			# context['shops']=shops
			context['stores']=stores
			context['products']=products
			context['brands']=brands

			return render(request,'analytics/products-stores/advanced-cfg-by-store.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})