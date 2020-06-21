# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import PasswordInput
from django.forms import ModelForm

from django.utils.translation import gettext as _

#from django.forms.widgets import TextInput

from .models import Users

class FrmUsers(ModelForm):
	title = None
	action = None
	btn_label = None
	icon_btn_submit=None

	def __init__(self, title=None, action=None, btn_label=None, icon_btn_submit=None, *args, **kwargs):
		super(FrmUsers, self).__init__(*args, **kwargs)
		self.title = title
		self.action = action
		self.btn_label = btn_label
		self.icon_btn_submit = icon_btn_submit

		self.fields['last_name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['mothers_last_name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['first_name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['middle_name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['email'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['password'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}

		title_frm = title.upper()

		if 'AGREGAR' in title_frm:
			'''
			Note that I must to do the cast to str for each field
			because was raisen the error: 
			"can only concatenate str (not "__proxy__") to str
			'''
			self.fields['last_name'].label = '* ' + _('Last name')
			self.fields['first_name'].label = '* ' + _('First name')
			self.fields['email'].label = '* ' + str(self.fields['email'].label)
			self.fields['password'].label = '* ' + str(self.fields['password'].label)

			self.fields['last_name'].required = True
			self.fields['first_name'].required = True
			self.fields['email'].required = True
		#elif 'BUSCAR' in title_frm:
		elif _('My user profile').upper() not in title_frm:
			self.fields['last_name'].label = _('Last name')
			self.fields['first_name'].label = _('First name')
			self.fields['password'].widget.attrs = {'hidden': 'true', 'style': 'visibility: hidden'}

			self.fields['last_name'].required = False
			self.fields['mothers_last_name'].required = False
			self.fields['first_name'].required = False
			self.fields['middle_name'].required = False
			self.fields['email'].required = False
			self.fields['password'].required = False

	class Meta:
		model = Users
		fields = [
			'last_name', 'mothers_last_name', 'first_name', 
			'middle_name', 'email', 'password'
		]
		exclude = [
			'created_at', 'created_when', 'disabled', 
			'disabled_at', 'disabled_when', 'disabled_reason', 
			'dropped', 'dropped_at', 'dropped_when', 
			'created_by_user', 'dropped_reason', 
			'top_bar_theme'
		]
		widgets = {
			'password': PasswordInput()
		}

class FrmUserProfile(FrmUsers):
	# @property
	# def profile_picture(self):
	# 	return self.fields['profile_picture']

	def __init__(self, title=None, action=None, btn_label=None, icon_btn_submit=None, user=None, *args, **kwargs):
		super(FrmUserProfile, self).__init__(title=title, action=action, btn_label=btn_label, icon_btn_submit=icon_btn_submit, *args, **kwargs)

		self.fields['last_name'].required=True
		self.fields['last_name'].label = '* ' + _('Last name')
		self.fields['first_name'].required=True
		self.fields['first_name'].label = '* ' + _('First name')
		self.fields['email'].required=True
		self.fields['email'].label = '* ' + str(self.fields['email'].label)
		self.fields['password'].required = True
		self.fields['password'].label = '* ' + str(self.fields['password'].label)
		self.fields['profile_picture'].label=''
		self.fields['profile_picture'].widget.attrs = {'style': 'margin: 0 0 10px 0', 'onchange': 'readURL(this);', 'accept': 'image/*'}

		if user is not None:
			self.fields['last_name'].initial=user.last_name
			self.fields['mothers_last_name'].initial=user.mothers_last_name
			self.fields['first_name'].initial=user.first_name
			self.fields['middle_name'].initial=user.middle_name
			self.fields['email'].initial=user.email
			self.fields['password'].initial=''
			#self.fields['profile_picture'].initial=user.profile_picture

	class Meta:
		model = Users
		fields = [
			'profile_picture',
			'last_name', 'mothers_last_name', 'first_name', 
			'middle_name', 'email', 'password'
		]
		widgets = {
			'password': PasswordInput()
		}