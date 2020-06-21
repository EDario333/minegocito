# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.translation import gettext as _

from datetime import datetime, timedelta

from users.models import Users

# Create your models here.

class AppVersions(models.Model):
	name = models.CharField(max_length=254, default=None, blank=False, null=False, unique=True)
	description = models.CharField(max_length=1024, default=None, blank=True, null=True)
	price = models.DecimalField(max_digits=5, decimal_places=2, default=None, blank=False, null=False)
	disabled = models.BooleanField(default=False, blank=False, null=False, editable=False)

	class Meta:
		permissions = (
			(_('Find') + ' [action=#/app-versions/find]', _('Find')),
			(_('Add') + ' [action=#/app-versions/add]', _('Add')),
			(_('Edit') + ' [action=#/app-versions/edit]', _('Edit')),
			(_('Delete') + ' [action=#/app-versions/delete]', _('Delete')),
		)

class Features(models.Model):
	name = models.CharField(max_length=254, default=None, blank=False, null=False, unique=True)
	description = models.CharField(max_length=1024, default=None, blank=True, null=True)
	disabled = models.BooleanField(default=False, blank=False, null=False, editable=False)

	class Meta:
		permissions = (
			(_('Find') + ' [action=#/features/find]', _('Find')),
			(_('Add') + ' [action=#/features/add]', _('Add')),
			(_('Edit') + ' [action=#/features/edit]', _('Edit')),
			(_('Delete') + ' [action=#/features/delete]', _('Delete')),
		)

class FeaturesAppVersion(models.Model):
	app_version = models.ForeignKey(AppVersions, on_delete=models.PROTECT, default=None, blank=True, null=True, db_column='app_version_id')
	feature = models.ForeignKey(Features, on_delete=models.PROTECT, default=None, blank=True, null=True, db_column='feature_id')
	description = models.CharField(max_length=1024, blank=False, null=False)
	disabled = models.BooleanField(default=False, blank=False, null=False, editable=False)

	class Meta:
		unique_together = ('app_version', 'feature')
		permissions = (
			(_('Find') + ' [action=#/app-versions-features/find]', _('Find')),
			(_('Add') + ' [action=#/app-versions-features/add]', _('Add')),
			(_('Edit') + ' [action=#/app-versions-features/edit]', _('Edit')),
			(_('Delete') + ' [action=#/app-versions-features/delete]', _('Delete')),
		)

class Payments(models.Model):
	user = models.ForeignKey(Users, on_delete=models.PROTECT, default=None, db_column='user_id', verbose_name=_('User'))
	app = models.ForeignKey(AppVersions, on_delete=models.PROTECT, default=None, db_column='app_version_id')

	quantity = models.PositiveSmallIntegerField(default=1, blank=False, null=False)

	at = models.TimeField(editable = False, default=datetime.now(), blank=False, null=False)
	when = models.DateField(editable = False, default=datetime.now(), blank=False, null=False)

	detail_bank_key = models.CharField(max_length=254, default=None, blank=False, null=False)
	details = models.CharField(max_length=254, default=None, blank=True, null=True)
	comments = models.CharField(max_length=1024, default=None, blank=True, null=True)

	active = True
	expires_at = models.TimeField(editable = False, default=None, blank=False, null=False)
	expires_when = models.DateField(editable = False, default=None, blank=False, null=False)

	'''
	service_expires_at = models.TimeField(editable = False, default=self.at, blank=False, null=False)
	service_expires_when = models.DateField(editable = False, default=self.get_expires_when(), blank=False, null=False)
	'''

	def get_expires_when(self):
		return self.when + timedelta(days=30*self.quantity)

	def get_total_amount(self):
		return self.quantity * self.app.price

	class Meta:
		unique_together = ('user', 'app')
		permissions = (
			(_('Find') + ' [action=#/licenses/find]', _('Find')),
			(_('Add') + ' [action=#/licenses/add]', _('Add')),
			(_('Edit') + ' [action=#/licenses/edit]', _('Edit')),
			(_('Delete') + ' [action=#/licenses/delete]', _('Delete')),
		)