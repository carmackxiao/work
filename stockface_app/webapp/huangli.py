# -*- coding: utf-8 -*-
import time
from datetime import datetime, date, timedelta
import urllib2
from bs4 import BeautifulSoup

def get_huangli_info():
	today = date.today()
	one_day = timedelta(days=1)
	tomorrow = today + one_day

	page_id = tomorrow.strftime("%Y-%m-%d") + '.html'

	url = 'http://www.meiguoshenpo.com/huangli/' + page_id
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.1.14) Gecko/20080404 (FoxPlus) Firefox/2.0.0.14')
	page = urllib2.urlopen(req)
	soup = BeautifulSoup(page, 'html5lib')
	table_list = soup.select('div[id="LEFT_DIV"]')[0](text=u'岁次')
	item = table_list[0]
	huangli_riqi = item.parent.next_sibling.next_sibling.contents[0]
	print huangli_riqi
	return huangli_riqi

def get_tomorrow_gan():
	glist = [u'癸', u'甲', u'乙', u'丙', u'丁', u'戊', u'己', u'庚', u'辛', u'壬']

	today = date.today()
	one_day = timedelta(days=1)
	tomorrow = today + one_day

	c = tomorrow.year / 100
	y = tomorrow.year % 100
	
	m = tomorrow.month
	if m == 1:
		m = 13
	elif m == 2:
		m = 14

	d = tomorrow.day

	g = 4 * c + (c / 4) + 5 * y + (y / 4) + (3 * (m + 1) / 5) + d - 3

	gan_index = g % 10
	gan_name = glist[gan_index]


	print c, y, m, d
	print g, gan_index
	print gan_name
	return gan_name

def get_tomorrow_zhi():
	zlist = [u'亥', u'子', u'丑', u'寅', u'卯', u'辰', u'巳', u'午', u'未', u'申', u'酉', u'戌']

	today = date.today()
	one_day = timedelta(days=1)
	tomorrow = today + one_day

	c = tomorrow.year / 100
	y = tomorrow.year % 100
	
	m = tomorrow.month
	if m == 1:
		m = 13
	elif m == 2:
		m = 14

	d = tomorrow.day

	i = 0
	if m % 2 == 0:
		i = 6

	z = 8 * c + (c / 4) + 5 * y + (y / 4) + (3 * (m + 1) / 5) + d + 7 + i

	zhi_index = z % 12
	zhi_name = zlist[zhi_index]


	print c, y, m, d
	print z, zhi_index
	print zhi_name
	return zhi_name

def get_tomorrow_ganzhi():
	gan = get_tomorrow_gan()
	zhi = get_tomorrow_zhi()
	return gan + zhi + u'日'