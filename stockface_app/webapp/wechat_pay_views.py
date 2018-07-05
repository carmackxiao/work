# -*- coding: utf-8 -*-

from datetime import datetime, date
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import translation
from models import OrderRecord
from circle_models import CircleFace, CircleAccount
from task import get_new_sn, timeline_subscribe, timeline_unsubscribe
import json
import threading
import uuid
from django.views.decorators.csrf import csrf_exempt
from wechat_pay import *

@csrf_exempt
def wxpay_notify(request):
	wxpay_server = Wxpay_server_pub()
	wxpay_server.saveData(request.body)
	post_data = wxpay_server.getData()
	if 'result_code' in post_data and 'return_code' in post_data and 'transaction_id' in post_data:
		if post_data['result_code'] == Wxpay_server_pub.SUCCESS and post_data['return_code'] == Wxpay_server_pub.SUCCESS:
			transaction_id = post_data['transaction_id']
			out_trade_no = post_data['out_trade_no']
			total_fee = post_data['total_fee']
			time_end = post_data['time_end']

			order_query_pub = OrderQuery_pub()
			order_query_pub.setParameter('out_trade_no', out_trade_no)
			order_query_pub.setParameter('transaction_id', transaction_id)
			order_result = order_query_pub.getResult()
			if order_result['return_code'] == Wxpay_server_pub.SUCCESS and order_result['result_code'] == Wxpay_server_pub.SUCCESS and order_result['trade_state'] == Wxpay_server_pub.SUCCESS:
				result_list = OrderRecord.objects(order_id=out_trade_no)
				if len(result_list) > 0:
					order_item = result_list[0]								 
					order_item.transaction_id = transaction_id
					order_item.total_fee = total_fee
					order_item.time_end = time_end
					order_item.save()

					result_list = CircleAccount.objects(sn=order_item.product_id)
					if len(result_list) > 0:
						circle_account_item = result_list[0]
						circle_account_item.valid = True
						circle_account_item.pay_time = datetime.now()
						circle_account_item.save()

	wxpay_server_pub = Wxpay_server_pub()
	wxpay_server_pub.setReturnParameter('return_code', Wxpay_server_pub.SUCCESS)
	wxpay_server_pub.setReturnParameter('return_msg', 'OK')
	return_xml = wxpay_server_pub.returnXml()
	return HttpResponse(return_xml, content_type="application/xml")

@csrf_exempt
def pay_callback(request):
	wxpay_server = Wxpay_server_pub()
	wxpay_server.saveData(request.body)
	post_data = wxpay_server.getData()

	order_record = OrderRecord()
	order_record.order_id = str(uuid.uuid1()).replace('-', '')
	order_record.appid = post_data['appid']
	order_record.openid = post_data['openid']
	order_record.mch_id = post_data['mch_id']
	order_record.is_subscribe = post_data['is_subscribe']
	order_record.nonce_str = post_data['nonce_str']
	order_record.product_id = post_data['product_id']
	order_record.sign = post_data['sign']
	order_record.created_time = datetime.now()
	order_record.save()

	unified_order = UnifiedOrder_pub()
	unified_order.setParameter('body', u'Pebble表盘－“银河石”终身使用权')
	unified_order.setParameter('out_trade_no', order_record.order_id)
	unified_order.setParameter('total_fee', '1000')
	unified_order.setParameter('notify_url', WxPayConf_pub.NOTIFY_URL)
	unified_order.setParameter('trade_type', 'NATIVE')
	unified_order.setParameter('product_id', order_record.product_id)
	unified_order.setParameter('openid', order_record.openid)

	prepay_id = unified_order.getPrepayId()

	wxpay_server_pub = Wxpay_server_pub()
	wxpay_server_pub.setReturnParameter('return_code', Wxpay_server_pub.SUCCESS)
	wxpay_server_pub.setReturnParameter('appid', WxPayConf_pub.APPID)
	wxpay_server_pub.setReturnParameter('mch_id', WxPayConf_pub.MCHID)
	wxpay_server_pub.setReturnParameter('nonce_str', wxpay_server_pub.createNoncestr())
	wxpay_server_pub.setReturnParameter('prepay_id', prepay_id)
	wxpay_server_pub.setReturnParameter('result_code', Wxpay_server_pub.SUCCESS)
	wxpay_server_pub.setReturnParameter('sign', wxpay_server_pub.getSign(wxpay_server_pub.returnParameters))
	return_xml = wxpay_server_pub.returnXml()

	return HttpResponse(return_xml, content_type="application/xml")
