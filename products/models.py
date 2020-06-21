# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.translation import gettext as _

from catalogues.models import MyModel
#from brands.models import Brands
#from stores.models import Stores
#from shops.models import Shops

#from datetime import datetime
#import os

class Products(MyModel):
	name = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('Product name'), unique=True)

	'''
	def undrop(self):
		self.dropped = False
		self.dropped_at = None
		self.dropped_when = None
		self.dropped_reason = None
		self.save()

	def drop(self, reason=None):
		full_time = datetime.now()
		self.dropped = True
		self.dropped_at = full_time
		self.dropped_when = full_time
		self.dropped_reason = reason
		self.save()
	'''

	class Meta:
		permissions = (
			(_('Find') + ' [action=#/products/find]', _('Find')),
			(_('Add') + ' [action=#/products/add]', _('Add')),
			(_('Edit') + ' [action=#/products/edit]', _('Edit')),
			(_('Delete') + ' [action=#/products/delete]', _('Delete')),
		)
		unique_together = ('name', 'created_by_user')

'''
class ProductsInStores(MyModel):
	def uploads_dir(instance, filename):
		# We must to create its upload dir...
		path = os.getcwd() + '/static/uploads/shops/shop-' + str(instance.store.shop.id) + '/stores/store-' + str(instance.store.id) + '/products/'
		try:
			os.makedirs(path)
		except OSError:  
			print("Creation of the directory %s failed" % path)
		else:  
			print ("Successfully created the directory %s " % path)
		return path + filename

	product = models.ForeignKey(Products, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='product_id', verbose_name=_('Product'))
	brand = models.ForeignKey(Brands, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='brand_id', verbose_name=_('Brand'))
	#shop = models.ForeignKey(Shops, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='shop_id', verbose_name=_('Shop'))
	store = models.ForeignKey(Stores, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='store_id', verbose_name=_('Store'))
	sku = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('SKU'), unique=True)
	photo = models.ImageField(default=None, blank=True, null=True, verbose_name=_('Photo'), upload_to=uploads_dir, max_length=500)
	quantity = models.PositiveIntegerField(default=1, blank=False, null=False, verbose_name=_('Quantity'))
	price = models.DecimalField(max_digits=11, decimal_places=2, default=None, blank=False, null=False, verbose_name=_('Price'))

	@property
	def static_photo(self):
		result = self.photo.name[self.photo.name.index('/static'):]
		return result

	class Meta:
		unique_together = ('product', 'brand', 'store')
		permissions = (
			(_('Find') + ' [action=#/products-stores/find]', _('Find')),
			(_('Add') + ' [action=#/products-stores/add]', _('Add')),
			(_('Edit') + ' [action=#/products-stores/edit]', _('Edit')),
			(_('Delete') + ' [action=#/products-stores/delete]', _('Delete')),
		)
'''