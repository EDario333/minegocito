# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist

from django.forms import ModelForm
from django.forms.widgets import TextInput
from django.forms import Textarea

from django.utils.translation import gettext as _

from .models import Purchases

class FrmPurchases(ModelForm):
	title = None
	action = None
	btn_label = None
	icon_btn_submit=None

	def __init__(self, title=None, action=None, btn_label=None, icon_btn_submit=None, user=None, *args, **kwargs):
		super(FrmPurchases, self).__init__(*args, **kwargs)
		self.title = title
		self.action = action
		self.btn_label = btn_label
		self.icon_btn_submit = icon_btn_submit

		self.fields['provider'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['identifier'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['purchased_at'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['purchased_when'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		#self.fields['product'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0', 'placeholder': _('Do not include brand name or any other feature')}
		#self.fields['brand'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		#self.fields['store'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		#self.fields['quantity'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0', 'min': '1'}
		#self.fields['purchase_price'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['description'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['notes'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}

		title_frm = title.upper()

		if 'AGREGAR' in title_frm:
			if user is not None:
				try:
					result = Purchases.objects.filter(created_by_user=user).latest('identifier')
					try:
						self.fields['identifier'].initial = int(result.identifier)+1
					except ValueError:
						self.fields['identifier'].initial = result.id+1
				except ObjectDoesNotExist:
					self.fields['identifier'].initial = 1

			self.fields['provider'].label = '* ' + self.fields['provider'].label
			self.fields['identifier'].label = '* ' + self.fields['identifier'].label
			self.fields['purchased_at'].label = '* ' + self.fields['purchased_at'].label
			self.fields['purchased_when'].label = '* ' + self.fields['purchased_when'].label
			#self.fields['product'].label = '* ' + self.fields['product'].label
			#self.fields['brand'].label = '* ' + self.fields['brand'].label
			#self.fields['store'].label = '* ' + self.fields['store'].label
			#self.fields['quantity'].label = '* ' + self.fields['quantity'].label
			#self.fields['purchase_price'].label = '* ' + self.fields['purchase_price'].label
		else:
			self.fields['provider'].required = False
			self.fields['identifier'].required = False
			self.fields['purchased_at'].required = False
			self.fields['purchased_when'].required = False
			#self.fields['product'].required = False
			#self.fields['brand'].required = False
			#self.fields['store'].required = False
			#self.fields['quantity'].required = False
			#self.fields['purchase_price'].required = False
			self.fields['description'].required = False
			self.fields['notes'].required = False

	class Meta:
		model = Purchases
		fields = [
			'provider', 'identifier', 'purchased_at', 
			'purchased_when', 'description', 'notes'
		]
		exclude = [
			'created_at', 'created_when', 'disabled', 
			'disabled_at', 'disabled_when', 'disabled_reason', 
			'dropped', 'dropped_at', 'dropped_when', 
			'created_by_user', 'dropped_reason'
		]
		widgets = {
			#'product': TextInput(),
			'provider': TextInput(),
			'description': Textarea(),
			'notes': Textarea()
			#'shop': TextInput(),
			#'store': TextInput(),
		}