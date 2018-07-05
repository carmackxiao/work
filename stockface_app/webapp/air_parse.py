# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
from pypebbleapi import Timeline
import threading
import time
from datetime import datetime, date, timedelta

def parse_data(fly_day, fly_number):
	fly_day = '20160503'
	fly_number = 'FM926T'
	url = 'http://flights.ctrip.com/actualtime/fno--' + fly_number + '-' + fly_day + '.html'
	print url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.1.14) Gecko/20080404 (FoxPlus) Firefox/2.0.0.14')
	page = urllib2.urlopen(req)
	soup = BeautifulSoup(page, 'html5lib')
	fly_list = soup.select('div[class="detail-fly"]')
	for detail_fly in fly_list:
		print detail_fly

	# 	zhongchao_item = {}

	# 	# get game status
	# 	status_list = game_item.select('td[class="td_4"]')
	# 	for span_list in status_list:
	# 		span_name_list = span_list.select('span')
	# 		for span_name in span_name_list:
	# 			# print span_name.string
	# 			zhongchao_item['status'] = span_name.string

	# 	# get team name list
	# 	team_list = game_item.select('td[class="td_5"]')
	# 	for team_a_list in team_list:
	# 		team_name_list = team_a_list.select('a')
	# 		for team_name in team_name_list:
	# 			zhongchao_item['name_home'] = team_name.string

	# 	team_list = game_item.select('td[class="td_7"]')
	# 	for team_a_list in team_list:
	# 		team_name_list = team_a_list.select('a')
	# 		for team_name in team_name_list:
	# 			zhongchao_item['name_away'] = team_name.string

	# 	# get score list
	# 	score_list = game_item.select('td[class="td_6"]')
	# 	for score_span_item in score_list:
	# 		 score_item_list = score_span_item.select('span')
	# 		 for score_item in score_item_list:
	# 		 	# print score_item.string
	# 		 	zhongchao_item['score'] = score_item.string

	# 	zhongchao_list.append(zhongchao_item)

	# return zhongchao_list