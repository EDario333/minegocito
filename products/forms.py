# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import ModelForm
from django.forms.widgets import TextInput

from django.utils.translation import gettext as _

from .models import Products#, ProductsInStores

class FrmProducts(ModelForm):
	title = None
	action = None
	btn_label = None
	icon_btn_submit=None

	def __init__(self, title=None, action=None, btn_label=None, icon_btn_submit=None, *args, **kwargs):
		super(FrmProducts, self).__init__(*args, **kwargs)
		self.title = title
		self.action = action
		self.btn_label = btn_label
		self.icon_btn_submit = icon_btn_submit

		self.fields['name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0', 'placeholder': _('Do not include brand name or any other feature')}

		title_frm = title.upper()

		if 'AGREGAR' in title_frm:
			self.fields['name'].label = '* ' + self.fields['name'].label
		#elif 'BUSCAR' in title_frm:
		else:
			self.fields['name'].required = False

	class Meta:
		model = Products
		fields = [
			'name'
		]
		exclude = [
			'created_at', 'created_when', 'disabled', 
			'disabled_at', 'disabled_when', 'disabled_reason', 
			'dropped', 'dropped_at', 'dropped_when', 
			'created_by_user', 'dropped_reason'
		]
		widgets = {
		}
'''
class FrmProductsInStores(ModelForm):
	title = None
	action = None
	btn_label = None
	icon_btn_submit=None

	def __init__(self, title=None, action=None, btn_label=None, icon_btn_submit=None, *args, **kwargs):
		super(FrmProductsInStores, self).__init__(*args, **kwargs)
		self.title = title
		self.action = action
		self.btn_label = btn_label
		self.icon_btn_submit = icon_btn_submit

		self.fields['product'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0', 'placeholder': _('Do not include brand name or any other feature')}
		self.fields['sku'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['brand'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		#self.fields['shop'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['store'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['quantity'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['price'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}
		self.fields['photo'].widget.attrs = {'style': 'margin: 0 0 10px 0'}

		title_frm = title.upper()

		if 'AGREGAR' in title_frm:
			self.fields['product'].label = '* ' + self.fields['product'].label
			self.fields['sku'].label = '* ' + self.fields['sku'].label
			self.fields['brand'].label = '* ' + self.fields['brand'].label
			#self.fields['shop'].label = '* ' + self.fields['shop'].label
			self.fields['store'].label = '* ' + self.fields['store'].label
			self.fields['quantity'].label = '* ' + self.fields['quantity'].label
			self.fields['price'].label = '* ' + self.fields['price'].label
			#self.fields['photo'].label = '* ' + self.fields['photo'].label
		else:
			self.fields['product'].required = False
			self.fields['sku'].required = False
			self.fields['brand'].required = False
			#self.fields['shop'].required = False
			self.fields['store'].required = False
			self.fields['quantity'].required = False
			self.fields['price'].required = False
			#self.fields['photo'].required = False

	class Meta:
		model = ProductsInStores
		fields = [
			'product', 'sku', 'brand', 'store', 
			'quantity', 'price', 'photo'
		]
		exclude = [
			'created_at', 'created_when', 'disabled', 
			'disabled_at', 'disabled_when', 'disabled_reason', 
			'dropped', 'dropped_at', 'dropped_when', 
			'created_by_user', 'dropped_reason'
		]
		widgets = {
			'product': TextInput(),
			'brand': TextInput(),
			#'shop': TextInput(),
			'store': TextInput(),
		}
'''