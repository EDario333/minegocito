# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.utils.translation import gettext as _

from catalogues.models import MyModel

from taggit.managers import TaggableManager

class Brands(MyModel):
	name = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('Brand name'), unique=True)

	class Meta:
		permissions = (
			#(_('Find') + ' [action=#/brands/find]', _('Can view brands')),
			#(_('Add') + ' [action=#/brands/add]', _('Can add brands')),
			#(_('Edit') + ' [action=#/brands/edit]', _('Can edit brands')),
			#(_('Delete') + ' [action=#/brands/delete]', _('Can delete brands')),
			(_('Find') + ' [action=#/brands/find]', _('Find')),
			(_('Add') + ' [action=#/brands/add]', _('Add')),
			(_('Edit') + ' [action=#/brands/edit]', _('Edit')),
			(_('Delete') + ' [action=#/brands/delete]', _('Delete')),
		)