# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.translation import gettext as _

from catalogues.models import City, MyModel

from users.models import Users

from shops.models import Shops

import os

class Stores(MyModel):
	shop = models.ForeignKey(Shops, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='shop_id', verbose_name=_('Belongs to shop'))
	city = models.ForeignKey(City, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='city_id', verbose_name=_('City'))
	admin = models.ForeignKey(Users, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='admin_id', verbose_name=_('User admin'))

	name = models.CharField(max_length=255, default=None, blank=False, null=False, verbose_name=_('Store name'))
	
	address_line1 = models.CharField(max_length=1024, default=None, blank=False, null=False, verbose_name=_('Address line 1'))
	address_line2 = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Address line 2'))
	cell_phone = models.CharField(max_length=10, default=None, blank=False, null=False, verbose_name=_('Cell phone'))
	home_phone = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_('Home phone'))
	other_phone = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_('Other phone'))

	@property
	def store_with_shop_name(self):
		result = self.name + ' [' + _('Belongs to shop')
		result += '=' + self.shop.name 
		result += '; ' + _('User admin') + '='
		result += self.admin.first_name + ' '
		result += self.admin.last_name + ' ('
		result += self.admin.email + ')]'
		return result
	
	def save(self):
		super(Stores, self).save()
		# We must to create its upload dir...
		path = os.getcwd() + '/static/uploads/shops/shop-' + str(self.shop.id) + '/stores/store-' + str(self.id)
		try:
			os.makedirs(path)
		except OSError:  
			print("Creation of the directory %s failed" % path)
		else:  
			print ("Successfully created the directory %s " % path)

	class Meta:
		# In MySQL, with utf8 encoding for tables, the max key size for varchar is 255
		#unique_together = ('name', 'shop', 'city', 'address_line1')
		unique_together = ('created_by_user', 'shop', 'name', 'city')
		permissions = (
			(_('Find') + ' [action=#/stores/find]', _('Find')),
			(_('Add') + ' [action=#/stores/add]', _('Add')),
			(_('Edit') + ' [action=#/stores/edit]', _('Edit')),
			(_('Delete') + ' [action=#/stores/delete]', _('Delete')),
		)