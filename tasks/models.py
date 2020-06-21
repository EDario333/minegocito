# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

#from django.core.exceptions import ObjectDoesNotExist

from django.utils.translation import gettext as _

#from datetime import datetime

#from users.models import Users

from catalogues.models import MyModel

class Tasks(MyModel):
	name = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('Task name'), unique=True)
	description = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Description'))
	initial = models.BooleanField(default=False, editable = False, blank=False, null=False)
	order = models.PositiveSmallIntegerField(default=1, blank=False, null=False)
	url = models.CharField(max_length=1024, default=None, blank=False, null=False, verbose_name=_('URL'), editable=False)

	'''
	users = models.ManyToManyField(
		Users,
		verbose_name=_('users'),
		blank=True,
		related_name="user_set",
		related_query_name="user",
	)
	'''

	class Meta:
		permissions = (
			(_('Find') + ' [action=#/tasks/find]', _('Find')),
			(_('Add') + ' [action=#/tasks/add]', _('Add')),
			(_('Edit') + ' [action=#/tasks/edit]', _('Edit')),
			(_('Delete') + ' [action=#/tasks/delete]', _('Delete')),
		)
		ordering = ['order']
'''
class UsersTasksManager(models.Manager):
	use_in_migrations = True
'''
class UsersTasks(MyModel):
	user = models.ForeignKey('users.Users', on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='user_id', verbose_name=_('To user'))
	task = models.ForeignKey(Tasks, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='task_id', verbose_name=_('Task'))
	percent = models.PositiveSmallIntegerField(default=0, blank=False, null=False, editable=False)
	fully_dropped = models.BooleanField(default=False, editable = False, blank=False, null=False)
	fully_dropped_at = models.TimeField(editable = False, default=None, blank=True, null=True)
	fully_dropped_when = models.DateField(editable = False, default=None, blank=True, null=True)
	fully_dropped_reason = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Specify the reason to drop this object'))

	#objects = UsersTasksManager()

	class Meta:
		unique_together = ('user', 'task')
		permissions = (
			(_('Find') + ' [action=#/users-tasks/find]', _('Find')),
			(_('Add') + ' [action=#/users-tasks/add]', _('Add')),
			(_('Edit') + ' [action=#/users-tasks/edit]', _('Edit')),
			(_('Delete') + ' [action=#/users-tasks/delete]', _('Delete')),
		)