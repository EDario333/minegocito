# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms import ModelForm

from django.utils.translation import gettext as _

#from dal import autocomplete

from django.forms.widgets import TextInput

from .models import Shops

class FrmShops(ModelForm):
	title = None
	action = None
	btn_label = None
	icon_btn_submit=None

	def __init__(self, title=None, action=None, btn_label=None, icon_btn_submit=None, *args, **kwargs):
		super(FrmShops, self).__init__(*args, **kwargs)
		self.title = title
		self.action = action
		self.btn_label = btn_label
		self.icon_btn_submit = icon_btn_submit

		self.fields['name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['city'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['admin'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['address_line1'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['address_line2'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['cell_phone'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['home_phone'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['other_phone'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['categories'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0', 'placeholder': _('Examples: hardware store, home store, and so on')}
		self.fields['categories'].label = _('Categories')
		self.fields['categories'].help_text = None

		title_frm = title.upper()

		if 'AGREGAR' in title_frm:
			self.fields['name'].label = '* ' + self.fields['name'].label
			self.fields['city'].label = '* ' + self.fields['city'].label
			self.fields['admin'].label = '* ' + self.fields['admin'].label
			self.fields['address_line1'].label = '* ' + self.fields['address_line1'].label
			self.fields['cell_phone'].label = '* ' + self.fields['cell_phone'].label
			self.fields['categories'].label = '* ' + self.fields['categories'].label
		#elif 'BUSCAR' in title_frm:
		else:
			self.fields['image'].widget.attrs = {'disabled': '', 'style': 'visibility: hidden', 'hidden': ''}
			self.fields['image'].required = False
			self.fields['name'].required = False
			self.fields['city'].required = False
			self.fields['admin'].required = False
			self.fields['address_line1'].required = False
			self.fields['cell_phone'].required = False
			self.fields['categories'].required = False

		'''
		self.fields['dob'].label = '* ' + _('Date of birth')

		self.fields['age'].label = '* ' + _('Age')
		#self.fields['age'].initial = 18
		self.fields['age'].widget.attrs = {'min': 18, 'max': 999, 'maxlength': 3, 'readonly': 'true'}

		self.fields['marital_status'].label = '* ' + _('Marital status')
		self.fields['n_children'].label = '* ' + _('Number of children')
		self.fields['n_children'].widget.attrs = {'min': 0, 'max': 99, 'maxlength': 2}

		self.fields['weight'].label = '* ' + _('Weight')
		self.fields['weight'].widget.attrs = {'min': 1, 'max': 9999999, 'maxlength': 7}

		self.fields['height'].label = '* ' + _('Height')
		self.fields['height'].widget.attrs = {'min': 1, 'max': 9999, 'maxlength': 4}

		self.fields['muscle_mass'].label = '* ' + _('Muscle mass')
		self.fields['muscle_mass'].widget.attrs = {'min': 1, 'max': 9999, 'maxlength': 4}

		self.fields['waist_measurement'].label = '* ' + _('Waist measurement')
		self.fields['waist_measurement'].widget.attrs = {'min': 1, 'max': 9999, 'maxlength': 4}

		self.fields['grade'].label = '* ' + _('Grade')
		self.fields['occupation'].label = '* ' + _('Occupation')
		self.fields['preffered_foods'].label = '* ' + _('Preffered foods')
		self.fields['preffered_drinks'].label = '* ' + _('Preffered drinks')
		'''

	class Meta:
		model = Shops
		exclude = [
			'created_at', 'created_when', 'disabled', 
			'disabled_at', 'disabled_when', 'disabled_reason', 
			'dropped', 'dropped_at', 'dropped_when', 
			'created_by_user', 'dropped_reason'
		]
		widgets = {
			#'age': AdminDateWidget(),
			#'postal_code': autocomplete.Select2(url='locations-autocomplete'),
			#'city': autocomplete.Select2Multiple(url='suggested-colaborators-autocomplete', forward=['researches_lines', 'locations', 'categories', 'tags', 'colaborators'], attrs={'data-html': True}), 
			'city': TextInput(),
			'admin': TextInput(),
		}