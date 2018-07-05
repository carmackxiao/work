# -*- coding: utf-8 -*-

from datetime import datetime, date
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse
from django.template import RequestContext
from circle_models import CircleFace, CircleAccount
import paypalrestsdk

paypalrestsdk.configure({
  # 'mode': 'sandbox', # sandbox
  # 'client_id': 'Aaj3C23U8wKkWLd5HPDJq2WdUw0jlRLtQux62Iqi-RCp3LEJDk9aFusAY-2TP6gl6IaVHcq2fRJuRF_a',
  # 'client_secret': 'EP4ypT4x5_swa2oFAUxG9EP_LLptuq1AaWt_oAkeWA9v9EJz6fisS8imclBgx1RKOH5DoOcOl76TCFNo'
  'mode': 'live', # live
  'client_id': 'AUaMLq35QdpJGYwE4ca23jDe4HMFsCgvbt7kPl_kkhQNGQA92qBM49ue1wZ9WI2abm5yHHoh-b8SAqog',
  'client_secret': 'EKTA0ooD0HkGwcBHGz67gapqyNulHzbE82RZOzJDmITL-KpPh34h2Mv9Sq9PZGFpuuKa0Jw5m4vxht6j'
})

def create_payment(request):
  sn = request.GET['sn']
  payment = paypalrestsdk.Payment({
    'intent': 'sale',
    'redirect_urls': {
      'return_url': 'http://115.28.69.10/webapp/paypal_process',
      'cancel_url': 'http://115.28.69.10/webapp/cancel'
    },    
    'payer': {
      'payment_method': 'paypal',
    },
    'transactions': [{
      'amount': {
          'total': '2.00',
          'currency': 'USD',
          'details': {
            'subtotal': '2.00',
          }
      },
      'description': 'Pebble Galaxy Stone Watchface',

      "item_list": {
        "items":[
          {
            "name":"Pebble Galaxy Stone Watchface",
            "description":"Pebble Galaxy Stone Watchface",
            "quantity":"1",
            "price":"2",
            "currency":"USD",
            "sku": sn
          },
        ],
      }      
    }]
  })

  if payment.create():
    print('Payment created successfully')
    for link in payment.links:
      if link.method == "REDIRECT":
        redirect_url = link.href
        print("Redirect for approval: %s"%(redirect_url))
        return redirect(redirect_url)
  else:
    print(payment.error)
    context = {}
    return render(request, 'webapp/chinaface/paypal_error.html', context)

def paypal_payment_success(request):
    context = {'sn': '123456', 'language': 'en'}
    return render(request, 'webapp/circle/paypal_success.html', context)

def process_payment(request):
    payment_id = request.GET['paymentId']
    player_id = request.GET['PayerID']

    payment = paypalrestsdk.Payment.find(payment_id)
    payment_result = payment.execute({"payer_id": player_id})
    if payment_result:
      payment = paypalrestsdk.Payment.find(payment_id)
      if payment.state == 'approved':
        sku = payment.transactions[0].item_list.items[0].sku
        result_list = CircleAccount.objects(sn=sku)
        if len(result_list) > 0:
          circle_account_item = result_list[0]
          circle_account_item.valid = True
          circle_account_item.pay_time = datetime.now()
          circle_account_item.save()
        
        print("Payment execute successfully")
        context = {'sn': sku}
        return render(request, 'webapp/circle/paypal_success.html', context)
    else:
      print(payment.error)    
      context = {}
      return render(request, 'webapp/circle/paypal_error.html', context)



