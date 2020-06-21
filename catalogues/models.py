# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from cities_light.abstract_models import AbstractCity, AbstractRegion, AbstractCountry
from cities_light.receivers import connect_default_signals

from django.utils.translation import gettext as _

from datetime import datetime

from utils import utils

#from users.models import Users

class Country(AbstractCountry):
  class Meta:
    verbose_name = _("Country")
    verbose_name_plural = _("Countries")

connect_default_signals(Country)

class Region(AbstractRegion):
  pass

connect_default_signals(Region)

class City(AbstractCity):
  timezone = models.CharField(max_length=40)

connect_default_signals(City)

class MyModel(models.Model):
	def __init__(self, *args, **kwargs):
		super(MyModel, self).__init__(*args, **kwargs)

	created_by_user = models.ForeignKey('users.Users', editable = False, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='created_by_user', verbose_name=_('Created by'), related_name='%(class)s_created_by')
	created_at = models.TimeField(default=datetime.now(), blank=False, null=False)
	created_when = models.DateField(default=datetime.now(), blank=False, null=False)

	disabled = models.BooleanField(default=False)
	disabled_at = models.TimeField(editable = False, default=None, blank=True, null=True)
	disabled_when = models.DateField(editable = False, default=None, blank=True, null=True)
	disabled_reason = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Specify the reason to disable this product'))

	dropped = models.BooleanField(default=False)
	dropped_at = models.TimeField(editable = False, default=None, blank=True, null=True)
	dropped_when = models.DateField(editable = False, default=None, blank=True, null=True)
	dropped_reason = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Specify the reason to drop this object'))

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

	class Meta:
		#proxy = True
		abstract = True

class Person(MyModel):
	def __init__(self, *args, **kwargs):
		super(Person, self).__init__(*args, **kwargs)

	last_name = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('Last name'))
	mothers_last_name = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Mothers last name'))	
	first_name = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('First name'))
	middle_name = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Middle name'))

	gender = models.CharField(max_length=1, choices=utils.GENDERS, default=None, blank=False, null=False, verbose_name=_('Gender'))
	dob = models.DateField(default=None, blank=False, null=False, verbose_name=_('Date of birth'))

	email = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Email'))

	city = models.ForeignKey(City, on_delete=models.PROTECT, default=None, blank=True, null=True, db_column='city_id', verbose_name=_('City'))
	address_line1 = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Address line 1'))
	address_line2 = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Address line 2'))

	cell_phone = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_('Cell phone'))
	home_phone = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_('Home phone'))
	other_phone = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_('Other phone'))

	@property
	def full_name(self):
		result=self.first_name
		if self.middle_name and self.middle_name is not None and len(self.middle_name.strip()) > 0:
			result+=' ' + str(self.middle_name)
		result+=' ' + str(self.last_name)
		if self.mothers_last_name and self.mothers_last_name is not None and len(self.mothers_last_name.strip()) > 0:
			result+=' ' + str(self.mothers_last_name)
		return result
	
	@property
	def dob_fmt_mx(self):
		result=str(self.dob)
		result=result[8:]+'/'+result[5:7]+'/'+result[:4]
		return result
	
	class Meta:
		#abstract = True
		# unique_together = [
		# 	# ('email', 'created_by_user')
		# 	('last_name', 'mothers_last_name', 'first_name', 'middle_name', 'gender', 'dob', 'email', 'created_by_user')
		# ]

		permissions = (
			(_('Find') + ' [action=#/persons/find]', _('Find')),
			(_('Add') + ' [action=#/persons/add]', _('Add')),
			(_('Edit') + ' [action=#/persons/edit]', _('Edit')),
			(_('Delete') + ' [action=#/persons/delete]', _('Delete')),
		)

class ObjectWithAddress(MyModel):
	def __init__(self, *args, **kwargs):
		super(ObjectWithAddress, self).__init__(*args, **kwargs)

	city = models.ForeignKey(City, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='city_id', verbose_name=_('City'))
	address_line1 = models.CharField(max_length=1024, default=None, blank=False, null=False, verbose_name=_('Address line 1'))
	address_line2 = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Address line 2'))

	email = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('Email'), unique=True)
	cell_phone = models.CharField(max_length=10, default=None, blank=False, null=False, verbose_name=_('Cell phone'))
	home_phone = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_('Home phone'))
	other_phone = models.CharField(max_length=10, default=None, blank=True, null=True, verbose_name=_('Other phone'))

	class Meta:
		abstract = True
		#unique_together = ('last_name', 'mothers_last_name', 'first_name', 'middle_name', 'gender', 'dob', 'city', 'address_line1')