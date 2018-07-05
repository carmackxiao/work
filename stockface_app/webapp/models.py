from mongoengine import *
from datetime import datetime

class UserStock(Document):
	pebble_id = StringField(max_length=256)
	stock_code1 = StringField(max_length=32)
	stock_code2 = StringField(max_length=32)
	stock_code3 = StringField(max_length=32)
	created_time = DateTimeField(default=datetime.now)
	use_time = IntField(default=0)
	valid = BooleanField(default=True)
	already_pay = BooleanField(default=False)	

class ChinaWatchFace3(Document):
	pebble_id = StringField(max_length=256, required=True, unique=True)
	sn = StringField(max_length=18, required=True, unique=True)
	created_time = DateTimeField(default=datetime.now, required=True)
	valid = BooleanField(default=True, required=True)
	pay_time = DateTimeField()
	use_time = IntField(default=0)
	city_name = StringField(max_length=512, required=False)
	watch_style = StringField(max_length=32, required=False)
	vibration_period = IntField(default=0, required=True)
	not_alert = BooleanField(default=True, required=True)
	not_alert_start = IntField(default=19, required=True)
	not_alert_end = IntField(default=8, required=True)
	invert_color = StringField(max_length=4, required=False)
	watch_color = StringField(max_length=8, required=False)
	bluetooth_alert = BooleanField(default=True, required=True)

	countday_check = BooleanField(default=False, required=False)
	mydate_name = StringField(max_length=512, required=False)
	mydate = StringField(max_length=16, required=False)
	mytime = StringField(max_length=16, required=False)
	countday_type = StringField(max_length=4, required=False)

	note_check = BooleanField(default=False, required=False)
	mytxt1 = StringField(max_length=512, required=False)
	mytxt2 = StringField(max_length=512, required=False)

	weather_station = StringField(max_length=4, required=False)

	today_weather_check = BooleanField(default=False, required=False)
	health_check = BooleanField(default=False, required=False)
	health_value = StringField(max_length=128, required=False)
	tap_check = BooleanField(default=True, required=False)
	hour24_check = BooleanField(default=True, required=False)
	timeline_english_check = BooleanField(default=True, required=False)
	timeline_zhongchao_check = BooleanField(default=False, required=False)
	timeline_huangli_check = BooleanField(default=False, required=False)
	timeline_news_check = BooleanField(default=False, required=False)
	switch_bw_check = BooleanField(default=False, required=False)
	shake_sens = StringField(default='1', required=False)
	language = StringField(max_length=128, required=False)
	t_unit = StringField(max_length=16, required=False)
	show_second_check = BooleanField(default=False, required=False)

class WatchAccount3(Document):
	account_id = StringField(max_length=256, required=True, unique=True)
	sn = StringField(max_length=18, required=True, unique=True)
	created_time = DateTimeField(default=datetime.now, required=True)
	expired_time = DateTimeField(required=False)
	valid = BooleanField(default=True, required=True)
	pay_time = DateTimeField()
	timeline_token = StringField(max_length=256, required=False)
	version_number = StringField(max_length=32, required=False)

class TimelineResourceEn1(Document):
	resource_id = IntField(default=0, required=True)
	english = StringField(max_length=512, required=True)
	chinese = StringField(max_length=512, required=True)
	created_time = DateTimeField(default=datetime.now, required=True)

class TimelineResourceEn2(Document):
	resource_id = IntField(default=0, required=True)
	english_chinese = StringField(max_length=512, required=True)
	created_time = DateTimeField(default=datetime.now, required=True)

class TimelineResourceEn2Chap(Document):
	chap_id = IntField(default=1, required=True)
	chap_content = StringField(max_length=1024, required=True)

class TimelineTopicRecord(Document):
	topic = StringField(max_length=64, required=True)
	index = IntField(default=0, required=True)

class TimelineResourceZhongchao(Document):
	resource_id = IntField(default=0, required=True)
	game_time = StringField(max_length=64, required=True)
	name_home = StringField(max_length=512, required=True)
	name_away = StringField(max_length=512, required=True)
	score_home = StringField(max_length=64, required=False)
	score_away = StringField(max_length=64, required=False)
	game_state = StringField(max_length=64, required=False)
	created_time = DateTimeField(default=datetime.now, required=True)
	game_day = StringField(max_length=64, required=False)

class ChinaWatchFace(Document):
	pebble_id = StringField(max_length=256, required=True, unique=True)
	sn = StringField(max_length=18, required=True, unique=True)
	created_time = DateTimeField(default=datetime.now, required=True)
	valid = BooleanField(default=True, required=True)
	pay_time = DateTimeField()
	use_time = IntField(default=0)
	city_name = StringField(max_length=512, required=False)
	watch_style = StringField(max_length=32, required=False)
	vibration_period = IntField(default=0, required=True)
	not_alert = BooleanField(default=True, required=True)
	not_alert_start = IntField(default=19, required=True)
	not_alert_end = IntField(default=8, required=True)
	invert_color = StringField(max_length=4, required=False)
	watch_color = StringField(max_length=8, required=False)
	bluetooth_alert = BooleanField(default=True, required=True)

class WatchAccount(Document):
	account_id = StringField(max_length=256, required=True, unique=True)
	sn = StringField(max_length=18, required=True, unique=True)
	created_time = DateTimeField(default=datetime.now, required=True)
	valid = BooleanField(default=True, required=True)
	pay_time = DateTimeField()

class SequenceNumber(Document):
	sn = StringField(max_length=18, required=True, unique=True)
	in_use = BooleanField(default=False)

class AKStore(Document):
	ak = StringField(max_length=64, required=True)
	day = StringField(max_length=8, required=True)
	use_count = IntField(default=0)
	meta = {
        'indexes': [
        	{'fields': ['ak', 'day'], 'unique': True},
        ],
    }

class OrderRecord(Document):
	order_id = StringField(max_length=128, required=False, unique=True)
	appid = StringField(max_length=128, required=False)
	openid = StringField(max_length=128, required=False)
	mch_id = StringField(max_length=128, required=False)
	is_subscribe = StringField(max_length=128, required=False)
	nonce_str = StringField(max_length=128, required=False)
	product_id = StringField(max_length=128, required=False)
	sign = StringField(max_length=128, required=False)
	transaction_id = StringField(max_length=128, required=False)
	total_fee = IntField(default=0)
	created_time = DateTimeField(default=datetime.now, required=False)
	time_end = StringField(max_length=128, required=False)
	
