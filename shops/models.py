# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

#from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist

from django.utils.translation import gettext as _

from datetime import datetime

from catalogues.models import City, MyModel
from users.models import Users

from taggit.managers import TaggableManager

import os

#class Shops(models.Model):
class Shops(MyModel):
	def uploads_dir(instance, filename):
		# We must to create its upload dir...
		path = os.getcwd() + '/static/uploads/shops/' + str(instance.id)
		try:
			os.makedirs(path)
		except OSError:  
			print("Creation of the directory %s failed" % path)
		else:  
			print ("Successfully created the directory %s " % path)
		# return path + '/product-' + str(instance.purchase_detail.product.id) + '-sku-' + str(instance.sku) + 'filename-' + filename
		return path

	image = models.ImageField(default=None, blank=True, null=True, verbose_name=_('Photo'), upload_to=uploads_dir, max_length=500)
	name = models.CharField(max_length=255, default=None, blank=False, null=False, verbose_name=_('Shop name'))
	city = models.ForeignKey(City, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='city_id', verbose_name=_('City'))
	admin = models.ForeignKey(Users, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='admin_id', verbose_name=_('User admin'))
	address_line1 = models.CharField(max_length=1024, default=None, blank=False, null=False, verbose_name=_('Address line 1'))
	address_line2 = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Address line 2'))
	cell_phone = models.CharField(max_length=10, default=None, blank=False, null=False, verbose_name=_('Cell phone'))
	home_phone = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_('Home phone'))
	other_phone = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_('Other phone'))
	visits_number = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name=_('Visits number'), editable=False)

	categories = TaggableManager()

	'''
	created_by_user = models.ForeignKey(Users, editable = False, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='created_by_user', verbose_name=_('Created by'), related_name='%(class)s_created_by')
	created_at = models.TimeField(editable = False, default=datetime.now(), blank=False, null=False)
	created_when = models.DateField(editable = False, default=datetime.now(), blank=False, null=False)

	disabled = models.BooleanField(editable = False, default=False)
	disabled_at = models.TimeField(editable = False, default=None, blank=True, null=True)
	disabled_when = models.DateField(editable = False, default=None, blank=True, null=True)
	disabled_reason = models.CharField(editable = False, max_length=1024, default=None, blank=True, null=True, verbose_name=_('Specify the reason to disable this shop'))

	dropped = models.BooleanField(editable = False, default=False)
	dropped_at = models.TimeField(editable = False, default=None, blank=True, null=True)
	dropped_when = models.DateField(editable = False, default=None, blank=True, null=True)
	dropped_reason = models.CharField(editable = False, max_length=1024, default=None, blank=True, null=True, verbose_name=_('Specify the reason to drop this shop'))
	'''

	@property
	def static_photo(self):
		result = '/static/imgs/no-image-available.jpg'

		if self.image.name and self.image.name is not None and len(self.image.name) > 0:
			result = self.image.name[self.image.name.index('/static'):]

		return result

	def save(self):
		super(Shops, self).save()
		# We must to create its upload dir...
		path = os.getcwd() + '/static/uploads/shops/shop-' + str(self.id)
		try:
			os.makedirs(path)
		except OSError:  
			print("Creation of the directory %s failed" % path)
		else:  
			print ("Successfully created the directory %s " % path)

	class Meta:
		# In MySQL, with utf8 encoding for tables, the max key size for varchar is 255
		#unique_together = ('name', 'city', 'address_line1')
		unique_together = ('created_by_user', 'name', 'city')
		permissions = (
			(_('Find') + ' [action=#/shops/find]', _('Find')),
			(_('Add') + ' [action=#/shops/add]', _('Add')),
			(_('Edit') + ' [action=#/shops/edit]', _('Edit')),
			(_('Delete') + ' [action=#/shops/delete]', _('Delete')),
		)
		#app_label = _('Shops')