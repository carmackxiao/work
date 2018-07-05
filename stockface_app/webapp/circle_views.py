from datetime import datetime, date
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import translation
from circle_models import CircleFace, CircleAccount
from task import get_new_sn
from circle_task import timeline_subscribe, timeline_unsubscribe
import json
import threading
import time
import os
from django.conf import settings
from wechat_pay import *
import qrcode
from PIL import Image

COLOR_TEMPLATE_DICT = {
	'1': {'KEY_T_BG_COLOR': '000000', 'KEY_T_HOUR_BG_COLOR': '55aaff', 'KEY_T_MINUTE_BG_COLOR': '00ffff', 'KEY_T_SECOND_BG_COLOR': '00ffff', 'KEY_T_CIRCLE_LINE_COLOR': '00ffff', 'KEY_T_CIRCLE_ACTIVE_LINE_COLOR': '00ffff', 'KEY_T_TEXT_COLOR': 'ffffff', 'KEY_T_HOUR_TEXT_COLOR': '000000', 'KEY_T_MINUTE_TEXT_COLOR': '000000', 'KEY_T_BATTERY_COLOR': 'ffffff'},
	'2': {'KEY_T_BG_COLOR': '000000', 'KEY_T_HOUR_BG_COLOR': '00aa55', 'KEY_T_MINUTE_BG_COLOR': '00ff00', 'KEY_T_SECOND_BG_COLOR': '00ff00', 'KEY_T_CIRCLE_LINE_COLOR': '00ff00', 'KEY_T_CIRCLE_ACTIVE_LINE_COLOR': '00ff00', 'KEY_T_TEXT_COLOR': 'ffffff', 'KEY_T_HOUR_TEXT_COLOR': '000000', 'KEY_T_MINUTE_TEXT_COLOR': '000000', 'KEY_T_BATTERY_COLOR': 'ffffff'},
	'3': {'KEY_T_BG_COLOR': '000000', 'KEY_T_HOUR_BG_COLOR': 'ff5500', 'KEY_T_MINUTE_BG_COLOR': 'ffaa00', 'KEY_T_SECOND_BG_COLOR': 'ffaa00', 'KEY_T_CIRCLE_LINE_COLOR': 'ffaa00', 'KEY_T_CIRCLE_ACTIVE_LINE_COLOR': 'ffaa00', 'KEY_T_TEXT_COLOR': 'ffffff', 'KEY_T_HOUR_TEXT_COLOR': '000000', 'KEY_T_MINUTE_TEXT_COLOR': '000000', 'KEY_T_BATTERY_COLOR': 'ffffff'},
	'4': {'KEY_T_BG_COLOR': '000000', 'KEY_T_HOUR_BG_COLOR': 'ff0000', 'KEY_T_MINUTE_BG_COLOR': 'ff5555', 'KEY_T_SECOND_BG_COLOR': 'ff5555', 'KEY_T_CIRCLE_LINE_COLOR': 'ff5555', 'KEY_T_CIRCLE_ACTIVE_LINE_COLOR': 'ff5555', 'KEY_T_TEXT_COLOR': 'ffffff', 'KEY_T_HOUR_TEXT_COLOR': '000000', 'KEY_T_MINUTE_TEXT_COLOR': '000000', 'KEY_T_BATTERY_COLOR': 'ffffff'},
	'5': {'KEY_T_BG_COLOR': '000000', 'KEY_T_HOUR_BG_COLOR': 'aa55ff', 'KEY_T_MINUTE_BG_COLOR': 'aaaaff', 'KEY_T_SECOND_BG_COLOR': 'aaaaff', 'KEY_T_CIRCLE_LINE_COLOR': 'aaaaff', 'KEY_T_CIRCLE_ACTIVE_LINE_COLOR': 'aaaaff', 'KEY_T_TEXT_COLOR': 'ffffff', 'KEY_T_HOUR_TEXT_COLOR': '000000', 'KEY_T_MINUTE_TEXT_COLOR': '000000', 'KEY_T_BATTERY_COLOR': 'ffffff'},
	'6': {'KEY_T_BG_COLOR': '000000', 'KEY_T_HOUR_BG_COLOR': 'ffaa00', 'KEY_T_MINUTE_BG_COLOR': 'ffff00', 'KEY_T_SECOND_BG_COLOR': 'ffff00', 'KEY_T_CIRCLE_LINE_COLOR': 'ffff00', 'KEY_T_CIRCLE_ACTIVE_LINE_COLOR': 'ffff00', 'KEY_T_TEXT_COLOR': 'ffffff', 'KEY_T_HOUR_TEXT_COLOR': '000000', 'KEY_T_MINUTE_TEXT_COLOR': '000000', 'KEY_T_BATTERY_COLOR': 'ffffff'},
	'7': {'KEY_T_BG_COLOR': '000000', 'KEY_T_HOUR_BG_COLOR': '99353f', 'KEY_T_MINUTE_BG_COLOR': 'f1aa86', 'KEY_T_SECOND_BG_COLOR': 'f1aa86', 'KEY_T_CIRCLE_LINE_COLOR': 'f1aa86', 'KEY_T_CIRCLE_ACTIVE_LINE_COLOR': 'f1aa86', 'KEY_T_TEXT_COLOR': 'ffffff', 'KEY_T_HOUR_TEXT_COLOR': '000000', 'KEY_T_MINUTE_TEXT_COLOR': '000000', 'KEY_T_BATTERY_COLOR': 'ffffff'},
	'8': {'KEY_T_BG_COLOR': '000000', 'KEY_T_HOUR_BG_COLOR': '00aaaa', 'KEY_T_MINUTE_BG_COLOR': '55aa55', 'KEY_T_SECOND_BG_COLOR': '55aa55', 'KEY_T_CIRCLE_LINE_COLOR': '55aa55', 'KEY_T_CIRCLE_ACTIVE_LINE_COLOR': '55aa55', 'KEY_T_TEXT_COLOR': 'ffffff', 'KEY_T_HOUR_TEXT_COLOR': '000000', 'KEY_T_MINUTE_TEXT_COLOR': '000000', 'KEY_T_BATTERY_COLOR': 'ffffff'},
}


def is_expired(created_time):
	start_date = datetime(created_time.year, created_time.month, created_time.day)
	end_date = datetime(date.today().year, date.today().month, date.today().day)
	days = (end_date - start_date).days
	if days > 2:
		return True
	else:
		return False

def expired(request):
	context= {'sn':'123456', 'language': 'zh'}
	return render(request, 'webapp/circle/expired.html', context)

def create_qrcode_image(sn):
	time_str = time.strftime("%Y%m%d")
	full_path = os.path.join(settings.MEDIA_ROOT, 'qrcode', time_str)
	print full_path
	if not os.path.exists(full_path):
		os.makedirs(full_path)
	
	native_link_pub = NativeLink_pub()
	native_link_pub.setParameter('product_id', sn)
	long_url_str = native_link_pub.getUrl()

	short_pub = ShortUrl_pub()
	short_pub.setParameter('long_url', long_url_str)
	short_url_str = short_pub.getShortUrl()

	print short_url_str

	img = qrcode.make(short_url_str)
	img.thumbnail((80, 80))

	full_file_name = os.path.join(full_path, sn + '.png')
	img.save(full_file_name)
	save_path = os.path.join('qrcode', time_str, sn + '.png')
	print save_path
	return save_path

# watch face valid
def valid(request):
	print 'come here*****************'
	account_id = request.GET['account_id']
	timeline_token = None
	version_number = None
	if request.GET.has_key('timeline_token'):
		timeline_token = request.GET['timeline_token']
	if request.GET.has_key('version_number'):
		version_number = request.GET['version_number']
	
	item = CircleAccount.objects(account_id=account_id).first()
	if item:
		if timeline_token:
			item.timeline_token = timeline_token
			item.save()
		if version_number:
			item.version_number = version_number
			item.save()
		if not item.qrcode_image_path:
			print 'create qrcode'
			item.qrcode_image_path = create_qrcode_image(item.sn)
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
			return HttpResponse("false&" + item.sn + "&" + item.qrcode_image_path)
	else:
		item = CircleAccount()
		item.account_id = account_id
		item.timeline_token = timeline_token
		item.version_number = version_number
		item.sn = get_new_sn()
		item.created_time = datetime.now
		item.qrcode_image_path = create_qrcode_image(item.sn)
		item.save()

	return HttpResponse("true")

def set_color_from_template(watch_color, context):
	context['bg_color'] = '#' + COLOR_TEMPLATE_DICT[watch_color]['KEY_T_BG_COLOR']
	context['hour_bg_color'] = '#' + COLOR_TEMPLATE_DICT[watch_color]['KEY_T_HOUR_BG_COLOR']
	context['hour_text_color'] = '#' + COLOR_TEMPLATE_DICT[watch_color]['KEY_T_HOUR_TEXT_COLOR']
	context['minute_bg_color'] = '#' + COLOR_TEMPLATE_DICT[watch_color]['KEY_T_MINUTE_BG_COLOR']
	context['second_bg_color'] = '#' + COLOR_TEMPLATE_DICT[watch_color]['KEY_T_SECOND_BG_COLOR']
	context['minute_text_color'] = '#' + COLOR_TEMPLATE_DICT[watch_color]['KEY_T_MINUTE_TEXT_COLOR']
	context['circle_color'] = '#' + COLOR_TEMPLATE_DICT[watch_color]['KEY_T_CIRCLE_LINE_COLOR']
	context['other_text_color'] = '#' + COLOR_TEMPLATE_DICT[watch_color]['KEY_T_TEXT_COLOR']
	context['battery_color'] = '#' + COLOR_TEMPLATE_DICT[watch_color]['KEY_T_BATTERY_COLOR']

# chinaface setting page
def setting(request):
	print '******************'
	print request.LANGUAGE_CODE
	show_version = True
	show_invert_color = False
	version = 1
	watch_color = 'black'
	show_color = False
	show_custom = False
	language = 'en'
	t_unit = 'C'

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

	if request.GET.has_key('language'):
		language = request.GET['language']
		print 'get has language=' + language
	else:
		language = request.LANGUAGE_CODE
		print 'request has language=' + language	

	watchid = request.GET['watchid']
	context = {'watchid': watchid}
	context['weather_station'] = 'C'

	if language:
		if language.startswith('zh') or language.endswith('ZN'):
			language = 'zh'
			t_unit = 'C'
			context['weather_station'] = 'C'
		elif language.startswith('es'):
			language = 'es'
			t_unit = 'F'
			context['weather_station'] = 'Y'
		elif language.startswith('de'):
			language = 'de'
			t_unit = 'F'
			context['weather_station'] = 'Y'
		elif language.startswith('fr'):
			language = 'fr'
			t_unit = 'F'
			context['weather_station'] = 'Y'
		elif language.startswith('it'):
			language = 'it'
			t_unit = 'F'
			context['weather_station'] = 'Y'
		elif language.startswith('pt'):
			language = 'pt'
			t_unit = 'F'
			context['weather_station'] = 'Y'
		else:
			language = 'en'
			t_unit = 'F'
			context['weather_station'] = 'Y'

		translation.activate(language)
		request.LANGUAGE_CODE = translation.get_language()

	context['watch_color_type'] = watch_color
	context['no_alert_range'] = range(0, 24)
	context['show_version'] = show_version
	context['show_invert_color'] = show_invert_color
	context['show_color'] = show_color
	context['show_custom'] = show_custom
	context['version_number'] = False
	context['language'] = language
	context['t_unit'] = t_unit
	context['sn'] = ''
	context['already_pay'] = False
	context['health_value'] = 'MC';
	context['show_nongli_check'] = False
	context['shake_sens'] = '1'
	context['bluetooth_icon'] = 'C'
	context['timeline_news_check'] = False

	set_color_from_template('1', context)

	item = CircleAccount.objects(account_id=watchid).first()
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
			else:
				context['already_pay'] = True

		if not item.valid:
			context['sn'] = item.sn
			return render(request, 'webapp/circle/expired.html', context)

	chinaface = CircleFace.objects(pebble_id=watchid).first()
	if chinaface:
		if chinaface.city_name != None:
			context['city_name'] = chinaface.city_name	
		
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
			set_color_from_template(context['watch_color'], context)
		else:
			context['watch_color'] = '1'

		if chinaface.bg_color != None:
			context['bg_color'] = chinaface.bg_color

		if chinaface.hour_bg_color != None:
			context['hour_bg_color'] = chinaface.hour_bg_color

		if chinaface.hour_text_color != None:
			context['hour_text_color'] = chinaface.hour_text_color

		if chinaface.minute_bg_color != None:
			context['minute_bg_color'] = chinaface.minute_bg_color

		if chinaface.second_bg_color != None:
			context['second_bg_color'] = chinaface.second_bg_color

		if chinaface.minute_text_color != None:
			context['minute_text_color'] = chinaface.minute_text_color

		if chinaface.circle_color != None:
			context['circle_color'] = chinaface.circle_color

		if chinaface.other_text_color != None:
			context['other_text_color'] = chinaface.other_text_color

		if chinaface.battery_color != None:
			context['battery_color'] = chinaface.battery_color


		if chinaface.bluetooth_alert != None:
			context['bluetooth_alert'] = chinaface.bluetooth_alert
		else:
			context['bluetooth_alert'] = True

		if chinaface.bluetooth_icon != None:
			context['bluetooth_icon'] = chinaface.bluetooth_icon
		else:
			context['bluetooth_icon'] = 'C'

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

		if chinaface.weather_station != None:
			context['weather_station'] = chinaface.weather_station
		else:
			context['weather_station'] = 'C'

		if chinaface.health_check != None:
			context['health_check'] = chinaface.health_check
		else:
			context['health_check'] = True

		if chinaface.health_value != None:
			context['health_value'] = chinaface.health_value
		else:
			context['health_value'] = ''

		if chinaface.t_unit != None:
			context['t_unit'] = chinaface.t_unit


		if chinaface.show_temperature_check != None:
			context['show_temperature_check'] = chinaface.show_temperature_check
		else:
			context['show_temperature_check'] = True

		if chinaface.show_day_check != None:
			context['show_day_check'] = chinaface.show_day_check
		else:
			context['show_day_check'] = True

		if chinaface.show_bluetooth_check != None:
			context['show_bluetooth_check'] = chinaface.show_bluetooth_check
		else:
			context['show_bluetooth_check'] = True

		if chinaface.show_battery_check != None:
			context['show_battery_check'] = chinaface.show_battery_check
		else:
			context['show_battery_check'] = True

		if chinaface.show_second_check != None:
			context['show_second_check'] = chinaface.show_second_check
		else:
			context['show_second_check'] = True

		if chinaface.show_nongli_check != None:
			context['show_nongli_check'] = chinaface.show_nongli_check
		else:
			context['show_nongli_check'] = False

		if chinaface.show_aqi_check != None:
			context['show_aqi_check'] = chinaface.show_aqi_check
		else:
			context['show_aqi_check'] = True

		if chinaface.shake_sens != None:
			context['shake_sens'] = chinaface.shake_sens
		else:
			context['shake_sens'] = '1'


		if not request.GET.has_key('change'):
			if chinaface.language != None:
				language = chinaface.language
				context['language'] = chinaface.language
				translation.activate(language)
				request.LANGUAGE_CODE = translation.get_language()
	else:
		context['mydate'] = '2016-01-01'
		context['mytime'] = '00:00'

		context['countday_check'] = False
		context['note_check'] = False

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

		context['timeline_english_check'] = False
		context['timeline_zhongchao_check'] = False
		context['timeline_huangli_check'] = False

		context['show_temperature_check'] = True
		context['today_weather_check'] = True
		context['health_check'] = True
		context['show_day_check'] = True
		context['show_bluetooth_check'] = True
		context['show_battery_check'] = True
		context['show_second_check'] = True
		context['show_aqi_check'] = True

	return render(request, 'webapp/circle/setting.html', context)


def do_timeline_english_subscribe(watchid, timeline_english_check):
	watch_account = CircleAccount.objects(account_id=watchid).first()
	if watch_account:
		if watch_account.timeline_token:
			if timeline_english_check:
				timeline_subscribe(watch_account.timeline_token, 'english')
			else:
				timeline_unsubscribe(watch_account.timeline_token, 'english')

def do_timeline_zhongchao_subscribe(watchid, timeline_zhongchao_check):
	watch_account = CircleAccount.objects(account_id=watchid).first()
	if watch_account:
		if watch_account.timeline_token:
			if timeline_zhongchao_check:
				timeline_subscribe(watch_account.timeline_token, 'zhongchao')
			else:
				timeline_unsubscribe(watch_account.timeline_token, 'zhongchao')

def do_timeline_huangli_subscribe(watchid, timeline_huangli_check):
	watch_account = CircleAccount.objects(account_id=watchid).first()
	if watch_account:
		if watch_account.timeline_token:
			if timeline_huangli_check:
				timeline_subscribe(watch_account.timeline_token, 'huangli')
			else:
				timeline_unsubscribe(watch_account.timeline_token, 'huangli')

def do_timeline_news_subscribe(watchid, timeline_news_check):
	watch_account = CircleAccount.objects(account_id=watchid).first()
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
	language = data['language']
	t_unit = data['t_unit']

	show_temperature_check = data['show_temperature_check']
	show_day_check = data['show_day_check']
	show_bluetooth_check = data['show_bluetooth_check']
	show_battery_check = data['show_battery_check']
	show_second_check = data['show_second_check']
	display_value = data['display_value']
	show_aqi_check = data['show_aqi_check']
	show_nongli_check = data['show_nongli_check']

	bg_color = data['bg_color']
	hour_bg_color = data['hour_bg_color']
	hour_text_color = data['hour_text_color']
	minute_bg_color = data['minute_bg_color']
	second_bg_color = data['second_bg_color']
	minute_text_color = data['minute_text_color']
	circle_color = data['circle_color']
	other_text_color = data['other_text_color']
	battery_color = data['battery_color']
	shake_sens = data['shake_sens']
	bluetooth_icon = data['bluetooth_icon']

	chinaface = CircleFace.objects(pebble_id=watchid).first()
	if not chinaface:
		chinaface = CircleFace()
		chinaface.pebble_id = watchid
		chinaface.sn = get_new_sn()
		chinaface.created_time = datetime.now

	chinaface.city_name = city_name
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
	chinaface.language = language
	chinaface.t_unit = t_unit

	chinaface.show_temperature_check = show_temperature_check
	chinaface.show_day_check = show_day_check
	chinaface.show_bluetooth_check = show_bluetooth_check
	chinaface.show_battery_check = show_battery_check
	chinaface.show_second_check = show_second_check
	chinaface.display_value = display_value
	chinaface.show_aqi_check = show_aqi_check
	chinaface.show_nongli_check = show_nongli_check

	chinaface.bg_color = bg_color
	chinaface.hour_bg_color = hour_bg_color
	chinaface.hour_text_color = hour_text_color
	chinaface.minute_bg_color = minute_bg_color
	chinaface.second_bg_color = second_bg_color
	chinaface.minute_text_color = minute_text_color
	chinaface.circle_color = circle_color
	chinaface.other_text_color = other_text_color
	chinaface.battery_color = battery_color

	chinaface.shake_sens = shake_sens
	chinaface.bluetooth_icon = bluetooth_icon

	chinaface.save()

	t = threading.Thread(target=do_timeline_subscribe,args=(watchid, timeline_english_check, timeline_zhongchao_check, timeline_huangli_check, timeline_news_check))
	t.setDaemon(True)
	t.start()

	return render(request, 'webapp/circle/setting.html')