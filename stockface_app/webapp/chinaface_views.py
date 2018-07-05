from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from models import UserStock, ChinaWatchFace, WatchAccount
from task import get_new_sn
import json

# chinaface 1 and 2 use this view
# china watch face valid
def account_valid(request):
	account_id = request.GET['account_id']
	item = WatchAccount.objects(account_id=account_id).first()
	if item:
		if item.valid:
			return HttpResponse("true")
		else:
			return HttpResponse("false&" + item.sn)
	else:
		item = WatchAccount()
		item.account_id = account_id
		item.sn = get_new_sn()
		item.created_time = datetime.now
		item.save()

	return HttpResponse("true")

# china watch face valid
def chinawatchface_valid(request):
	watchid = request.GET['watchid']
	item = ChinaWatchFace.objects(pebble_id=watchid).first()
	if item:
		item.use_time = item.use_time + 1
		item.save()
		if item.valid:
			return HttpResponse("true")
		else:
			return HttpResponse("false&" + item.sn)
	else:
		item = ChinaWatchFace()
		item.pebble_id = watchid
		item.sn = get_new_sn()
		item.created_time = datetime.now
		item.save()

	return HttpResponse("true")

# chinaface setting page
def setting(request):
	show_version = True
	show_invert_color = False
	version = 1
	watch_color = 'black'
	show_color = False

	if request.GET.has_key('v'):
		version = request.GET['v']
	
	if request.GET.has_key('watch_color'):
		watch_color = request.GET['watch_color']

	if version == '2':
		show_version = False
	if version == '3':
		show_version = False
		if watch_color == 'black':
			show_invert_color = True

	if watch_color == 'color':
		show_color = True
		show_invert_color = False

	watchid = request.GET['watchid']
	context = {'watchid': watchid}
	context['no_alert_range'] = range(0, 24)
	context['show_version'] = show_version
	context['show_invert_color'] = show_invert_color
	context['show_color'] = show_color

	chinaface = ChinaWatchFace.objects(pebble_id=watchid).first()
	if chinaface:
		if chinaface.city_name != None:
			context['city_name'] = chinaface.city_name	
		
		if chinaface.watch_style != None:
			context['watch_style'] = chinaface.watch_style
		else:
			context['watch_style'] = "qinxin"	
		
		if chinaface.vibration_period != None:
			context['vibration_period'] = chinaface.vibration_period
		else:
			context['vibration_period'] = '0'

		if chinaface.not_alert != None:
			context['not_alert'] = chinaface.not_alert
		else:
			context['not_alert'] = True

		if chinaface.not_alert_start != None:
			context['not_alert_start'] = chinaface.not_alert_start
		else:
			context['not_alert_start'] = '19'

		if chinaface.not_alert_end != None:
			context['not_alert_end'] = chinaface.not_alert_end
		else:
			context['not_alert_end'] = '8'

		if chinaface.invert_color != None:
			context['invert_color'] = chinaface.invert_color
		else:
			context['invert_color'] = 'B'

		if chinaface.watch_color != None:
			context['watch_color'] = chinaface.watch_color
		else:
			context['watch_color'] = '#000000'

		if chinaface.bluetooth_alert != None:
			context['bluetooth_alert'] = chinaface.bluetooth_alert
		else:
			context['bluetooth_alert'] = True


	return render(request, 'webapp/chinaface/setting.html', context)

def save(request):
	data = json.loads(request.GET['data'])
	watchid = data['watchid']
	city_name = data['city_name']
	watch_style = data['watch_style']
	invert_color = data['invert_color']
	watch_color = data['watch_color']

	vibration_period = 0
	if data['vibration_period'].strip() != '':
		vibration_period = int(data['vibration_period'])

	not_alert = data['not_alert']

	not_alert_start = 19
	if data['not_alert_start'].strip() != '':
		not_alert_start = int(data['not_alert_start'])

	not_alert_end = 8
	if data['not_alert_end'].strip() != '':
		not_alert_end = int(data['not_alert_end'])

	bluetooth_alert = data['bluetooth_alert']

	chinaface = ChinaWatchFace.objects(pebble_id=watchid).first()
	if not chinaface:
		chinaface = ChinaWatchFace()
		chinaface.pebble_id = watchid
		chinaface.sn = get_new_sn()
		chinaface.created_time = datetime.now

	chinaface.city_name = city_name
	chinaface.watch_style = watch_style
	chinaface.vibration_period = vibration_period
	chinaface.not_alert = not_alert
	chinaface.not_alert_start = not_alert_start
	chinaface.not_alert_end = not_alert_end
	chinaface.invert_color = invert_color
	chinaface.watch_color = watch_color
	chinaface.bluetooth_alert = bluetooth_alert
	chinaface.save()

	return render(request, 'webapp/chinaface/setting.html')