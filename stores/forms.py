# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#from django import forms
from django.forms import ModelForm

from django.utils.translation import gettext as _

from django.forms.widgets import TextInput

from .models import Stores

class FrmStores(ModelForm):
	title = None
	action = None
	btn_label = None
	icon_btn_submit=None

	def __init__(self, title=None, action=None, btn_label=None, icon_btn_submit=None, *args, **kwargs):
		super(FrmStores, self).__init__(*args, **kwargs)
		self.title = title
		self.action = action
		self.btn_label = btn_label
		self.icon_btn_submit = icon_btn_submit

		self.fields['shop'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['city'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['admin'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['address_line1'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['address_line2'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['cell_phone'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['home_phone'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['other_phone'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}

		title_frm = title.upper()

		if 'AGREGAR' in title_frm:
			self.fields['shop'].label = '* ' + self.fields['shop'].label
			self.fields['name'].label = '* ' + self.fields['name'].label
			self.fields['city'].label = '* ' + self.fields['city'].label
			self.fields['admin'].label = '* ' + self.fields['admin'].label
			self.fields['address_line1'].label = '* ' + self.fields['address_line1'].label
			self.fields['cell_phone'].label = '* ' + self.fields['cell_phone'].label
		#elif 'BUSCAR' in title_frm:
		else:
			self.fields['shop'].required = False
			self.fields['name'].required = False
			self.fields['city'].required = False
			self.fields['admin'].required = False
			self.fields['address_line1'].required = False
			self.fields['cell_phone'].required = False

	class Meta:
		model = Stores
		fields = [
			'shop', 'name', 'admin', 'city', 'address_line1',
			'address_line2', 'cell_phone', 'home_phone', 
			'other_phone'
		]
		exclude = [
			'created_at', 'created_when', 'disabled', 
			'disabled_at', 'disabled_when', 'disabled_reason', 
			'dropped', 'dropped_at', 'dropped_when', 
			'created_by_user', 'dropped_reason'
		]
		widgets = {
			'shop': TextInput(),
			'city': TextInput(),
			'admin': TextInput(),
		}