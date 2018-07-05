# -*- coding: utf-8 -*-

from pypebbleapi import Timeline
from models import SequenceNumber, TimelineResourceEn1, TimelineResourceZhongchao, TimelineResourceEn2, TimelineTopicRecord, TimelineResourceEn2Chap
import random
import threading
from datetime import datetime, date, timedelta
from circle_key import *

timeline = Timeline(FACE3_TIMELINE_API_KEY)

def make_seq_number():
	while True:
		seq_number = random.randrange(100000, 999999, 1)
		if SequenceNumber.objects(sn=str(seq_number)).count() == 0:
			new_item = SequenceNumber()
			new_item.sn = str(seq_number)
			new_item.save()
			print seq_number
			return

def fill_seq_numbers():
	for i in range(100000, 999999):
		make_seq_number()

def get_new_sn():
	item = SequenceNumber.objects(in_use=False).first()
	item.in_use = True
	item.save()

	return item.sn

def timeline_subscribe(user_token, topic):
	timeline.subscribe(user_token, topic)

def timeline_unsubscribe(user_token, topic):
	timeline.unsubscribe(user_token, topic)

def delete_timeline_pin(pin_id):
	timeline.delete_shared_pin(pin_id)

def delete_timeline_pins():
	for i in range(1, 10):
		pin_id = "english-pin2-" + str(i)
		print pin_id
		timeline.delete_shared_pin(pin_id)

		# pin_id = "english-pin2-" + str(i) + '-1'
		# print pin_id
		# timeline.delete_shared_pin(pin_id)
		
		# pin_id = "english-pin2-" + str(i) + '-2'
		# print pin_id
		# timeline.delete_shared_pin(pin_id)

# def send_zhongchao_timeline_pins():
# 	for item in TimelineResourceZhongchao.objects:

def process_en_chapter():
	i = 1
	chap_id = 1
	body = u""
	for item in TimelineResourceEn2.objects().order_by('resource_id'):
		sentence = item.english_chinese
		if i > 3:
			en_chapter = TimelineResourceEn2Chap()
			en_chapter.chap_id = chap_id
			en_chapter.chap_content = body
			en_chapter.save()

			chap_id = chap_id + 1

			body = u""
			i = 1
		else:
			body = body + sentence + "\n\n"
			i = i + 1


def send_timeline_en_pins_one(pins_list, today):
	if len(pins_list) > 2:
		morning_item = pins_list[0]
		noon_item = pins_list[1]
		even_item = pins_list[2]
		title = u"英语口语"

		pin_id = "english-pin2-" + str(morning_item.chap_id)
		pin_time = today.isoformat() + "T00:00:00.000Z"
		print pin_id
		timeline.delete_shared_pin(pin_id)
		subtitle = u"新的一天"
		body = morning_item.chap_content
		send_timeline_shared_pin(pin_id, pin_time, title, subtitle, body)

		pin_id = "english-pin2-" + str(noon_item.chap_id)
		pin_time = today.isoformat() + "T04:00:00.000Z"
		print pin_id
		timeline.delete_shared_pin(pin_id)
		subtitle = u"吃好点"
		body = noon_item.chap_content
		send_timeline_shared_pin(pin_id, pin_time, title, subtitle, body)

		pin_id = "english-pin2-" + str(even_item.chap_id)
		pin_time = today.isoformat() + "T13:00:00.000Z"
		print pin_id
		timeline.delete_shared_pin(pin_id)
		subtitle = u"早点休息"
		body = even_item.chap_content
		send_timeline_shared_pin(pin_id, pin_time, title, subtitle, body)

def send_timeline_pins_by_day():
	topic_record = TimelineTopicRecord.objects(topic='english')[0]
	index = topic_record.index

	pins_list = TimelineResourceEn2Chap.objects(chap_id__gte=index)[:3]
	topic_record.index = index + 3
	topic_record.save()

	today = date.today()
	send_timeline_en_pins_one(pins_list, today)

def send_timeline_pins():
	i = 1
	body = u""
	pins_list = []
	for item in TimelineResourceEn1.objects:
		sentence = item.english + '\n' + item.chinese
		if i > 3:
			pins_list.append(body)	
			body = u""
			i = 1
		else:
			last_body = body
			body = body + sentence + "\n\n"
			if len(body) > 500:
				body = last_body
			i = i + 1

	chap_id = 0
	i = 1
	today = date.today()
	one_day = timedelta(days=1)
	# today = today + one_day
	pin_time = None
	for item in pins_list[33:]:
		chap_id = chap_id + 1
		pin_id = "english-pin-" + str(chap_id)
		print pin_id
		title = u"英语口语"
		subtitle = u""
		
		timeline.delete_shared_pin(pin_id)

		if i == 1:
			pin_time = today.isoformat() + "T00:00:00.000Z"
			print pin_time + ", " + str(chap_id)
			subtitle = u"新的一天"
			send_timeline_shared_pin(pin_id, pin_time, title, subtitle, item)
			i = i + 1
		elif i == 2:
			pin_time = today.isoformat() + "T04:00:00.000Z"
			print pin_time + ", " + str(chap_id)
			subtitle = u"吃好点"
			send_timeline_shared_pin(pin_id, pin_time, title, subtitle, item)
			i = i + 1
		elif i == 3:
			pin_time = today.isoformat() + "T13:00:00.000Z"
			print pin_time + ", " + str(chap_id)
			subtitle = u"早点休息"
			send_timeline_shared_pin(pin_id, pin_time, title, subtitle, item)
			today = today + one_day
			i = 1


def send_zhongchao_timeline_pins():
	for item in TimelineResourceZhongchao.objects().order_by('resource_id'):
		pin_id = 'zhongchao-'  + str(item.resource_id)
		pin_time = item.game_time
		title = u'中超联赛'
		subtitle = item.name_away + u'vs' + item.name_home
		print pin_id + ' ' + subtitle
		body = item.name_away + u'vs' + item.name_home + u'\n\n敬请观看!' + u'\n\n啤酒花生!'
		send_game_timeline_shared_pin(pin_id, pin_time, title, subtitle, body, item.name_home, item.name_away, False, False, 'start')

def send_test():
	# send_game_timeline_shared_pin('zhongchao-1', '2016-04-20T01:22:00.000Z', u'中超联赛', u'1今晚7:30\n宏运vs恒大', u'2今晚7:30\n宏运vs恒大', u'宏运', u'恒大', u'03', u'00', 'game-over')
	body = u'做个好梦。Sweet dreams! *该句和Good night!一起用于就寝前。一般人均可使用，特别多用于父母对子女。 Don\'t let the bedbugs bite. (晚安。) *bedbugs “臭虫”，直译是“别让臭虫咬了。”但现在没有这种意思，只是睡觉前常用的表达方式之一。 Have pleasant dreams. ' + '\n\n' \
			+ u"另找时间可以吗? How about a rain check? *rain check指“(比赛、活动等)因雨天改期再赛时作为入场券的原票票根”。由因雨天中止或延期比赛而发给观众“rain check”引申为被邀请者因故不能接受邀请，而邀请继续有效的意思，“以后方便的时间”、“下次还有机会”。 Let's do it another time. (再找时间吧。)"
 
	
	send_timeline_shared_pin('english-1', '2016-06-15T06:00:00.000Z', u'english', u'test', body)

def get_utc_time(delta):
	alert_time = datetime.utcnow()
	add = timedelta(seconds=delta)
	alert_time = alert_time + add

	iso_date_str = alert_time.isoformat()
	index = iso_date_str.rfind('.')
	iso_date_str = iso_date_str[0:index] + '.000Z'
	return iso_date_str

def send_game_timeline_shared_pin(pin_id, pin_time, title, subtitle, body, name_home, name_away, score_home, score_away, status):
	topics = ['zhongchao']
	if status == 'in-game':
		# in game
		subtitle = u'比赛进行中\n\n' +  name_away +  u'vs' + name_home
		body = subtitle + u'\n\n' + score_away + u'比' + score_home 
		notice_body = score_away + u'比' + score_home 
		pin_time = get_utc_time(30)
		pin = {'id': pin_id, 'time': pin_time, 'layout': {'type': 'sportsPin', 'title': title, 'subtitle': subtitle, 'body': body, 'tinyIcon': 'system://images/SOCCER_GAME', 'largeIcon': 'system://images/SOCCER_GAME', 'nameHome': name_home, 'nameAway': name_away, 'scoreHome': score_home, 'scoreAway': score_away, 'sportsGameState': "in-game"}, "updateNotification": {'time': pin_time, 'layout': {'type': 'genericNotification', 'tinyIcon': 'system://images/SOCCER_GAME', 'title': title, 'subtitle': subtitle, 'body': notice_body}}}
	elif status == 'game-over': 
		# game over
		subtitle = u'比赛结束\n\n' +  name_away +  u'vs' + name_home
		body = subtitle + u'\n\n' + score_away + u'比' + score_home 
		notice_body = score_away + u'比' + score_home 
		pin_time = get_utc_time(30)
		pin = {'id': pin_id, 'time': pin_time, 'layout': {'type': 'sportsPin', 'title': title, 'subtitle': subtitle, 'body': body, 'tinyIcon': 'system://images/SOCCER_GAME', 'largeIcon': 'system://images/SOCCER_GAME', 'nameHome': name_home, 'nameAway': name_away, 'scoreHome': score_home, 'scoreAway': score_away, 'sportsGameState': "in-game"}, "updateNotification": {'time': pin_time, 'layout': {'type': 'genericNotification', 'tinyIcon': 'system://images/SOCCER_GAME', 'title': title, 'subtitle': subtitle, 'body': notice_body}}}
	else:
		# game not start
		pin = {'id': pin_id, 'time': pin_time, 'layout': {'type': 'sportsPin', 'title': title, 'subtitle': subtitle, 'body': body, 'tinyIcon': 'system://images/SOCCER_GAME', 'largeIcon': 'system://images/SOCCER_GAME', 'nameHome': name_home, 'nameAway': name_away}, "reminders": [{'time': pin_time, 'layout': {'type': 'genericReminder', 'tinyIcon': 'system://images/SOCCER_GAME', 'title': title, 'subtitle': subtitle, 'body': body}}]}

	timeline.send_shared_pin(topics, pin)


def send_news_timeline_shared_pin(pin_id, pin_time, title, subtitle, body):
	topics = ['news']
	pin = {'id': pin_id, 'time': pin_time, 'layout': {'type': 'genericPin', 'title': title, 'subtitle': subtitle, 'body': body,'tinyIcon': 'system://images/NEWS_EVENT'}, "reminders": [{'time': pin_time, 'layout': {'type': 'genericReminder', 'tinyIcon': 'system://images/NEWS_EVENT', 'title': title, 'subtitle': subtitle, 'body': body}}]}
	timeline.send_shared_pin(topics, pin)


def send_timeline_shared_pin(pin_id, pin_time, title, subtitle, body):
	topics = ['english']
	pin = {'id': pin_id, 'time': pin_time, 'layout': {'type': 'genericPin', 'title': title, 'subtitle': subtitle, 'body': body,'tinyIcon': 'system://images/NOTIFICATION_FLAG'}, "reminders": [{'time': pin_time, 'layout': {'type': 'genericReminder', 'tinyIcon': 'system://images/TIMELINE_CALENDAR', 'title': title, 'subtitle': subtitle, 'body': body}}]}
	# pin = {'id': 'english-pin-1', 'time': pin_time, 'layout': {'type': 'genericPin', 'title': title, 'subtitle': subtitle, 'body': u"don't let me down. \n别让我失望。\n\neasy come easy go. \n来得容易，去得快。\n\ni beg your pardon. \n请你原谅。",'tinyIcon': 'system://images/NOTIFICATION_FLAG'}}

	# pin = {'id': 'english-pin0', 'time': '2016-03-18T18:00:00Z', 'layout': {'type': 'genericPin', 'title': 'English Test', 'body': "don't let me down. easy come easy go. i beg your pardon.",'tinyIcon': 'system://images/SCHEDULED_EVENT'}}

	timeline.send_shared_pin(topics, pin)

def send_huangli_timeline_shared_pin(pin_id, pin_time, title, subtitle, body):
	topics = ['huangli']
	pin = {'id': pin_id, 'time': pin_time, 'layout': {'type': 'genericPin', 'title': title, 'subtitle': subtitle, 'body': body,'tinyIcon': 'system://images/TIMELINE_CALENDAR'}}
	timeline.send_shared_pin(topics, pin)

def process_oral_english_file():
	txt_file_name = '/root/work/stockface_web/resource/english/oral_english_8000.txt'
	txt_file = open(txt_file_name, 'r')
	resource_id = 0
	while(True):
		line = txt_file.readline()
		if not line:
			break

		timeline_resource = TimelineResourceEn2()
		timeline_resource.resource_id = resource_id
		timeline_resource.english_chinese = line.strip()
		timeline_resource.created_time = datetime.now
		timeline_resource.save()
		resource_id = resource_id + 1

	txt_file.close()

def process_resource_txt_file():
	txt_file_name = '/Users/carmack/work/stockface_web/resource/english/frequent_english.txt'
	txt_file = open(txt_file_name, 'r')
	while(True):
		line = txt_file.readline()
		if not line:
			break
		english_end_index1 = line.rfind('.')
		english_end_index2 = line.rfind('?')
		english_end_index3 = line.rfind('!')
		max_index = max(english_end_index1, english_end_index2, english_end_index3)
		if max_index > 0:
			chinese = line[max_index + 1:].strip()
			first_index = line.find('.')
			if first_index > 0:
				english = line [first_index + 1: max_index + 1].strip()
				resource_id = int(line[:first_index].strip())
				
				timeline_resource = TimelineResourceEn1()
				timeline_resource.resource_id = resource_id
				timeline_resource.english = english
				timeline_resource.chinese = chinese
				timeline_resource.created_time = datetime.now
				timeline_resource.save()

	txt_file.close()

def process_zhongchao_txt_file():
	# txt_file_name = '/Users/carmack/work/stockface_web/resource/zhongchao/zhongchao.txt'
	txt_file_name = '/root/work/stockface_web/resource/zhongchao/zhongchao.txt'
	txt_file = open(txt_file_name, 'r')
	resource_id = 0
	while(True):
		line = txt_file.readline()
		if not line:
			break
		line = line.strip()
		if len(line) > 0:
			item_list = line.split()
			item_day = item_list[0]
			index = item_day.find('(')
			item_day = '2016-' + item_day[:index]

			item_time = item_list[1]
			if item_time == '19:35':
				item_time = 'T11:35:00.000Z'
			elif item_time == '15:00':
				item_time = 'T07:00:00.000Z'
			elif item_time == '15:30':
				item_time = 'T07:30:00.000Z'
			elif item_time == '16:00':
				item_time = 'T08:00:00.000Z'
			else:
				print 'miss ' + item_time

			item_home_name = item_list[2]
			item_away_name = item_list[4]

			print item_day + '' + item_time + ' ' + item_home_name + ' ' + item_away_name
				
			timeline_resource = TimelineResourceZhongchao()
			timeline_resource.resource_id = resource_id
			timeline_resource.game_time = item_day + '' + item_time
			timeline_resource.name_home = item_home_name
			timeline_resource.name_away = item_away_name

			timeline_resource.created_time = datetime.now
			timeline_resource.save()

			resource_id = resource_id + 1

	txt_file.close()

