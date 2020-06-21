# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist

from django.forms import ModelForm
from django.forms.widgets import TextInput
from django.forms import Textarea

from django.utils.translation import gettext as _

from .models import Sales

class FrmSales(ModelForm):
	title = None
	action = None
	btn_label = None
	icon_btn_submit=None

	def __init__(self, title=None, action=None, btn_label=None, icon_btn_submit=None, user=None, *args, **kwargs):
		super(FrmSales, self).__init__(*args, **kwargs)
		self.title = title
		self.action = action
		self.btn_label = btn_label
		self.icon_btn_submit = icon_btn_submit

		self.fields['customer'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['identifier'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['sold_at'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['sold_when'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['description'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['notes'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}

		title_frm = title.upper()

		if 'AGREGAR' in title_frm:
			if user is not None:
				try:
					result = Sales.objects.filter(created_by_user=user).latest('identifier')
					try:
						self.fields['identifier'].initial = int(result.identifier)+1
					except ValueError:
						self.fields['identifier'].initial = result.id+1
				except ObjectDoesNotExist:
					self.fields['identifier'].initial = 1

			self.fields['customer'].initial = _('Public') + ' ' + _('General') + ' ' + '[RFC=XXXXXXXXXXX'+str(user.id)+']'
			self.fields['customer'].label = '* ' + self.fields['customer'].label
			self.fields['identifier'].label = '* ' + self.fields['identifier'].label
			#self.fields['sku'].label = '* ' + self.fields['sku'].label
			self.fields['sold_at'].label = '* ' + self.fields['sold_at'].label
			self.fields['sold_when'].label = '* ' + self.fields['sold_when'].label
		else:
			self.fields['customer'].required = False
			self.fields['identifier'].required = False
			#self.fields['sku'].required = False
			self.fields['sold_at'].required = False
			self.fields['sold_when'].required = False
			#self.fields['description'].required = False
			#self.fields['notes'].required = False

	class Meta:
		model = Sales
		fields = [
			'customer', 'identifier', 'sold_at', 'sold_when', 
			'description', 'notes'
		]
		exclude = [
			'created_at', 'created_when', 'disabled', 
			'disabled_at', 'disabled_when', 'disabled_reason', 
			'dropped', 'dropped_at', 'dropped_when', 
			'created_by_user', 'dropped_reason'
		]
		widgets = {
			#'product': TextInput(),
			'customer': TextInput(),
			'description': Textarea(),
			'notes': Textarea()
			#'shop': TextInput(),
			#'store': TextInput(),
		}