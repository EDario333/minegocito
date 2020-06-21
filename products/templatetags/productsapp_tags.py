# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template import Library

from django.utils.translation import gettext as _

from products.products_stores_views import ProductsPurchasedView

register = Library()

@register.inclusion_tag('products-stores/purchased-products.html', takes_context=True)
def products_stored(context):
	request = context['request']
	can_edit = context['can_edit']
	can_delete = context['can_delete']

	view = ProductsPurchasedView(user=request.user, stored=True)
	products = view.object_list

	return {'request': request, 'products': products, 'stored': True, 'can_edit': can_edit, 'can_delete': can_delete}

@register.inclusion_tag('products-stores/purchased-products.html', takes_context=True)
def products_not_stored(context):
	request = context['request']

	view = ProductsPurchasedView(user=request.user, stored=False)
	products = view.object_list

	return {'request': request, 'products': products, 'stored': False, 'can_edit': False, 'can_delete': False}

'''
@register.inclusion_tag('products-stores/all-products-purchased.html', takes_context=True)
def all_products_purchased(context):
  request = context['request']
  can_edit = context['can_edit']
  can_delete = context['can_delete']

  view = ProductsPurchasedView(user=request.user, all=True)
  products = view.object_list

  return {'request': request, 'products': products, 'can_edit': can_edit, 'can_delete': can_delete}
'''