from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.utils.translation import gettext as _

from django.core.exceptions import ObjectDoesNotExist

from sales.models import Sales, SalesDetails

# from purchases.models import PurchasesProductsDetails

from datetime import datetime, timedelta

from customers.models import Customers

from users.models import Users

#from stores.models import Stores
from shops.models import Shops

from products.models import Products

from brands.models import Brands

import dateutil.parser

import json

# https://www.chartjs.org/samples/latest/scales/time/financial.html
# view-source:https://www.chartjs.org/samples/latest/scales/time/financial.html

dummy=_('Starting and ending dates are wrong')
dummy=_('Starting and ending times are wrong')
#dummy=_('Please select at least one store')
dummy=_('Please select at least one shop')
dummy=_('Please select at least one product')
dummy=_('Please select at least one brand')
dummy=_('Please select at least one customer')
dummy=_('Please select at least one cashier')

def __sales_of_the_day__(request, itm_menu):
	try:
		today=datetime.today()
		sales=Sales.objects.filter(sold_when=today,dropped=False).order_by('sold_at')

		if len(sales) < 1:
			msg=_('There are not any sale today')
			html_='<p class="label label-default">'
			html_+=msg + '</p> '
			html='$("#secSalesOfTheDay").html(\''+html_+'\');'
			html+='$("#secSalesOfTheDay").parent().css("height", "375.6px");'
			html+='$("#secSalesOfTheDay #sales_of_the_day").remove();'
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

		sales_id_array=[]
		sales_array=[]

		details='<div class="table-responsive">'
		details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
		details+=_('Sale ID')
		details+='</th><th>'
		details+=_('Saling when')
		details+='</th><th>'
		details+=_('Saling at')
		details+='</th><th>'
		details+=_('Options')
		details+='</th></tr></thead><tbody>'

		for sale in sales:
			if sale.id not in sales_id_array:
				sds=SalesDetails.objects.filter(sale=sale)
				for sd in sds:
					ppd=sd.product
					store=ppd.in_store

					# pd has data about product and brand
					pd=ppd.purchase_detail
					shop=store.shop

					if shop in shops and \
					pd.product in products and \
					pd.brand in brands and \
					sale.id not in sales_id_array:
						sales_array.append(sale)
						sales_id_array.append(sale.id)
						details+='<tr><td>'
						details+=sale.identifier+'</td><td>'
						details+=sale.sold_when_fmt_mx+'</td><td>'
						details+=str(sale.sold_at)+'</td><td>'
						details+='<a href="#" data-placement="bottom" '
						details+='data-toggle="tooltip" '
						details+='title="' + _('Details') + '" '
						details+='data-original-title="' + _('Details') + '" '
						details+='onclick="showDetailsSalesAnalytics(' + str(sale.id)
						details+=', itm_menu);'
						details+=' return false;">'
						# details+='onclick="alert(tst);">'
						details+='<i class="material-icons">zoom_in</i>'
						details+='</a></td></tr>'

		details += '</table></div>'

		data='var itm_menu = "' + itm_menu + '"; '
		data+='var module = "sales"; '
		data='var data = ['

		for sale in sales:
			data+='{t: new Date('
			data+=str(today.year)+','+str(today.month)+','+str(today.day)
			data+=','+str(sale.sold_at.hour)+','
			data+=str(sale.sold_at.minute)+','
			data+=str(sale.sold_at.second)
			data+='), y: ' + str(sale.number_of_sold_products) + '},'
		data=data[:len(data)-1]
		data+='];'
	except ObjectDoesNotExist:
		msg=_('There are not any sale today')
		html='show_msg_with_toastr("warning", "' + msg + '");'
		return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_of_the_day").getContext("2d");'

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

	html += '$("#secSalesOfTheDay #secDetails").html(\''
	html += details
	html += '\');'

	return html

def index(request):
	context={}
	if request.method == 'GET':
		itm_menu=request.GET.get('itm_menu', 'lnk1')
		form = {
			'title': _('Sales analytics')
		}
		context['form']=form
		context['itm_menu']=itm_menu
		context['sales_of_the_day_chart']=__sales_of_the_day__(request, itm_menu)
		return render(request,'analytics/sales/index.html',context=context)

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
		shops=json.loads(shops)
		shops=Shops.objects.filter(dropped=False, pk__in=shops)

		products=request.POST.get('products', None)
		products=json.loads(products)
		products=Products.objects.filter(dropped=False, pk__in=products)

		brands=request.POST.get('brands', None)
		brands=json.loads(brands)
		brands=Brands.objects.filter(dropped=False, pk__in=brands)

		customers=request.POST.get('customers', None)
		customers=json.loads(customers)
		customers=Customers.objects.filter(dropped=False, pk__in=customers)

		users=request.POST.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		try:
			# sales=Sales.objects.filter(sold_when__range=(starting_when, ending_when), sold_at__range=(starting_at, ending_at), dropped=False).order_by('sold_at')
			starts=dateutil.parser.parse(starting_when+' '+starting_at)
			ends=dateutil.parser.parse(ending_when+' '+ending_at)

			sales=Sales.objects.filter(sold_date__range=(starts, ends), dropped=False,created_by_user__in=users,customer__in=customers).order_by('sold_date')
			#sales=Sales.objects.filter(sold_when__range=(starting_when, ending_when), dropped=False)
			# sales=sales.filter(sold_at__range=(starting_at, ending_at)).order_by('sold_at')
			# print('*********sales******')
			# print(sales)

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByRange #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByRange").hide();'
				html+='$("#secSalesByRange #sales_by_range").hide();'
				html+='$("#secSalesByRange #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			sales_id_array=[]
			sales_array=[]

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop=store.shop

						if shop in shops and \
						pd.product in products and \
						pd.brand in brands and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							# details+='onclick="alert(tst);">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByRange #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByRange").hide();'
				html+='$("#secSalesByRange #sales_by_range").hide();'
				html+='$("#secSalesByRange #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			#for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_range").getContext("2d");'

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

	html += '$("#secSalesByRange #sales_by_range").show();'
	html += '$("#secSalesByRange #msg").empty();'
	html += '$("#secSalesByRange #secDetails").html(\''
	html += details
	html += '\');'
	# html += '$("#menuSalesByRange").show();'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	# return html
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def by_customer(request):
	if request.method=='POST':
		customer=request.POST.get('customer_obj', None)

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
			customer=Customers.objects.get(pk=customer)
		except ObjectDoesNotExist:
			msg=_('The specified customer does not exists')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("error", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

		try:
			sales=Sales.objects.filter(customer=customer, dropped=False, created_by_user__in=users).order_by('sold_date')

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByCustomers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByCustomers").hide();'
				html+='$("#secSalesByCustomers #sales_by_customers").hide();'
				html+='$("#secSalesByCustomers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			sales_id_array=[]
			sales_array=[]

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop=store.shop

						if shop in shops and \
						pd.product in products and \
						pd.brand in brands and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							# details+='onclick="alert(tst);">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByCustomers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByCustomers").hide();'
				html+='$("#secSalesByCustomers #sales_by_customers").hide();'
				html+='$("#secSalesByCustomers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			# for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_customers").getContext("2d");'

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

	html += '$("#secSalesByCustomers #sales_by_customers").show();'
	html += '$("#secSalesByCustomers #msg").empty();'
	html += '$("#secSalesByCustomers #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def all_customers(request):
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
			sales=Sales.objects.filter(dropped=False,created_by_user__in=users).order_by('sold_date')

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByCustomers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByCustomers").hide();'
				html+='$("#secSalesByCustomers #sales_by_customers").hide();'
				html+='$("#secSalesByCustomers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			sales_id_array=[]
			sales_array=[]

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop=store.shop

						if shop in shops and \
						pd.product in products and \
						pd.brand in brands and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							# details+='onclick="alert(tst);">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByCustomers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByCustomers").hide();'
				html+='$("#secSalesByCustomers #sales_by_customers").hide();'
				html+='$("#secSalesByCustomers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			# for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_customers").getContext("2d");'

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

	html += '$("#secSalesByCustomers #sales_by_customers").show();'
	html += '$("#secSalesByCustomers #msg").empty();'
	html += '$("#secSalesByCustomers #secDetails").html(\''
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

		customers=request.POST.get('customers', None)
		customers=json.loads(customers)
		customers=Customers.objects.filter(dropped=False, pk__in=customers)

		try:
			sales=Sales.objects.filter(created_by_user=user, dropped=False, customer__in=customers).order_by('sold_date')

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByUsers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByUsers #sales_by_users").hide();'
				html+='$("#secSalesByUsers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			sales_id_array=[]
			sales_array=[]

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop=store.shop

						if shop in shops and \
						pd.product in products and \
						pd.brand in brands and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByUsers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByUsers #sales_by_users").hide();'
				html+='$("#secSalesByUsers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			# for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_users").getContext("2d");'

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

	html += '$("#secSalesByUsers #sales_by_users").show();'
	html += '$("#secSalesByUsers #msg").empty();'
	html += '$("#secSalesByUsers #secDetails").html(\''
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

		customers=request.GET.get('customers', None)
		customers=json.loads(customers)
		customers=Customers.objects.filter(dropped=False, pk__in=customers)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			sales=Sales.objects.filter(dropped=False, customer__in=customers).order_by('sold_date')

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByUsers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByUsers #sales_by_users").hide();'
				html+='$("#secSalesByUsers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			sales_id_array=[]
			sales_array=[]

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop=store.shop

						if shop in shops and \
						pd.product in products and \
						pd.brand in brands and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByUsers #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByUsers #sales_by_users").hide();'
				html+='$("#secSalesByUsers #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			# for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_users").getContext("2d");'

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

	html += '$("#secSalesByUsers #sales_by_users").show();'
	html += '$("#secSalesByUsers #msg").empty();'
	html += '$("#secSalesByUsers #secDetails").html(\''
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

		customers=request.POST.get('customers', None)
		customers=json.loads(customers)
		customers=Customers.objects.filter(dropped=False, pk__in=customers)

		users=request.POST.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

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
			sales=Sales.objects.filter(dropped=False,created_by_user__in=users,customer__in=customers).order_by('sold_date')

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByProducts #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByProducts #sales_by_products").hide();'
				html+='$("#secSalesByProducts #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			sales_id_array=[]
			sales_array=[]

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop=store.shop

						if shop in shops and \
						pd.product.id == product.id and \
						pd.brand in brands and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByProducts #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByProducts #sales_by_products").hide();'
				html+='$("#secSalesByProducts #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			# for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_products").getContext("2d");'

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

	html += '$("#secSalesByProducts #sales_by_products").show();'
	html += '$("#secSalesByProducts #msg").empty();'
	html += '$("#secSalesByProducts #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
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

		customers=request.GET.get('customers', None)
		customers=json.loads(customers)
		customers=Customers.objects.filter(dropped=False, pk__in=customers)

		users=request.GET.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			sales=Sales.objects.filter(dropped=False,created_by_user__in=users,customer__in=customers).order_by('sold_date')

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByProducts #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByProducts #sales_by_products").hide();'
				html+='$("#secSalesByProducts #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			sales_id_array=[]
			sales_array=[]

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop=store.shop

						if shop in shops and \
						pd.product in products and \
						pd.brand in brands and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByProducts #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByProducts #sales_by_products").hide();'
				html+='$("#secSalesByProducts #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			# for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_products").getContext("2d");'

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

	html += '$("#secSalesByProducts #sales_by_products").show();'
	html += '$("#secSalesByProducts #msg").empty();'
	html += '$("#secSalesByProducts #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
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

		customers=request.POST.get('customers', None)
		customers=json.loads(customers)
		customers=Customers.objects.filter(dropped=False, pk__in=customers)

		users=request.POST.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

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
			sales=Sales.objects.filter(dropped=False,created_by_user__in=users,customer__in=customers).order_by('sold_date')

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByBrands #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByBrands #sales_by_brands").hide();'
				html+='$("#secSalesByBrands #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			sales_id_array=[]
			sales_array=[]

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop=store.shop

						if shop in shops and \
						pd.product in products and \
						pd.brand.id == brand.id and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByBrands #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByBrands #sales_by_brands").hide();'
				html+='$("#secSalesByBrands #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			# for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_brands").getContext("2d");'

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

	html += '$("#secSalesByBrands #sales_by_brands").show();'
	html += '$("#secSalesByBrands #msg").empty();'
	html += '$("#secSalesByBrands #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
	return HttpResponse(html, 'text/html; charset=utf-8')

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def all_brands(request):
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

		customers=request.GET.get('customers', None)
		customers=json.loads(customers)
		customers=Customers.objects.filter(dropped=False, pk__in=customers)

		users=request.GET.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			sales=Sales.objects.filter(dropped=False,created_by_user__in=users,customer__in=customers).order_by('sold_date')

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByBrands #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByBrands #sales_by_brands").hide();'
				html+='$("#secSalesByBrands #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			sales_id_array=[]
			sales_array=[]

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop=store.shop

						if shop in shops and \
						pd.product in products and \
						pd.brand in brands and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByBrands #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByBrands #sales_by_brands").hide();'
				html+='$("#secSalesByBrands #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			# for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_brands").getContext("2d");'

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

	html += '$("#secSalesByBrands #sales_by_brands").show();'
	html += '$("#secSalesByBrands #msg").empty();'
	html += '$("#secSalesByBrands #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
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

		customers=request.POST.get('customers', None)
		customers=json.loads(customers)
		customers=Customers.objects.filter(dropped=False, pk__in=customers)

		users=request.POST.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

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
			sales=Sales.objects.filter(dropped=False,created_by_user__in=users,customer__in=customers).order_by('sold_date')

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByShops #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByShops #sales_by_shops").hide();'
				html+='$("#secSalesByShops #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			sales_id_array=[]
			sales_array=[]

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop_=store.shop

						if shop.id == shop_.id and \
						pd.product in products and \
						pd.brand in brands and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByShops #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByShops #sales_by_shops").hide();'
				html+='$("#secSalesByShops #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			# for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')
			# return html

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_shops").getContext("2d");'

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

	html += '$("#secSalesByShops #sales_by_shops").show();'
	html += '$("#secSalesByShops #msg").empty();'
	html += '$("#secSalesByShops #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
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

		customers=request.GET.get('customers', None)
		customers=json.loads(customers)
		customers=Customers.objects.filter(dropped=False, pk__in=customers)

		users=request.GET.get('users', None)
		users=json.loads(users)
		users=Users.objects.filter(dropped=False, pk__in=users)

		itm_menu=request.GET.get('itm_menu', None)

		try:
			sales=Sales.objects.filter(dropped=False,created_by_user__in=users,customer__in=customers).order_by('sold_date')

			if len(sales) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByShops #msg").html(\''+html_+'\');'
				# html+='$("#menuSalesByUsers").hide();'
				html+='$("#secSalesByShops #sales_by_shops").hide();'
				html+='$("#secSalesByShops #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')
				# return html

			details='<div class="table-responsive">'
			details+='<table class="table table-bordered table-striped table-hover dataTable js-exportable"><thead><tr><th>'
			details+=_('Sale ID')
			details+='</th><th>'
			details+=_('Saling when')
			details+='</th><th>'
			details+=_('Saling at')
			details+='</th><th>'
			details+=_('Options')
			details+='</th></tr></thead><tbody>'

			sales_id_array=[]
			sales_array=[]

			for sale in sales:
				if sale.id not in sales_id_array:
					sds=SalesDetails.objects.filter(sale=sale)
					for sd in sds:
						ppd=sd.product
						store=ppd.in_store

						# pd has data about product and brand
						pd=ppd.purchase_detail
						shop=store.shop

						if shop in shops and \
						pd.product in products and \
						pd.brand in brands and \
						sale.id not in sales_id_array:
							sales_array.append(sale)
							sales_id_array.append(sale.id)
							details+='<tr><td>'
							details+=sale.identifier+'</td><td>'
							details+=sale.sold_when_fmt_mx+'</td><td>'
							details+=str(sale.sold_at)+'</td><td>'
							details+='<a href="#" data-placement="bottom" '
							details+='data-toggle="tooltip" '
							details+='title="' + _('Details') + '" '
							details+='data-original-title="' + _('Details') + '" '
							details+='onclick="showDetails(' + str(sale.id)
							details+=', module, false, false, false, false, itm_menu);'
							details+=' return false;">'
							details+='<i class="material-icons">zoom_in</i>'
							details+='</a></td></tr>'

			if len(sales_array) < 1:
				msg=_('There are not any sale matching with your query options')
				html_='<p class="label label-default">'
				html_+=msg + '</p> '
				html='<script type="text/javascript">$("#secSalesByShops #msg").html(\''+html_+'\');'
				html+='$("#secSalesByShops #sales_by_shops").hide();'
				html+='$("#secSalesByShops #secDetails").empty();'
				html+='</script>'
				return HttpResponse(html, 'text/html; charset=utf-8')

			details += '</table></div>'

			data='<script type="text/javascript"> '
			data+='var itm_menu = "' + itm_menu + '"; '
			data+='var module = "sales"; '
			data+='var data = ['

			# for sale in sales:
			for sale in sales_array:
				sold_when=sale.sold_when
				sold_at=sale.sold_at
				data+='{t: new Date('
				data+=str(sold_when.year)+','+str(sold_when.month)+','+str(sold_when.day)
				data+=','+str(sold_at.hour)+','
				data+=str(sold_at.minute)+','
				data+=str(sold_at.second)
				data+='), y: ' + str(sale.number_of_sold_products) + '},'

			data=data[:len(data)-1]
			data+='];'
		except ObjectDoesNotExist:
			msg=_('There are not any sale matching with your query options')
			html='<script type="text/javascript"> '
			html+='show_msg_with_toastr("warning", "' + msg + '");'
			html+='</script>'
			return HttpResponse(html, 'text/html; charset=utf-8')

	ds_lbl=_('Sold products')

	html = data

	html += 'var dateFormat = "YYYY MMMM DD";'
	html += 'var ctx =  document.getElementById("sales_by_shops").getContext("2d");'

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

	html += '$("#secSalesByShops #sales_by_shops").show();'
	html += '$("#secSalesByShops #msg").empty();'
	html += '$("#secSalesByShops #secDetails").html(\''
	html += details
	html += '\');'
	html+='</script>'
	html+='<script src="/static/js/dashboard/search-results/after-load-html.js"></script>'
	html+='</script>'
	# return html
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
			customers=Customers.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['customers']=customers
			context['users']=my_users

			return render(request,'analytics/sales/advanced-cfg-by-range.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def advanced_cfg_by_customers(request):
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

			return render(request,'analytics/sales/advanced-cfg-by-customers.html',context=context)
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
			customers=Customers.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['customers']=customers

			return render(request,'analytics/sales/advanced-cfg-by-users.html',context=context)
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
			customers=Customers.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['customers']=customers
			context['users']=my_users

			return render(request,'analytics/sales/advanced-cfg-by-products.html',context=context)
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
			customers=Customers.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['customers']=customers
			context['users']=my_users

			return render(request,'analytics/sales/advanced-cfg-by-brands.html',context=context)
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
			customers=Customers.objects.filter(dropped=False,created_by_user__in=my_users)

			context['shops']=shops
			context['products']=products
			context['brands']=brands
			context['customers']=customers
			context['users']=my_users

			return render(request,'analytics/sales/advanced-cfg-by-shops.html',context=context)
		except ObjectDoesNotExist as e:
			print('**********e.args[0]*********')
			print(e.args[0])

	msg = _('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})