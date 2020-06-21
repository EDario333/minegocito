# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.translation import gettext as _

from catalogues.models import \
ObjectWithAddress, \
Person, \
MyModel

class Providers(ObjectWithAddress):
	name = models.CharField(max_length=255, default=None, blank=False, null=False, verbose_name=_('Provider name'))
	rfc = models.CharField(max_length=255, default=None, blank=False, null=False, verbose_name=_('RFC'))
	#contact_person = models.ForeignKey(Person, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='contact_person_id', verbose_name=_('Contact person'))

	class Meta:
		unique_together = [
			('name', 'created_by_user'),
			('rfc', 'created_by_user')
		]
		permissions = (
			(_('Find') + ' [action=#/providers/find]', _('Find')),
			(_('Add') + ' [action=#/providers/add]', _('Add')),
			(_('Edit') + ' [action=#/providers/edit]', _('Edit')),
			(_('Delete') + ' [action=#/providers/delete]', _('Delete')),
		)

# class ProvidersContactPersons(ObjectWithAddress):
class ProvidersContactPersons(MyModel):
	provider = models.ForeignKey(Providers, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='provider_id', verbose_name=_('Provider'))
	contact_person = models.ForeignKey(Person, on_delete=models.PROTECT, default=None, blank=False, null=False, db_column='contact_person_id', verbose_name=_('Contact person'))

	class Meta:
		unique_together = ('provider', 'contact_person')
		# unique_together = ('provider', 'email')