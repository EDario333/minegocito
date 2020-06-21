# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import gettext as _

UNDEFINED_LBL = _('Prefer not to say')
CHOOSE_ONE_LBL = '-- ' + _('Pick one') + ' --'

GENDERS = (
	(None, CHOOSE_ONE_LBL),
	('', UNDEFINED_LBL),
  ('M', _('Male')),
  ('F', _('Female')),
)

KEYS = ['tbgs1', 'tlyon3_sme', 'thdsrmzdlnegdr', 'uknfcrslf', 'skyngdckmtf']
SERVERS = ['aws', 'gcloud', 'cpython', 'apache', 'dummy']
PROVIDERS = ['es_MX', 'es_ES', 'en_US', 'en_UK', 'es']
IPS = ['local', 'remote', '127.0.0.1', 'ipv4', 'ipv6']
CRIP_UID = ['309160-@UID@d759-01a-uzpz-123lkj', 'abc62k-@UID@dpemc1390kda-84jk-v', 'uer932-@UID@d3ix-u93-021m-coakc4', '3a9c16-@UID@d6p37-e-i5md', 'coak33-@UID@dkd7-hashmd']

def validate_recaptcha(recaptcha_response):
	import json
	import urllib

	url = 'https://www.google.com/recaptcha/api/siteverify'

	values = {
		'secret': '6Ld-f6sUAAAAADULp8SOto55v0gg84N6AzcoS_1A',
		'response': recaptcha_response
	}

	data = urllib.parse.urlencode(values).encode()
	req =  urllib.request.Request(url, data=data)
	response = urllib.request.urlopen(req)

	return json.loads(response.read().decode())

def retrieve_recaptcha_error(error_codes):
	msg = _('reCAPTCHA validation has failed') + '. '
	msg += _('Retry, and if the problem persist get in touch with the system administrator and report')
	msg += ': '

	if 'invalid-input-secret' in error_codes:
		msg += _('The secret parameter is invalid or malformed').lower()

	if 'missing-input-secret' in error_codes:
		msg += ', ' + _('The secret parameter is missing').lower()

	if 'missing-input-response' in error_codes:
		msg += ', ' + _('The response parameter is missing').lower()

	if 'invalid-input-response' in error_codes:
		msg += ', ' + _('The response parameter is invalid or malformed').lower()

	if 'bad-request' in error_codes:
		msg += ', ' + _('The request is invalid or malformed').lower()

	return msg

def get_main_url(request):
	url=request.build_absolute_uri()
	return url[:url.index(request.get_full_path())]