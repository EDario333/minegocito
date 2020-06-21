# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.translation import gettext as _

from catalogues.models import Person

class Customers(Person):
	rfc = models.CharField(max_length=255, default=None, blank=False, null=False, verbose_name=_('RFC'))

	@property
	def full_name(self):
		result=self.first_name

		if self.middle_name and len(self.middle_name.strip()) > 0:
			result+=' ' + self.middle_name

		result+=' ' + self.last_name

		if self.mothers_last_name and len(self.mothers_last_name.strip()) > 0:
			result+=' ' + self.mothers_last_name

		return result

	@property
	def gender_as_long_string(self):
		if self.gender=='M':
			return _('Male')
		elif self.gender=='F':
			return _('Female')

		return _('Prefer not to say')

	@property
	def dob_fmt_mx(self):
		year = self.dob.year
		month = self.dob.month
		day = self.dob.day
		result = str(day) + '/' + str(month) + '/' + str(year)
		return result

	class Meta:
		# unique_together = [
		# 	('rfc', 'created_by_user')
		# ]

		permissions = (
			(_('Find') + ' [action=#/customers/find]', _('Find')),
			(_('Add') + ' [action=#/customers/add]', _('Add')),
			(_('Edit') + ' [action=#/customers/edit]', _('Edit')),
			(_('Delete') + ' [action=#/customers/delete]', _('Delete')),
		)