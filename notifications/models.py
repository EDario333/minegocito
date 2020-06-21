# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.translation import gettext as _

from catalogues.models import MyModel

class Notifications(MyModel):
	name = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('Task name'), unique=True)
	description = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Description'))
	initial = models.BooleanField(default=False, editable = False, blank=False, null=False)
	#order = models.PositiveSmallIntegerField(default=1, blank=False, null=False)
	icon = models.CharField(max_length=254, default=None, blank=False, null=False)
	bg_color = models.CharField(max_length=30, default='blue-grey', blank=False, null=False, verbose_name=_('Background color icon'))

	class Meta:
		permissions = (
			(_('Find') + ' [action=#/notifs/find]', _('Find')),
			(_('Add') + ' [action=#/notifs/add]', _('Add')),
			(_('Edit') + ' [action=#/notifs/edit]', _('Edit')),
			(_('Delete') + ' [action=#/notifs/delete]', _('Delete')),
		)
		ordering = ['-created_when', '-created_at']

class UsersNotifications(MyModel):
	user = models.ForeignKey('users.Users', on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='user_id', verbose_name=_('To user'))
	notification = models.ForeignKey(Notifications, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='notif_id', verbose_name=_('Notification'))
	done = models.BooleanField(default=False, editable = False, blank=False, null=False)
	obj_name = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('Object name'))
	fully_dropped = models.BooleanField(default=False, editable = False, blank=False, null=False)
	fully_dropped_at = models.TimeField(editable = False, default=None, blank=True, null=True)
	fully_dropped_when = models.DateField(editable = False, default=None, blank=True, null=True)
	fully_dropped_reason = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Specify the reason to drop this object'))

	@property
	def created_when_fmt_mx(self):
		year = self.created_when.year
		month = str(self.created_when.month)
		day = str(self.created_when.day)
		if len(day)<2:
			day='0'+day
		if len(month)<2:
			month='0'+month
		result = str(day) + '/' + str(month) + '/' + str(year)
		return result

	class Meta:
		# unique_together = ('user', 'notification')
		permissions = (
			(_('Find') + ' [action=#/users-notifs/find]', _('Find')),
			(_('Add') + ' [action=#/users-notifs/add]', _('Add')),
			(_('Edit') + ' [action=#/users-notifs/edit]', _('Edit')),
			(_('Delete') + ' [action=#/users-notifs/delete]', _('Delete')),
		)
		ordering = ['-created_when', '-created_at']