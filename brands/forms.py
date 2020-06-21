# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#from django import forms
from django.forms import ModelForm

#from django.utils.translation import gettext as _

from .models import Brands

class FrmBrands(ModelForm):
	title = None
	action = None
	btn_label = None
	icon_btn_submit=None

	def __init__(self, title=None, action=None, btn_label=None, icon_btn_submit=None, *args, **kwargs):
		super(FrmBrands, self).__init__(*args, **kwargs)
		self.title = title
		self.action = action
		self.btn_label = btn_label
		self.icon_btn_submit = icon_btn_submit

		self.fields['name'].widget.attrs = {'class': 'form-control validate', 'style': 'margin: 0 0 10px 0'}

		title_frm = title.upper()

		if 'AGREGAR' in title_frm:
			self.fields['name'].label = '* ' + self.fields['name'].label
		#elif 'BUSCAR' in title_frm:
		else:
			self.fields['name'].required = False

	class Meta:
		model = Brands
		fields = [
			'name'
		]
		exclude = [
			'created_at', 'created_when', 'disabled', 
			'disabled_at', 'disabled_when', 'disabled_reason', 
			'dropped', 'dropped_at', 'dropped_when', 
			'created_by_user', 'dropped_reason'
		]
		'''
		widgets = {
		}
		'''