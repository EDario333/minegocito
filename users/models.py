# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
#from django.contrib.auth.models import ContentType
#from django.contrib.auth.models import Permission

from django.utils import timezone

from django.utils.translation import gettext as _

import datetime

#from tasks.models import Tasks, UsersTasks

from catalogues.models import MyModel

from utils import utils

import os

class AppMenu:
	app = ''
	icon = ''
	children = []

	def __init__(self, app='', icon='', *args, **kwargs):
		super(AppMenu, self).__init__(*args, **kwargs)
		self.app = app
		self.icon = icon
		self.children = []

class Users(User, MyModel):
	def uploads_dir(instance, filename):
		# We must to create its upload dir...
		path = os.getcwd() + '/static/uploads/users/'
		try:
			os.makedirs(path)
		except OSError:  
			print("Creation of the directory %s failed" % path)
		else:  
			print ("Successfully created the directory %s " % path)
		return path + str(instance.id) + '-filename-' + filename

	mothers_last_name = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Mothers last name'))
	middle_name = models.CharField(max_length=254, default=None, blank=True, null=True, verbose_name=_('Middle name'))

	phishing = models.BooleanField(default=False, editable = False, blank=False, null=False)
	phishing_at = models.TimeField(editable = False, default=None, blank=True, null=True)
	phishing_when = models.DateField(editable = False, default=None, blank=True, null=True)

	#See https://docs.djangoproject.com/en/2.0/ref/models/fields/#django.db.models.DateField for more details
	#created_at = models.TimeField(editable = False, default=datetime.datetime.now())
	#created_when = models.DateField(editable = False, default=datetime.datetime.now())

	email_confirmed = models.BooleanField(default=False, editable=False)
	email_confirmed_at = models.TimeField(editable = False, default=None, blank=True, null=True)
	email_confirmed_when = models.DateField(editable = False, default=None, blank=True, null=True)

	email_approved = models.BooleanField(default=False, editable=False)
	email_approved_at = models.TimeField(editable = False, default=None, blank=True, null=True)
	email_approved_when = models.DateField(editable = False, default=None, blank=True, null=True)

	first_time_login = models.BooleanField(default=False)
	show_dlg_first_tutorial_not_completed = models.BooleanField(default=True)
	first_tutorial_completed = models.BooleanField(default=False)
	current_step_first_tutorial = models.PositiveSmallIntegerField(default=0)
	created_with_fb = models.BooleanField(default=False, editable=False)
	fb_id = models.CharField(max_length=1024, default=None, blank=True, null=True, editable=False)
	created_with_google = models.BooleanField(default=False, editable=False)
	google_id = models.CharField(max_length=1024, default=None, blank=True, null=True, editable=False)

	profile_picture = models.ImageField(default=None, blank=True, null=True, verbose_name=_('Profile picture'), upload_to=uploads_dir, max_length=500)
	top_bar_theme = models.CharField(max_length=50, default='red', blank=False, null=False, editable=False)

	show_tasks = models.BooleanField(default=True, editable=False)
	show_notifications = models.BooleanField(default=True, editable=False)
	automatic_updates = models.BooleanField(default=True, editable=False)

	has_rated = models.BooleanField(default=False, editable=False)

	permissions = None
	menu = None
	plain_password = None

	@property
	def full_name(self):
		result=self.first_name
		if self.middle_name is not None and len(self.middle_name.strip())>0:
			result+=' '+self.middle_name
		result+=' '+self.last_name
		if self.mothers_last_name is not None and len(self.mothers_last_name.strip())>0:
			result+=' '+self.mothers_last_name
		return result
	
	@property
	def static_profile_picture(self):
		result = '/static/imgs/user.png'

		if self.profile_picture.name and self.profile_picture.name is not None and len(self.profile_picture.name) > 0:
			result = self.profile_picture.name[self.profile_picture.name.index('/static'):]

		return result

	def _check_field_value(self, value):
		if value and value is not None and len(value.strip()) > 0:
			return value + ' '
		return ''

	def get_full_name(self):
		result = self._check_field_value(self.first_name)
		result += self._check_field_value(self.middle_name)
		result += self._check_field_value(self.last_name)
		result += self._check_field_value(self.mothers_last_name)

		return result

	def get_expires_free_version(self):
		from datetime import timedelta
		return self.email_approved_when + timedelta(days=15)

	class Meta:
		#app_label = _('Users')
		permissions = (
			(_('Find') + ' [action=#/users/admin/find]', _('Find')),
			(_('Add') + ' [action=#/users/admin/add]', _('Add')),
			(_('Edit') + ' [action=#/users/admin/edit]', _('Edit')),
			(_('Delete') + ' [action=#/users/admin/delete]', _('Delete')),
		)

class UsersAdditionalData(models.Model):
	uad_id = models.AutoField(primary_key=True)
	user = models.OneToOneField(User, on_delete=models.PROTECT, default=None, db_column='user_id', verbose_name=_('User'))

	#city = models.ForeignKey(Cities, on_delete=models.PROTECT, default=None, blank=True, null=True, db_column='city_id', verbose_name=_('City'))

	#city = models.ForeignKey(City, on_delete=models.PROTECT, default=None, blank=True, null=True, db_column='city_id', verbose_name=_('City'))

	#geoname_id = models.TextField(default=None, blank=True, null=True, help_text=_('GeoNames help text'))

	gender = models.CharField(max_length=1, choices=utils.GENDERS, default=None, blank=True, verbose_name=_("Gender"))

	dob = models.DateField(default=None, blank=True, verbose_name=_("Date of birth"), null=True)

	fb = models.CharField(max_length=255, default=None, blank=True, null=True, unique=True, verbose_name=_("FB account"))

	twitter = models.CharField(max_length=255, default=None, blank=True, null=True, unique=True, verbose_name=_("Twitter account"))

	instagram = models.CharField(max_length=255, default=None, blank=True, null=True, unique=True, verbose_name=_("Instagram account"))

	created_at = models.TimeField(editable = False, default=datetime.datetime.now())
	created_when = models.DateField(editable = False, default=datetime.datetime.now())

	#unique_together = ('id', 'city', 'gender', 'dob')
	#unique_together = ('id', 'gender', 'dob')

	class Meta:
		verbose_name = _('User additional data')
		verbose_name_plural = _('Users additional data')
		permissions = (
			(_('Find') + ' [action=#/users-additional-data/admin/find]', _('Find')),
			(_('Add') + ' [action=#/users-additional-data/admin/add]', _('Add')),
			(_('Edit') + ' [action=#/users-additional-data/admin/edit]', _('Edit')),
			(_('Delete') + ' [action=#/users-additional-data/admin/delete]', _('Delete')),
		)

class UsersLoggedIn(models.Model):
	uli_id = models.AutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.PROTECT, default=None, db_column='user_id', verbose_name=_('User'))
	ip = models.GenericIPAddressField()
	user_agent = models.CharField(max_length=1024, default=None, blank=False, null=False, unique=False, verbose_name=_('User agent'))
	csrfmiddlewaretoken = models.CharField(max_length=1024, default=None, blank=False, null=False, unique=False)

	logged_at = models.TimeField(editable = False, default=timezone.now())
	logged_when = models.DateField(editable = False, default=timezone.now())
	active = models.BooleanField(editable = False, default=True)

	disconnected_at = models.TimeField(editable = False, default=None, blank=True, null=True)
	disconnected_when = models.DateField(editable = False, default=None, blank=True, null=True)

	class Meta:
		verbose_name = _('User logged in')
		verbose_name_plural = _('Users logged in')
		permissions = (
			(_('Find') + ' [action=#/users-logged-in/find]', _('Find')),
			(_('Add') + ' [action=#/users-logged-in/add]', _('Add')),
			(_('Edit') + ' [action=#/users-logged-in/edit]', _('Edit')),
			(_('Delete') + ' [action=#/users-logged-in/delete]', _('Delete')),
		)

class Ratings(models.Model):
	user = models.OneToOneField(Users, on_delete=models.PROTECT, default=None, db_column='user_id', verbose_name=_('User'))
	rating = models.PositiveSmallIntegerField(default=None, blank=True, null=True)
	comments = models.CharField(max_length=1024, default=None, blank=True, null=True, verbose_name=_('Comments'))