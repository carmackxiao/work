import tools
import circle_tools
import task
import circle_task

def cron_get_zhongchao_data():
	tools.get_zhongchao_data()

def cron_send_huangli_timeline():
	circle_tools.send_huangli_timeline()
	tools.send_huangli_timeline()

def cron_send_news_timeline():
	circle_tools.send_news_timeline()
	tools.send_news_timeline()

def cron_send_timeline_pins_by_day():
	circle_task.send_timeline_pins_by_day()
	task.send_timeline_pins_by_day()
