from django.apps import AppConfig

from django.utils.translation import gettext as _

class UsersConfig(AppConfig):
	name = 'users'
	verbose_name = _('Users')