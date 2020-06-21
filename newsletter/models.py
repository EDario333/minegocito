from django.db import models
from django.utils.translation import gettext as _

from catalogues.models import MyModel

class Subscriptions(MyModel):
	email = models.CharField(max_length=254, default=None, blank=False, null=False, verbose_name=_('Email'), unique=True)