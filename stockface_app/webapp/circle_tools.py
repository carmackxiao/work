# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
from pypebbleapi import Timeline
from models import SequenceNumber, TimelineResourceEn1, TimelineResourceZhongchao
import random
import threading
import time
import json
from datetime import datetime, date, timedelta
from circle_task import send_game_timeline_shared_pin, send_huangli_timeline_shared_pin, delete_timeline_pin, send_news_timeline_shared_pin
from huangli import get_tomorrow_ganzhi, get_huangli_info
from news_parse import get_news_data

def copy_zhongchao_day():
	for item in TimelineResourceZhongchao.objects:
		item.game_day = item.game_time[:10]
		item.save()

def get_huangli_data():
	huangli_riqi = get_huangli_info()
	ganzhi = get_tomorrow_ganzhi()
	
	today = date.today()
	one_day = timedelta(days=1)
	tomorrow = today + one_day

	data_day = tomorrow.strftime('%Y-%m-%d')
	url = 'http://v.juhe.cn/laohuangli/d?date=' + data_day + '&key=bece4b847e35cff9fb2937e4f99d4dd0'
	response = urllib2.urlopen(url)
	data = json.load(response)
	result = data['result']
	
	yinli = result['yinli']
	shenxiao = yinli[2:5]

	body = u'五行:' + result['wuxing'] + '\n\n' + u'宜:' + result['yi'] + '\n\n' + u'忌:' + result['ji'] + '\n\n' + u'冲煞:' + result['chongsha'] + '\n\n' + u'百忌:' + result['baiji'] + '\n\n' + u'吉神:' + result['jishen'] + '\n\n' + u'凶神:' + result['xiongshen'] 

	return [huangli_riqi, body, shenxiao] 


def send_news_timeline():
	today = date.today()
	# one_day = timedelta(days=1)
	# tomorrow = today + one_day

	# pin_id = 'huangli' + today.strftime("%Y%m%d")
	pin_id = 'news' + today.strftime("%Y%m%d")

	# delete_timeline_pin(pin_id)

	pin_time = today.isoformat() + "T01:10:00.000Z"

	title = u'新闻头条'
	news_list = get_news_data()

	subtitle = u'公号:pebblecn'
	body = u'\n\n'.join(news_list)

	print pin_id, pin_time, subtitle, body

	send_news_timeline_shared_pin(pin_id, pin_time, title, subtitle, body)

def send_huangli_timeline():
	today = date.today()
	one_day = timedelta(days=1)
	yesterday = today - one_day
	tomorrow = today + one_day

	# pin_id = 'huangli' + today.strftime("%Y%m%d")
	pin_id = 'huangli' + tomorrow.strftime("%Y%m%d")

	# delete_timeline_pin(pin_id)

	pin_time = tomorrow.isoformat() + "T00:00:00.000Z"

	title = u'黄历宜忌'
	subtitle = u''
	huangli_list = get_huangli_data()

	subtitle = huangli_list[2] + huangli_list[0]
	body = huangli_list[1]

	print pin_id, pin_time, subtitle, body

	send_huangli_timeline_shared_pin(pin_id, pin_time, title, subtitle, body)

def get_zhongchao_data():
	data_day = time.strftime('%Y-%m-%d',time.localtime(time.time()))
	# data_day = '2016-04-09'
	print data_day
	zhongchao_list = parse_zhongchao(data_day)
	print len(zhongchao_list)
	for item in zhongchao_list:
		name_home = item['name_home'][-2:]
		name_away = item['name_away'][-2:]

		if name_home == u'幸福':
			name_home = u'华夏'
		
		if name_away == u'幸福':
			name_away = u'华夏'

		score = item['score']
		status = item['status']

		print score

		scores = score.split('-')
		score_home = ''
		score_away = ''
		if len(scores) > 1:
			score_home = scores[0]
			score_away = scores[1]

		print name_home, name_away
		timeline_resource_list = TimelineResourceZhongchao.objects(name_home=name_home, name_away=name_away, game_day=data_day)
		print len(timeline_resource_list)
		if len(timeline_resource_list) > 0:
			game_data = timeline_resource_list[0]

		
			pin_id = 'zhongchao-'  + str(game_data.resource_id)
			pin_time = None
			title = u'中超联赛'
			subtitle = None
			body = None

			# print name_home, name_away, score_home, score_away
			print status

			if status == u'完场':
				if game_data.game_state != 'game-over':
					print 'game over ' + pin_id
					game_data.score_home = score_home
					game_data.score_away = score_away
					game_data.game_state = 'game-over'
					game_data.save()

					send_game_timeline_shared_pin(pin_id, pin_time, title, subtitle, body, name_home, name_away, score_home, score_away, 'game-over')
			elif status == u'未赛':
				print 'not start'
			else:
				# score change, need notice
				if game_data.score_home != score_home and game_data.score_away != score_away:
					if not (score_home == '0' and score_away == '0'):
						print 'in game ' + pin_id
						game_data.score_home = score_home
						game_data.score_away = score_away
						game_data.game_state = 'in-game'
						game_data.save()
						send_game_timeline_shared_pin(pin_id, pin_time, title, subtitle, body, name_home, name_away, score_home, score_away, 'in-game')


def parse_zhongchao(data_day):
	print 'enter..'
	page = urllib2.urlopen('http://data.sports.sina.com.cn/live/matchlist.php?day=' + data_day)
	soup = BeautifulSoup(page, 'html5lib')
	zhongchao_list = []
	game_list = soup.select('tr[class="213"]')
	for game_item in game_list:
		zhongchao_item = {}

		# get game status
		status_list = game_item.select('td[class="td_4"]')
		for span_list in status_list:
			span_name_list = span_list.select('span')
			for span_name in span_name_list:
				# print span_name.string
				zhongchao_item['status'] = span_name.string

		# get team name list
		team_list = game_item.select('td[class="td_5"]')
		for team_a_list in team_list:
			team_name_list = team_a_list.select('a')
			for team_name in team_name_list:
				zhongchao_item['name_home'] = team_name.string

		team_list = game_item.select('td[class="td_7"]')
		for team_a_list in team_list:
			team_name_list = team_a_list.select('a')
			for team_name in team_name_list:
				zhongchao_item['name_away'] = team_name.string

		# get score list
		score_list = game_item.select('td[class="td_6"]')
		for score_span_item in score_list:
			 score_item_list = score_span_item.select('span')
			 for score_item in score_item_list:
			 	# print score_item.string
			 	zhongchao_item['score'] = score_item.string

		zhongchao_list.append(zhongchao_item)

	return zhongchao_list