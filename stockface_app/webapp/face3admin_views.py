# -*- coding: utf-8 -*-

from datetime import datetime, date
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from models import ChinaWatchFace3, WatchAccount3, TimelineResourceZhongchao
from task import get_new_sn, send_game_timeline_shared_pin
import json
import threading


# chinaface setting page
def admin(request):
	pwd = request.GET['pwd']
	if pwd != '635241':
		return HttpResponse("wrong")
	context = {'info': ''}
	return render(request, 'webapp/chinaface/face3admin.html', context)

def done(request):
	sn = request.POST['sn']
	context = {'info': sn}
	item = WatchAccount3.objects(sn=sn).first()
	if item:
		item.pay_time = datetime.now()
		item.valid = True
		item.save()
		context['info'] = sn + ' success'
	else:
		context['info'] = sn + ' not found'

	return render_to_response('webapp/chinaface/face3admin.html', context, context_instance=RequestContext(request))

# timeline zhongchao record page
def zhongchao(request):
	pwd = request.GET['pwd']
	if pwd != '635241':
		return HttpResponse("wrong")
	zhongchao_list = TimelineResourceZhongchao.objects().order_by('resource_id')
	context = {'info': '', 'zhongchao_list': zhongchao_list}
	return render(request, 'webapp/chinaface/zhongchao.html', context)

def zhongchao_done(request):
	resource_id = request.POST['resource_id']
	score_home = request.POST['score_home']
	score_away = request.POST['score_away']
	
	context = {'info': resource_id}
	item = TimelineResourceZhongchao.objects(resource_id=resource_id).first()
	if item:
		if len(score_home.strip()) == 0 or len(score_away.strip()) == 0:
			item.score_home = None
			item.score_away = None
			item.game_state = None
			item.save()
		
			pin_id = 'zhongchao-'  + str(item.resource_id)
			pin_time = item.game_time
			title = u'中超联赛'
			subtitle = item.name_away + u'vs' + item.name_home
			print pin_id + ' ' + subtitle
			body = item.name_away + u'vs' + item.name_home + u'\n\n敬请观看!' + u'\n\n啤酒花生!'

			t = threading.Thread(target=send_game_timeline_shared_pin,args=(pin_id, pin_time, title, subtitle, body, item.name_home, item.name_away, False, False))
			t.setDaemon(True)
			t.start()

		else:
			item.score_home = score_home
			item.score_away = score_away
			item.game_state = 'in-game'
			item.save()
		
			pin_id = 'zhongchao-'  + str(item.resource_id)
			pin_time = None
			title = u'中超联赛'
			subtitle = None
			body = None
			name_home = item.name_home
			name_away = item.name_away
			score_home = item.score_home
			score_away = item.score_away

			t = threading.Thread(target=send_game_timeline_shared_pin,args=(pin_id, pin_time, title, subtitle, body, name_home, name_away, score_home, score_away))
			t.setDaemon(True)
			t.start()

			print 'send game'

		context['info'] = resource_id + ' success'
	else:
		context['info'] = resource_id + ' not found'

	zhongchao_list = TimelineResourceZhongchao.objects().order_by('resource_id')
	context = {'info': '', 'zhongchao_list': zhongchao_list}
	return render(request, 'webapp/chinaface/zhongchao.html', context)

def zhongchao_score(request):
	resource_id = request.GET['resource_id']
	item = TimelineResourceZhongchao.objects(resource_id=resource_id)[0]
	context = {'item': item, 'info': ''}
	return render(request, 'webapp/chinaface/zhongchao_score.html', context)

