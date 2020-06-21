# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.translation import gettext as _

#from users.models import Users

#from shops.models import shops

from datetime import datetime
#from products.models import Products
#from brands.models import Brands
from purchases.models import PurchasesProductsDetails
from catalogues.models import MyModel
from customers.models import Customers

class Sales(MyModel):
	customer=models.ForeignKey(Customers, related_name='sales_set', on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='customer_id', verbose_name=_('Customer'))
	identifier = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('Sale identifier'))
	#sku = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('SKU'), unique=True)
	sold_at = models.TimeField(default=datetime.now(), blank=False, null=False, verbose_name=_('Saling at'))
	sold_when = models.DateField(default=datetime.now(), blank=False, null=False, verbose_name=_('Saling when'))
	saved_at = models.TimeField(default=datetime.now(), blank=False, null=False, verbose_name=_('Saved at'))
	saved_when = models.DateField(default=datetime.now(), blank=False, null=False, verbose_name=_('Saved when'))
	description = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Description'))
	notes = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Notes or comments'))
	sold_date=models.DateTimeField(default=datetime.now(), blank=False, null=False, editable=False)
	#total = models.DecimalField(max_digits=11, decimal_places=2, default=None, blank=False, null=False, verbose_name=_('Total'))

	@property
	def number_of_sold_products(self):
		sd=SalesDetails.objects.filter(sale=self)
		return len(sd)

	@property
	def sold_when_fmt_mx(self):
		year = self.sold_when.year
		month = self.sold_when.month
		day = self.sold_when.day
		result = str(day) + '/' + str(month) + '/' + str(year)
		return result

	class Meta:
		unique_together = ('created_by_user', 'sold_at', 'sold_when', 'identifier')
		permissions = (
			(_('Find') + ' [action=#/sales/find]', _('Find')),
			(_('Add') + ' [action=#/sales/add]', _('Add')),
			(_('Edit') + ' [action=#/sales/edit]', _('Edit')),
			(_('Delete') + ' [action=#/sales/delete]', _('Delete')),
			(_('Analytics') + ' [action=#/analytics/sales/]', _('Analytics'))
		)

class SalesDetails(MyModel):
	sale = models.ForeignKey(Sales, related_name='sale_details_set', on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='sale_id', verbose_name=_('Sale'))
	product = models.ForeignKey(PurchasesProductsDetails, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='product_id', verbose_name=_('Product'))
	#brand = models.ForeignKey(Brands, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='brand_id', verbose_name=_('Brand'))

	#quantity = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name=_('Quantity'))
	#price = models.DecimalField(max_digits=11, decimal_places=2, default=None, blank=False, null=False, verbose_name=_('Price'))
	description = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Description'))
	notes = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Notes or comments'))

	'''
	sale = models.ForeignKey(Sales, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='sale_id', verbose_name=_('Brand'))
	itm = models.ForeignKey(ProductsInStores, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='itm_id', verbose_name=_('Article'))
	quantity = models.PositiveIntegerField(default=1, blank=False, null=False, verbose_name=_('Quantity'))
	'''

	class Meta:
		unique_together = ('sale', 'product')

	'''
	class Meta:
		unique_together = ('sale', 'product')
		permissions = (
			(_('Find') + ' [action=#/sales-details/find]', _('Find')),
			(_('Add') + ' [action=#/sales-details/add]', _('Add')),
			(_('Edit') + ' [action=#/sales-details/edit]', _('Edit')),
			(_('Delete') + ' [action=#/sales-details/delete]', _('Delete')),
		)
	'''