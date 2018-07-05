from datetime import datetime, date
from django.shortcuts import render
from django.http import HttpResponse
from models import ChinaWatchFace3, WatchAccount3
from task import get_new_sn, timeline_subscribe, timeline_unsubscribe
import json
import threading

def is_expired(created_time):
	start_date = datetime(created_time.year, created_time.month, created_time.day)
	end_date = datetime(date.today().year, date.today().month, date.today().day)
	days = (end_date - start_date).days
	if days > 2:
		return True
	else:
		return False

def expired(request):
	context= {'sn':'123456'}
	return render(request, 'webapp/chinaface/face3_expired.html', context)

# china watch face valid
def account_valid(request):
	account_id = request.GET['account_id']
	timeline_token = None
	version_number = None
	if request.GET.has_key('timeline_token'):
		timeline_token = request.GET['timeline_token']
	if request.GET.has_key('version_number'):
		version_number = request.GET['version_number']
	
	item = WatchAccount3.objects(account_id=account_id).first()
	if item:
		if timeline_token:
			item.timeline_token = timeline_token
			item.save()
		if version_number:
			item.version_number = version_number
			item.save()

		if item.valid:
			if not item.pay_time:
				if is_expired(item.created_time):
					item.expired_time = datetime.now
					item.valid = False
					item.save()
					return HttpResponse("false&" + item.sn)
			return HttpResponse("true")
		else:
			return HttpResponse("false&" + item.sn)
	else:
		item = WatchAccount3()
		item.account_id = account_id
		item.timeline_token = timeline_token
		item.version_number = version_number
		item.sn = get_new_sn()
		item.created_time = datetime.now
		item.save()

	return HttpResponse("true")

# china watch face valid
def chinaface_valid(request):
	watchid = request.GET['watchid']
	item = ChinaWatchFace3.objects(pebble_id=watchid).first()
	if item:
		item.use_time = item.use_time + 1
		item.save()
		if item.valid:
			return HttpResponse("true")
		else:
			return HttpResponse("false&" + item.sn)
	else:
		item = ChinaWatchFace3()
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
	show_custom = False

	if request.GET.has_key('v'):
		version = request.GET['v']
	
	if request.GET.has_key('watch_color'):
		watch_color = request.GET['watch_color']

	if version == '2':
		show_version = False
	if version == '3':
		show_version = False
		show_custom = True
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
	context['show_custom'] = show_custom
	context['version_number'] = False
	context['sn'] = ''
	context['shake_sens'] = '1'
	context['timeline_news_check'] = False
	context['show_second_check'] = False

	item = WatchAccount3.objects(account_id=watchid).first()
	if item:
		context['sn'] = item.sn
		if item.version_number:
			context['version_number'] = item.version_number
		if item.valid:
			if not item.pay_time:
				if is_expired(item.created_time):
					item.expired_time = datetime.now
					item.valid = False
					item.save()

		if not item.valid:
			return render(request, 'webapp/chinaface/face3_expired.html', context)

	chinaface = ChinaWatchFace3.objects(pebble_id=watchid).first()
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
			if len(chinaface.watch_color) > 3:
				# convert old value to defaut 1
				context['watch_color'] = '1'
			else:
				context['watch_color'] = chinaface.watch_color
		else:
			context['watch_color'] = '1'

		if chinaface.bluetooth_alert != None:
			context['bluetooth_alert'] = chinaface.bluetooth_alert
		else:
			context['bluetooth_alert'] = True

		# read info window settings
		if chinaface.countday_check != None:
			context['countday_check'] = chinaface.countday_check
		else:
			context['countday_check'] = False

		if chinaface.mydate_name != None:
			context['mydate_name'] = chinaface.mydate_name

		if chinaface.mydate != None and len(chinaface.mydate) > 6:
			context['mydate'] = chinaface.mydate
		else:
			context['mydate'] = '2016-01-01'

		if chinaface.mytime != None and len(chinaface.mytime) > 4:
			context['mytime'] = chinaface.mytime
		else:
			context['mytime'] = '00:00'

		if chinaface.countday_type != None:
			context['countday_type'] = chinaface.countday_type
		else:
			context['countday_type'] = 'Y'

		if chinaface.note_check != None:
			context['note_check'] = chinaface.note_check
		else:
			context['note_check'] = False

		if chinaface.mytxt1 != None:
			context['mytxt1'] = chinaface.mytxt1

		if chinaface.mytxt2 != None:
			context['mytxt2'] = chinaface.mytxt2

		if chinaface.today_weather_check != None:
			context['today_weather_check'] = chinaface.today_weather_check
		else:
			context['today_weather_check'] = True

		if chinaface.tap_check != None:
			context['tap_check'] = chinaface.tap_check
		else:
			context['tap_check'] = True

		if chinaface.hour24_check != None:
			context['hour24_check'] = chinaface.hour24_check
		else:
			context['hour24_check'] = True

		if chinaface.timeline_english_check != None:
			context['timeline_english_check'] = chinaface.timeline_english_check
		else:
			context['timeline_english_check'] = False

		if chinaface.timeline_zhongchao_check != None:
			context['timeline_zhongchao_check'] = chinaface.timeline_zhongchao_check
		else:
			context['timeline_zhongchao_check'] = False

		if chinaface.timeline_huangli_check != None:
			context['timeline_huangli_check'] = chinaface.timeline_huangli_check
		else:
			context['timeline_huangli_check'] = False

		if chinaface.timeline_news_check != None:
			context['timeline_news_check'] = chinaface.timeline_news_check
		else:
			context['timeline_news_check'] = False

		if chinaface.switch_bw_check != None:
			context['switch_bw_check'] = chinaface.switch_bw_check
		else:
			context['switch_bw_check'] = False

		if chinaface.weather_station != None:
			context['weather_station'] = chinaface.weather_station
		else:
			context['weather_station'] = 'C'

		if chinaface.health_check != None:
			context['health_check'] = chinaface.health_check
		else:
			context['health_check'] = False

		if chinaface.health_value != None:
			context['health_value'] = chinaface.health_value
		else:
			context['health_value'] = ''

		if chinaface.shake_sens != None:
			context['shake_sens'] = chinaface.shake_sens
		else:
			context['shake_sens'] = '1'

		if chinaface.show_second_check != None:
			context['show_second_check'] = chinaface.show_second_check
		else:
			context['show_second_check'] = False

	else:
		context['mydate'] = '2016-01-01'
		context['mytime'] = '00:00'

		context['today_weather_check'] = True
		context['countday_check'] = False
		context['note_check'] = False
		context['health_check'] = False

		context['weather_station'] = 'C'
		context['tap_check'] = True
		context['vibration_period'] = '0'
		context['watch_color'] = '1'
		context['countday_type'] = 'Y'
		context['not_alert'] = True
		context['not_alert_start'] = '19'
		context['not_alert_end'] = '8'
		context['invert_color'] = 'B'
		context['bluetooth_alert'] = True
		context['hour24_check'] = True

		context['switch_bw_check'] = False

		context['timeline_english_check'] = False
		context['timeline_zhongchao_check'] = False
		context['timeline_huangli_check'] = False

	return render(request, 'webapp/chinaface/face3_setting.html', context)


def do_timeline_english_subscribe(watchid, timeline_english_check):
	watch_account = WatchAccount3.objects(account_id=watchid).first()
	if watch_account:
		if watch_account.timeline_token:
			if timeline_english_check:
				timeline_subscribe(watch_account.timeline_token, 'english')
			else:
				timeline_unsubscribe(watch_account.timeline_token, 'english')

def do_timeline_zhongchao_subscribe(watchid, timeline_zhongchao_check):
	watch_account = WatchAccount3.objects(account_id=watchid).first()
	if watch_account:
		if watch_account.timeline_token:
			if timeline_zhongchao_check:
				timeline_subscribe(watch_account.timeline_token, 'zhongchao')
			else:
				timeline_unsubscribe(watch_account.timeline_token, 'zhongchao')

def do_timeline_huangli_subscribe(watchid, timeline_huangli_check):
	watch_account = WatchAccount3.objects(account_id=watchid).first()
	if watch_account:
		if watch_account.timeline_token:
			if timeline_huangli_check:
				timeline_subscribe(watch_account.timeline_token, 'huangli')
			else:
				timeline_unsubscribe(watch_account.timeline_token, 'huangli')

def do_timeline_news_subscribe(watchid, timeline_news_check):
	watch_account = WatchAccount3.objects(account_id=watchid).first()
	if watch_account:
		if watch_account.timeline_token:
			if timeline_news_check:
				timeline_subscribe(watch_account.timeline_token, 'news')
			else:
				timeline_unsubscribe(watch_account.timeline_token, 'news')

def do_timeline_subscribe(watchid, timeline_english_check, timeline_zhongchao_check, timeline_huangli_check, timeline_news_check):
	do_timeline_english_subscribe(watchid, timeline_english_check)
	do_timeline_zhongchao_subscribe(watchid, timeline_zhongchao_check)
	do_timeline_huangli_subscribe(watchid, timeline_huangli_check)
	do_timeline_news_subscribe(watchid, timeline_news_check)

def save(request):
	data = json.loads(request.GET['data'])
	watchid = data['watchid']
	city_name = data['city_name']
	watch_style = data['watch_style']
	invert_color = data['invert_color']
	watch_color = data['watch_color']
	
	# info window settings
	countday_check = data['countday_check']
	mydate_name = data['mydate_name'].strip()
	mydate = data['mydate']
	mytime = data['mytime']
	countday_type = data['countday_type']
	weather_station = data['weather_station']

	note_check = data['note_check']
	mytxt1 = data['mytxt1'].strip()
	mytxt2 = data['mytxt2'].strip()

	today_weather_check = data['today_weather_check']
	health_check = data['health_check']
	health_value = data['health_value']

	timeline_news_check = data['timeline_news_check']
	timeline_english_check = data['timeline_english_check']
	timeline_zhongchao_check = data['timeline_zhongchao_check']
	timeline_huangli_check = data['timeline_huangli_check']

	switch_bw_check = data['switch_bw_check']
	shake_sens = data['shake_sens']

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
	tap_check = data['tap_check']
	hour24_check = data['hour24_check']
	show_second_check = data['show_second_check']


	chinaface = ChinaWatchFace3.objects(pebble_id=watchid).first()
	if not chinaface:
		chinaface = ChinaWatchFace3()
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
	
	chinaface.countday_check = countday_check
	chinaface.mydate_name = mydate_name
	chinaface.mydate = mydate
	chinaface.mytime = mytime
	chinaface.countday_type = countday_type

	chinaface.note_check = note_check
	chinaface.mytxt1 = mytxt1
	chinaface.mytxt2 = mytxt2

	chinaface.today_weather_check = today_weather_check
	chinaface.health_check = health_check
	chinaface.health_value = health_value
	chinaface.tap_check = tap_check
	chinaface.hour24_check = hour24_check
	chinaface.timeline_english_check = timeline_english_check
	chinaface.timeline_zhongchao_check = timeline_zhongchao_check
	chinaface.timeline_huangli_check = timeline_huangli_check
	chinaface.timeline_news_check = timeline_news_check
	chinaface.weather_station = weather_station
	chinaface.switch_bw_check = switch_bw_check
	chinaface.shake_sens = shake_sens
	chinaface.show_second_check = show_second_check

	chinaface.save()

	# do_timeline_subscribe(watchid, timeline_english_check, timeline_zhongchao_check, timeline_huangli_check)

	print '********watchid****'
	print watchid
	print timeline_english_check, timeline_zhongchao_check, timeline_huangli_check

	t = threading.Thread(target=do_timeline_subscribe,args=(watchid, timeline_english_check, timeline_zhongchao_check, timeline_huangli_check, timeline_news_check))
	# t.setDaemon(True)
	t.start()

	return render(request, 'webapp/chinaface/face3_setting.html')