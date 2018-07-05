# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse
import sys, urllib, urllib2, json
from weather_code import weather_code_dict

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

def get_appid():
	return 'de90222088d0723e1ff61c7ff28d5212'

def get_utc_time_by_day(delta):
	alert_time = datetime.utcnow()
	add = timedelta(days=delta)
	alert_time = alert_time + add

	iso_date_str = alert_time.isoformat()
	index = iso_date_str.rfind('.')
	iso_date_str = iso_date_str[0:index] + '.000Z'
	return iso_date_str

def get_wind_deg_name(wind_deg):
	wind_deg_name = ''
	if wind_deg:
		wind_deg_num = float(wind_deg)
		if wind_deg_num >= 348.76 or wind_deg_num < 11.26:
			wind_deg_name = u'北'
		elif wind_deg_num >= 11.26 and wind_deg_num < 33.76:
			wind_deg_name = u'北东北'
		elif wind_deg_num >= 33.76 and wind_deg_num < 56.26:
			wind_deg_name = u'东北'
		elif wind_deg_num >= 56.26 and wind_deg_num < 78.76:
			wind_deg_name = u'东东北'
		elif wind_deg_num >= 78.76 and wind_deg_num < 101.26:
			wind_deg_name = u'东'
		elif wind_deg_num >= 101.26 and wind_deg_num < 123.76:
			wind_deg_name = u'东东南'
		elif wind_deg_num >= 123.76 and wind_deg_num < 146.26:
			wind_deg_name = u'东南'
		elif wind_deg_num >= 146.26 and wind_deg_num < 168.76:
			wind_deg_name = u'南东南'
		elif wind_deg_num >= 168.76 and wind_deg_num < 191.26:
			wind_deg_name = u'南'
		elif wind_deg_num >= 191.26 and wind_deg_num < 213.76:
			wind_deg_name = u'南西南'
		elif wind_deg_num >= 213.76 and wind_deg_num < 236.26:
			wind_deg_name = u'西南'
		elif wind_deg_num >= 236.26 and wind_deg_num < 258.76:
			wind_deg_name = u'西西南'
		elif wind_deg_num >= 258.76 and wind_deg_num < 281.76:
			wind_deg_name = u'西'
		elif wind_deg_num >= 281.76 and wind_deg_num < 303.76:
			wind_deg_name = u'西西北'
		elif wind_deg_num >= 303.76 and wind_deg_num < 326.26:
			wind_deg_name = u'西北'
		elif wind_deg_num >= 326.26 and wind_deg_num < 348.76:
			wind_deg_name = u'北西北'

	return wind_deg_name

def get_wind_speed_name(wind_speed):
	wind_speed_name = ''
	if wind_speed:
		wind_speed_num = float(wind_speed)
		if wind_speed_num >= 0.0 and wind_speed_num < 0.3:
			wind_speed_name = u'无风'
		elif wind_speed_num >= 0.3 and wind_speed_num < 1.6:
			wind_speed_name = u'软风'
		elif wind_speed_num >= 1.6 and wind_speed_num < 3.4:
			wind_speed_name = u'轻风'
		elif wind_speed_num >= 3.4 and wind_speed_num < 5.5:
			wind_speed_name = u'微风'
		elif wind_speed_num >= 5.5 and wind_speed_num < 8.0:
			wind_speed_name = u'和风'
		elif wind_speed_num >= 8.0 and wind_speed_num < 10.8:
			wind_speed_name = u'劲风'
		elif wind_speed_num >= 10.8 and wind_speed_num < 13.9:
			wind_speed_name = u'强风'
		elif wind_speed_num >= 13.9 and wind_speed_num < 17.2:
			wind_speed_name = u'疾风'
		elif wind_speed_num >= 17.2 and wind_speed_num < 20.8:
			wind_speed_name = u'大风'
		elif wind_speed_num >= 20.8 and wind_speed_num < 24.5:
			wind_speed_name = u'烈风'
		elif wind_speed_num >= 24.5 and wind_speed_num < 28.5:
			wind_speed_name = u'狂风'
		elif wind_speed_num >= 28.5 and wind_speed_num < 32.7:
			wind_speed_name = u'暴风'
		elif wind_speed_num >= 32.7:
			wind_speed_name = u'飓风'
	return wind_speed_name

def parse_current_weathermap_data(current_weathermap_data):
	weather_pinyin = ''
	description = ''
	temp = ''
	temp_min = ''
	temp_max = ''
	wind_speed = ''
	wind_deg = ''
	city_name = ''

	weather_dict = {'city_name': '', 'weather_pinyin': '', 'weather_desc': '', 'temp': '', 'wind_speed': '', 'wind_deg': ''}

	city_name = current_weathermap_data.get('name', '')

	weather = current_weathermap_data.get('weather')
	if weather and len(weather) > 0:
		weather_id = weather[0].get('id')
		print weather_id
		weather_pinyin = weather_code_dict.get(str(weather_id))
		print weather_pinyin
		description = weather[0].get('description', '')
		if description:
			description = description.replace(u'，', '')
		print description
	main = current_weathermap_data.get('main')
	if main:
		temp = str(int(round(main.get('temp'))))
		temp_min = str(main.get('temp_min', ''))
		temp_max = str(main.get('temp_max', ''))
	wind = current_weathermap_data.get('wind')
	if wind:
		wind_speed = str(wind.get('speed', ''))
		wind_deg = str(wind.get('deg', ''))

	weather_dict['weather_pinyin'] = weather_pinyin
	weather_dict['weather_desc'] = description
	weather_dict['temp'] = temp
	weather_dict['wind_speed'] = get_wind_speed_name(wind_speed)
	weather_dict['wind_deg'] = get_wind_deg_name(wind_deg)
	weather_dict['city_name'] = city_name

	return weather_dict

def parse_daily_data(daily_data):
	weather_pinyin = ''
	description = ''
	temp_min = ''
	temp_max = ''
	wind_speed = ''
	wind_deg = ''
	weather_dict = {'weather_pinyin': '', 'weather_desc': '', 'temp_min': '', 'temp_max': '', 'temp_scope': '', 'wind_speed': '', 'wind_deg': ''}

	temp = daily_data.get('temp')
	if temp:
		temp_min = str(int(round(temp.get('min'))))
		temp_max = str(int(round(temp.get('max'))))

	weather = daily_data.get('weather')
	if weather and len(weather) > 0:
		weather_id = weather[0].get('id')
		print weather_id
		weather_pinyin = weather_code_dict.get(str(weather_id))
		print weather_pinyin
		description = weather[0].get('description', '')
		if description:
			description = description.replace(u'，', '')

	wind_speed = str(daily_data.get('speed', ''))
	wind_deg = str(daily_data.get('deg', ''))

	weather_dict['temp_min'] = temp_min
	weather_dict['temp_max'] = temp_max
	weather_dict['temp_scope'] = temp_max + u' ~ ' + temp_min + u'℃'
	weather_dict['weather_pinyin'] = weather_pinyin
	weather_dict['weather_desc'] = description
	weather_dict['wind_speed'] = get_wind_speed_name(wind_speed)
	weather_dict['wind_deg'] = get_wind_deg_name(wind_deg)
	return weather_dict

def parse_forecast_weathermap_data(forecast_weathermap_data):
	forcast_list = []
	weather_list = forecast_weathermap_data.get('list')
	if weather_list and len(weather_list) > 3:
		today = weather_list[0]
		tomorrow = weather_list[1]
		two_day = weather_list[2]
		three_day = weather_list[3]

		print '****today***'
		forcast_list.append(parse_daily_data(today))
		print '****tomorrow**'
		forcast_list.append(parse_daily_data(tomorrow))
		print '****two_day****'
		forcast_list.append(parse_daily_data(two_day))
		print '****three_day*****'
		forcast_list.append(parse_daily_data(three_day))
	return forcast_list

def convert_openweathermap_data(location):
	server_url = 'http://api.openweathermap.org/data/2.5'
	current_url = server_url + '/weather'
	forecast_url = server_url + '/forecast/daily'
	current_weathermap_data = get_openweathermap_data(location, current_url)
	forecast_weathermap_data = get_openweathermap_data(location, forecast_url)

	print current_weathermap_data
	print '---------------------------------'
	print forecast_weathermap_data

	# date is fake

	current_weather_dict = parse_current_weathermap_data(current_weathermap_data)
	forcast_list = parse_forecast_weathermap_data(forecast_weathermap_data)
	print forcast_list
	today_weather = forcast_list[0]
	tomorrow_weather = forcast_list[1]
	two_day_weather = forcast_list[2]
	three_day_weather = forcast_list[3]

	unify_result_dict = {'error': 0, 'status': 'success', 'date': '1977-07-02', 'results': [{ \
		'currentCity': current_weather_dict['city_name'], \
		'pm25': '', 'index': [], \
		'weather_data': [ \
			{'date': u'今天 01月01日 (实时：' + current_weather_dict['temp'] + u'℃)', \
				'weather': current_weather_dict['weather_desc'], \
				'wind': current_weather_dict['wind_deg'] + current_weather_dict['wind_speed'], \
				'weather_pinyin': current_weather_dict['weather_pinyin'], \
				'temperature': today_weather['temp_scope']},  \
			{'date': u'周一', \
				'weather': tomorrow_weather['weather_desc'], \
				'wind': tomorrow_weather['wind_deg'] + tomorrow_weather['wind_speed'], \
				'weather_pinyin': tomorrow_weather['weather_pinyin'], \
				'temperature': tomorrow_weather['temp_scope']},  \
			{'date': u'周二', \
				'weather': two_day_weather['weather_desc'], \
				'wind': two_day_weather['wind_deg'] + two_day_weather['wind_speed'], \
				'weather_pinyin': two_day_weather['weather_pinyin'], \
				'temperature': two_day_weather['temp_scope']},  \
			{'date': u'周三', \
				'weather': three_day_weather['weather_desc'], \
				'wind': three_day_weather['wind_deg'] + three_day_weather['wind_speed'], \
				'weather_pinyin': three_day_weather['weather_pinyin'], \
				'temperature': three_day_weather['temp_scope']}  \
		] \
	}]}

	# print current_weather_dict

	print unify_result_dict
	return unify_result_dict


def get_openweathermap_data(location, service_url):
	appid = get_appid()
	if not appid:
		return None

	location = location.replace(' ', '')
	geo_arr = location.split(',')
	lon = '0'
	lat = '0'
	lon_clear = ''
	lat_clear = ''

	if len(geo_arr) == 2:
		lon = geo_arr[0]
		lat = geo_arr[1]
		lon_clear = lon.replace('.', '').replace('-', '')
		lat_clear = lat.replace('.', '').replace('-', '')

	url = service_url + '?q=' + location + '&lang=zh_cn&units=metric' + '&appid=' + appid
	if lon_clear.isdigit() and lat_clear.isdigit():
		url = service_url + '?lon=' + lon + '&lat=' + lat + '&lang=zh_cn&units=metric' + '&appid=' + appid
	
	print url
	req = urllib2.Request(url)
	resp = urllib2.urlopen(req)
	content = resp.read()
	value = json.loads(content) 
	return value 