# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.translation import gettext as _

from catalogues.models import MyModel
from brands.models import Brands
from stores.models import Stores
from products.models import Products
from providers.models import Providers

from datetime import datetime

import os

class Purchases(MyModel):
	provider=models.ForeignKey(Providers, related_name='providers_set', on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='provider_id', verbose_name=_('Provider'))
	identifier = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('Purchase identifier'))
	#product = models.ForeignKey(Products, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='product_id', verbose_name=_('Product'))
	#brand = models.ForeignKey(Brands, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='brand_id', verbose_name=_('Brand'))
	#store = models.ForeignKey(Stores, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='store_id', verbose_name=_('Store'))
	purchased_at = models.TimeField(default=datetime.now(), blank=False, null=False, verbose_name=_('Purchased at'))
	purchased_when = models.DateField(default=datetime.now(), blank=False, null=False, verbose_name=_('Purchased when'))
	purchased_date=models.DateTimeField(default=datetime.now(), blank=False, null=False, editable=False)
	#sku = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('SKU'), unique=True)
	#photo = models.ImageField(default=None, blank=True, null=True, verbose_name=_('Photo'), upload_to=uploads_dir, max_length=500)
	#quantity = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name=_('Quantity'))
	#purchase_price = models.DecimalField(max_digits=11, decimal_places=2, default=None, blank=False, null=False, verbose_name=_('Purchase price'))
	description = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Description'))
	notes = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Notes or comments'))

	_details = None
	_products = []
	_purchased_products_counter = 0
	_sold_products_counter=0
	_stored_products_counter=0

	'''
	def __init__(self, *args, **kwargs):
		super(Purchases, self).__init__(*args, **kwargs)

		results = PurchasesDetails.objects.filter(purchase=self).all()
		print('******results********')
		print(results)
		for result in results:
			print('******result********')
			print(result)
			self.details.push(result)
			self.products.push(result.products)
	'''
	def __retrieve_details__(self):
		self._details = PurchasesDetails.objects.filter(purchase=self).all()
		return self._details

	@property
	def details(self):
		'''
		print('**********ENTRO DETAILS*********')
		self._details = PurchasesDetails.objects.filter(purchase=self).all()
		return self._details
		'''
		if self._details is None:
			self.__retrieve_details__()

		return self._details

	def __retrieve_products__(self):
		#return self.products
		#self._products = []
		if self._details is None:
			self.__retrieve_details__()

		for detail in self._details:
			self._purchased_products_counter += detail.purchased_products_counter
			self._products.append(detail.products)
			self._sold_products_counter += detail.sold_products_counter
			self._stored_products_counter += detail.stored_products_counter

		#print(self._products.)
		return self._products

	@property
	def products(self):
		return self.__retrieve_products__()

	@property
	def purchased_products_counter(self):
		if self._details is None:
			self.__retrieve_details__()
			self.__retrieve_products__()

		return self._purchased_products_counter
	
	@property
	def sold_products_counter(self):
		# if self._sold_products_counter < 1:
		# 	print('***INICIO _sold_products_counter***')
		# 	if (self._products is None):
		# 		self.__retrieve_products__()

		# 	print(self._products)
		# 	for product in self._products:
		# 		if product.sold:
		# 			self._sold_products_counter+=1
		# 		if product.stored:
		# 			self._stored_products_counter+=1

		# print('**********self._sold_products_counter******')
		# print(self._sold_products_counter)
		return self._sold_products_counter

	@property
	def stored_products_counter(self):
		# if self._stored_products_counter < 1:
		# 	print('***INICIO _stored_products_counter***')
		# 	if (self._products is None):
		# 		self.__retrieve_products__()

		# 	print(self._products)
		# 	for product in self._products:
		# 		if product.sold:
		# 			self._sold_products_counter+=1
		# 		if product.stored:
		# 			self._stored_products_counter+=1

		# print('**********self._stored_products_counter******')
		# print(self._stored_products_counter)
		return self._stored_products_counter

	@property
	def purchased_when_fmt_mx(self):
		year = self.purchased_when.year
		month = self.purchased_when.month
		day = self.purchased_when.day
		result = str(day) + '/' + str(month) + '/' + str(year)
		'''
		result = \
			self.purchased_when[5:2] + '/' + \
			self.purchased_when[8:2] + '/' + \
			self.purchased_when[0:4]
		'''
		return result

	class Meta:
		#unique_together = ('product', 'brand', 'created_by_user', 'purchased_at', 'purchased_when')
		unique_together = ('created_by_user', 'purchased_at', 'purchased_when', 'identifier')
		permissions = (
			(_('Find') + ' [action=#/purchases/find]', _('Find')),
			(_('Add') + ' [action=#/purchases/add]', _('Add')),
			(_('Edit') + ' [action=#/purchases/edit]', _('Edit')),
			(_('Delete') + ' [action=#/purchases/delete]', _('Delete')),
		)

class PurchasesDetails(MyModel):
	purchase = models.ForeignKey(Purchases, related_name='purchase_details_set', on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='purchase_id', verbose_name=_('Purchase'))
	product = models.ForeignKey(Products, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='product_id', verbose_name=_('Product'))
	brand = models.ForeignKey(Brands, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='brand_id', verbose_name=_('Brand'))

	# IMPROVE: Change field quantity to PositiveSmallIntegerField?
	'''
	PositiveIntegerField: Values from 0 to 2147483647
	PositiveSmallIntegerField: Values from 0 to 32767 
	'''
	quantity = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name=_('Quantity'))
	purchase_price = models.DecimalField(max_digits=11, decimal_places=2, default=None, blank=False, null=False, verbose_name=_('Purchase price'))
	sale_price = models.DecimalField(max_digits=11, decimal_places=2, default=None, blank=False, null=False, verbose_name=_('Sale price'))
	description = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Description'))
	notes = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Notes or comments'))

	_products = None
	_purchased_products_counter = 0
	_sold_products_counter=0
	_stored_products_counter=0

	'''
	def __init__(self, *args, **kwargs):
		super(PurchasesDetails, self).__init__(*args, **kwargs)

		results = PurchasesProductsDetails.objects.filter(purchase_detail=self).all()
		print('******results details********')
		print(results)
		for result in results:
			print('******product********')
			print(result)
			self.products.push(result)
	'''
	def __retrieve_products__(self):
		self._products = PurchasesProductsDetails.objects.filter(purchase_detail=self).all()
		return self._products

	@property
	def products(self):
		if self._products is None:
			self.__retrieve_products__()

		return self._products

	@property
	def purchased_products_counter(self):
		if (self._products is None):
			self.__retrieve_products__()

		self._purchased_products_counter = len(self._products)
		return self._purchased_products_counter

	@property
	def sold_products_counter(self):
		if self._sold_products_counter < 1:
			if (self._products is None):
				self.__retrieve_products__()

			self._purchased_products_counter = len(self._products)

			for product in self._products:
				if product.sold:
					self._sold_products_counter+=1
				if product.stored:
					self._stored_products_counter+=1

		return self._sold_products_counter

	@property
	def stored_products_counter(self):
		if self._stored_products_counter < 1:
			if (self._products is None):
				self.__retrieve_products__()

			self._purchased_products_counter = len(self._products)

			for product in self._products:
				if product.sold:
					self._sold_products_counter+=1
				if product.stored:
					self._stored_products_counter+=1

		return self._stored_products_counter
'''
	class Meta:
		permissions = (
			(_('Find') + ' [action=#/purchases-details/find]', _('Find')),
			(_('Add') + ' [action=#/purchases-details/add]', _('Add')),
			(_('Edit') + ' [action=#/purchases-details/edit]', _('Edit')),
			(_('Delete') + ' [action=#/purchases-details/delete]', _('Delete')),
		)
'''

class PurchasesProductsDetails(MyModel):
	def uploads_dir(instance, filename):
		# We must to create its upload dir...
		path = os.getcwd() + '/static/uploads/products/purchases/' + str(instance.purchase_detail.purchase.id)
		try:
			os.makedirs(path)
		except OSError:  
			print("Creation of the directory %s failed" % path)
		else:  
			print ("Successfully created the directory %s " % path)
		return path + '/product-' + str(instance.purchase_detail.product.id) + '-sku-' + str(instance.sku) + 'filename-' + filename

	purchase_detail = models.ForeignKey(PurchasesDetails, related_name='products_details_set', on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='purchase_detail_id', verbose_name=_('Purchase details'))
	sku = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('SKU'), unique=True)
	image = models.ImageField(default=None, blank=True, null=True, verbose_name=_('Photo'), upload_to=uploads_dir, max_length=500)
	stored = models.BooleanField(default=False, editable = False, blank=False, null=False)
	in_store = models.ForeignKey(Stores, on_delete=models.PROTECT, default=None, blank=True, null=True, db_column='store_id', verbose_name=_('In store'))
	sold = models.BooleanField(default=False, editable = False, blank=False, null=False)
	#image = models.CharField(default=None, blank=True, null=True, verbose_name=_('Photo'), max_length=500)

	@property
	def static_photo(self):
		result = '/static/imgs/no-image-available.jpg'

		if self.image.name and self.image.name is not None and len(self.image.name) > 0:
			result = self.image.name[self.image.name.index('/static'):]

		return result

	class Meta:
		permissions = (
			(_('Find') + ' [action=#/products-stores/find]', _('Find')),
			(_('Add') + ' [action=#/products-stores/add]', _('Add')),
			(_('Edit') + ' [action=#/products-stores/edit]', _('Edit')),
			(_('Delete') + ' [action=#/products-stores/delete]', _('Delete')),
		)