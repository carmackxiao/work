# -*- coding: utf-8 -*-

from datetime import datetime, date
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from circle_models import CircleFace, CircleAccount
import json
import threading

def admin(request):
	pwd = request.GET['pwd']
	if pwd != '635241':
		return HttpResponse("wrong")
	context = {'info': ''}
	return render(request, 'webapp/circle/circleadmin.html', context)

def done(request):
	sn = request.POST['sn']
	context = {'info': sn}
	item = CircleAccount.objects(sn=sn).first()
	if item:
		item.pay_time = datetime.now()
		item.valid = True
		item.save()
		context['info'] = sn + ' success'
	else:
		context['info'] = sn + ' not found'

	return render_to_response('webapp/circle/circleadmin.html', context, context_instance=RequestContext(request))