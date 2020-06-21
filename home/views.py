# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

from taggit.models import TaggedItem

from django.http import JsonResponse

from shops.models import Shops

dummy=_('Low price feature 2')
dummy=_('Advanced technologies feature 2')
dummy=_('Multidisciplinary team feature 2')

def index(request):
	return render(request, 'home/index.html')

def retrieve_most_visited_shop(request):
	if request.method == 'GET':
		msg=_('There are not any registered shop yet')
		try:
			shop=Shops.objects.filter(dropped=False).order_by('-visits_number').first()
			if shop is not None:
				return JsonResponse({'status': 'success', 'shop_name': shop.name, 'shop_addr1': shop.address_line1, 'shop_addr2': shop.address_line2, 'shop_city': shop.city.display_name, 'shop_static_photo': shop.static_photo, 'shop_id': shop.id})
			else:
				return JsonResponse({'status': 'warning', 'msg': msg})
		except ObjectDoesNotExist:
			return JsonResponse({'status': 'error', 'msg': msg})

	msg=_('You do not have permission to perform this request')
	return JsonResponse({'status': 'error', 'msg': msg})

def retrieve_most_visited_shops(request):
	context={}
	if request.method == 'GET':
		try:
			shops=Shops.objects.filter(dropped=False).order_by('-visits_number', 'name')
			ct=ContentType.objects.get(app_label__icontains='icon',model='shops')

			shops_array=[]

			for shop in shops:
				tis=TaggedItem.objects.filter(content_type=ct,object_id=shop.id)
				categories_=[]
				for ti in tis:
					categories_.append(ti.tag)
				shops_array.append({'shop': shop, 'categories': categories_})

			if len(shops_array)>0:
				context['status']='success'
				context['shops']=shops_array
			else:
				context['status']='warning'

			return render(request, 'home/most-visited-shops-content.html', context=context)
		except ObjectDoesNotExist:
			msg=_('There are not any registered shop yet')
			context['status']='error'
			context['msg']=msg
			#return render(request, 'home/most-visited-shops.html', context=context)
			return render(request, 'home/most-visited-shops-content.html', context=context)

	msg=_('You do not have permission to perform this request')
	context['status']='error'
	context['msg']=msg
	#return render(request, 'home/most-visited-shops.html', context=context)
	return render(request, 'home/most-visited-shops-content.html', context=context)