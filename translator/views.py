# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse

from django.utils.translation import gettext as _

def get_msg(request):
  #if request.is_ajax():
    #message = "Yes, AJAX!"
  #else:
    #message = "Not Ajax"
  #return HttpResponse(message)
  if request.method == 'POST':
    return HttpResponse(_(request.POST['msg']))
  elif request.method == 'GET':
    return HttpResponse(_(request.GET['msg']))

  return None

def get_msgs(request):
  result = []

  if request.method == 'POST':
    msgs = request.POST['msgs'].split(',')
    for msg in msgs:
      result.append(_(msg))
      result.append(', ')
  elif request.method == 'GET':
    msgs = request.GET['msgs'].split(',')
    for msg in msgs:
      result.append(_(msg))
      result.append(', ')

  return HttpResponse(result)

def show_toastr_msg(level, msg):
  response = '<script type="text/javascript" src="/static/toastr/toastr.min.js"></script>'
  response += '<script type="text/javascript" src="/static/js/app.js"></script>'
  response += '<script type="text/javascript">'
  #response += 'alert("algo");'
  response += 'show_msg_with_toastr("{}", "{}");'.format(level, msg)
  response += '</script>'
  #return HttpResponse(response)
  return response