# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
from pypebbleapi import Timeline
import threading
import time
from datetime import datetime, date, timedelta

def get_news_data():
	url = 'http://news.163.com'
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.1.14) Gecko/20080404 (FoxPlus) Firefox/2.0.0.14')
	page = urllib2.urlopen(req)
	soup = BeautifulSoup(page, 'html5lib')

	news_list = []
	item_list = soup.select('div[id="js_top_news"]')
	if len(item_list) > 0:
		div_item = item_list[0]
		h2_list = div_item.select('h2')
		for h2_item in h2_list:
			a_list = h2_item.select('a')
			for a_item in a_list:
				a_item_str = a_item.string.replace(' ', '')
				if len(a_item_str) > 3:
					news_list.append(a_item_str)
		ul_list = div_item.select('ul[class="top_news_ul"]')
		for ul_item in ul_list:
			a_list = ul_item.select('a')
			for a_item in a_list:
				a_item_str = a_item.string.replace(' ', '')
				if len(a_item_str) > 3:
					news_list.append(a_item_str)

	# for news_item in news_list:
	# 	print news_item

	return news_list