# -*- coding: utf-8 -*-
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from models import UserStock, ChinaWatchFace, AKStore, WatchAccount3
from task import get_new_sn
import sys, urllib, urllib2, json
from weather_view import convert_openweathermap_data

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

def report(request):
	watch3_count = WatchAccount3.objects.count()
	context = {'watch3_count': watch3_count}
	return render(request, 'webapp/report.html', context)

def privacy_en(request):
	context = {}
	return render(request, 'webapp/privacy_en.html', context)

def privacy_cn(request):
	context = {}
	return render(request, 'webapp/privacy_cn.html', context)

def term_use_en(request):
	context = {}
	return render(request, 'webapp/term_use_en.html', context)

def term_en(request):
	price = '$9.99'
	if request.GET.has_key('price'):
		price = request.GET['price']

	context = {'price': price}
	return render(request, 'webapp/term_en.html', context)

# stock code setting page
def index(request):
	watchid = request.GET['watchid']
	context = {'watchid': watchid}

	user_stock = UserStock.objects(pebble_id=watchid).first()
	if user_stock:
		context['stock_code1'] = user_stock.stock_code1	
		context['stock_code2'] = user_stock.stock_code2
		context['stock_code3'] = user_stock.stock_code3	

	for item in UserStock.objects:
		print item.pebble_id

	return render(request, 'webapp/index.html', context)

def valid(request):
	watchid = request.GET['watchid']
	user_stock = UserStock.objects(pebble_id=watchid).first()
	if user_stock:
		user_stock.use_time = user_stock.use_time + 1
		user_stock.save()
		if user_stock.valid:
			return HttpResponse("true")
		else:
			return HttpResponse("false")

	return HttpResponse("true")

def save(request):
	data = json.loads(request.GET['data'])
	watchid = data['watchid']
	stock_code1 = data['stock_code1']
	stock_code2 = data['stock_code2']
	stock_code3 = data['stock_code3']

	user_stock = UserStock.objects(pebble_id=watchid).first()
	if not user_stock:
		user_stock = UserStock()
		user_stock.pebble_id = watchid

	user_stock.stock_code1 = stock_code1
	user_stock.stock_code2 = stock_code2
	user_stock.stock_code3 = stock_code3
	user_stock.save()

	return render(request, 'webapp/index.html')

def get_ak():
	ak_arr = ['rLE5nyrT7BFYQ9ps7Rf3OwjG', 'vGKPih6IQ7fP2Sw8tC4IPYAb', '0an3LuYDTlgwqaAOhcoClqPE', 'P2f3nCbwg5MERTQEB220ayIV', 'BnGe2wsVDWWSjGW9uuQ6HXfj', '0QSBACbFp6iBuhFDa4z5Uj34', 'UbOKXDGXxYZjbOBNpbhjRYKU', '10wcTGNHNsYGZ2WeLF5mDVFo']
	# ak_arr = ['2341234132', '21341234132']

	# first look if have today ak record, if not have, create all ak records
	day = datetime.now().strftime('%Y%m%d')
	if AKStore.objects(day=day).count() == 0:
		for ak in ak_arr:
			ak_item = AKStore()
			ak_item.ak = ak
			ak_item.day = day
			ak_item.save()

	# look today ak which one is less than 4900, get first one
	ak_store = AKStore.objects(day=day, use_count__lte=4900)
	if ak_store.count() > 0:
		ak_item = ak_store[0]
		ak_item.use_count = ak_item.use_count + 1
		ak_item.save()
		return ak_item.ak
	return None

def weather(request):
	location = request.GET['location'].encode('utf-8')
	weather_station = 'C'
	if request.GET.has_key('weather_station'):
		weather_station = request.GET['weather_station']

	content = ''
	if weather_station == 'G':
		openweathermap_data = convert_openweathermap_data(location)
		content = json.dumps(openweathermap_data)
	else:
		ak = get_ak()
		if not ak:
			HttpResponse("no ak")
		
		url = 'http://api.map.baidu.com/telematics/v3/weather?output=json&location=' + location + '&ak=' + ak
		req = urllib2.Request(url)
		resp = urllib2.urlopen(req)
		content = resp.read()

	return HttpResponse(content)  