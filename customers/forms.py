# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import ModelForm
from django.forms.widgets import TextInput

from django.utils.translation import gettext as _

from .models import Customers

class FrmCustomers(ModelForm):
	title = None
	action = None
	btn_label = None
	icon_btn_submit=None

	def __init__(self, title=None, action=None, btn_label=None, icon_btn_submit=None, *args, **kwargs):
		super(FrmCustomers, self).__init__(*args, **kwargs)
		self.title = title
		self.action = action
		self.btn_label = btn_label
		self.icon_btn_submit = icon_btn_submit

		self.fields['rfc'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['last_name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['mothers_last_name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['first_name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['middle_name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['gender'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['dob'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0', 'placeholder': _('Date format')}
		self.fields['email'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0', 'type': 'email'}
		self.fields['city'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['address_line1'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['address_line2'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['cell_phone'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['home_phone'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['other_phone'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}

		title_frm = title.upper()

		if 'AGREGAR' in title_frm:
			self.fields['rfc'].label = '* ' + self.fields['rfc'].label
			self.fields['last_name'].label = '* ' + self.fields['last_name'].label
			self.fields['first_name'].label = '* ' + self.fields['first_name'].label
			self.fields['gender'].label = '* ' + self.fields['gender'].label
			self.fields['dob'].required=True
			self.fields['dob'].label = '* ' + self.fields['dob'].label
			self.fields['email'].required=True
			self.fields['email'].label = '* ' + self.fields['email'].label
			self.fields['cell_phone'].required=True
			self.fields['cell_phone'].label = '* ' + self.fields['cell_phone'].label
		#elif 'BUSCAR' in title_frm:
		else:
			self.fields['rfc'].required = False
			self.fields['last_name'].required = False
			self.fields['mothers_last_name'].required = False
			self.fields['first_name'].required = False
			self.fields['middle_name'].required = False
			self.fields['gender'].required = False
			self.fields['dob'].required = False
			self.fields['email'].required = False
			self.fields['city'].required = False
			self.fields['address_line1'].required = False
			self.fields['address_line2'].required = False
			self.fields['cell_phone'].required = False
			self.fields['home_phone'].required = False
			self.fields['other_phone'].required = False

	class Meta:
		model = Customers
		fields = [
			'rfc', 'last_name', 'mothers_last_name', 
			'first_name', 'middle_name', 'gender', 'dob', 
			'email', 'city', 'address_line1', 'address_line2',
			'cell_phone', 'home_phone', 'other_phone'
		]
		exclude = [
			'created_at', 'created_when', 'disabled', 
			'disabled_at', 'disabled_when', 'disabled_reason', 
			'dropped', 'dropped_at', 'dropped_when', 
			'created_by_user', 'dropped_reason'
		]
		widgets = {
			'city': TextInput(),
		}