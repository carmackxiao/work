from django.conf.urls import url

from . import views, chinaface_views, chinaface3_views, face3admin_views, circle_views, circleadmin_views, wechat_pay_views, paypal_views, treasurebox_views, paypal_treasurebox_views

urlpatterns = [
    # stockface url
    url(r'^$', views.index, name='index'),
    url(r'^save$', views.save, name='save'),
    url(r'^valid$', views.valid, name='valid'),
    url(r'^report$', views.report, name='report'),

    url(r'^privacy_en$', views.privacy_en, name='privacy_en'),
    url(r'^privacy_cn$', views.privacy_cn, name='privacy_cn'),
    url(r'^term_en$', views.term_en, name='term_en'),
    url(r'^term_use_en$', views.term_use_en, name='term_use_en'),

    # weather
    url(r'^weather$', views.weather, name='weather'),
    # chinaface url
    url(r'^chinawatchface_valid$', chinaface_views.chinawatchface_valid, name='chinawatchface_valid'),
    url(r'^chinaface_setting$', chinaface_views.setting, name='chinaface_setting'),
    url(r'^chinaface_save$', chinaface_views.save, name='chinaface_save'),
    url(r'^account_valid$', chinaface_views.account_valid, name='account_valid'),

    # chinaface3 url
    url(r'^chinaface3_valid$', chinaface3_views.chinaface_valid, name='chinaface3_valid'),
    url(r'^chinaface3_setting$', chinaface3_views.setting, name='chinaface3_setting'),
    url(r'^chinaface3_save$', chinaface3_views.save, name='chinaface3_save'),
    url(r'^account3_valid$', chinaface3_views.account_valid, name='account3_valid'),

    # treasurebox
    url(r'^treasurebox_setting$', treasurebox_views.setting, name='treasurebox_setting'),
    url(r'^treasurebox_save$', treasurebox_views.save, name='treasurebox_save'),
    url(r'^treasurebox_expired$', treasurebox_views.expired, name='treasurebox_expired'),

    # circle watch face url
    url(r'^circle_setting$', circle_views.setting, name='circle_setting'),
    url(r'^circle_save$', circle_views.save, name='circle_save'),
    url(r'^circle_valid$', circle_views.valid, name='circle_valid'),
    url(r'^circle_expired$', circle_views.expired, name='circle_expired'),
    # circle admin url
    url(r'^circleadmin$', circleadmin_views.admin, name='circleadmin'),
    url(r'^circledone$', circleadmin_views.done, name='circledone'),

    # chinaface3 admin url
    url(r'^face3admin$', face3admin_views.admin, name='face3admin'),
    url(r'^face3done$', face3admin_views.done, name='face3done'),
    url(r'^zhongchao$', face3admin_views.zhongchao, name='zhongchao'),
    url(r'^zhongchao_score$', face3admin_views.zhongchao_score, name='zhongchao_score'),
    url(r'^zhongchao_done$', face3admin_views.zhongchao_done, name='zhongchao_done'),

    url(r'^chinafac3_expired$', chinaface3_views.expired, name='chinafac3_expired'),

    # wechat
    url(r'^wechat_pay_callback$', wechat_pay_views.pay_callback, name='wechat_pay_callback'),
    url(r'^wxpay_notify$', wechat_pay_views.wxpay_notify, name='wxpay_notify'),

    # #paypal
    url(r'^paypal_create$', paypal_views.create_payment, name='paypal_create'),
    url(r'^paypal_process$', paypal_views.process_payment, name='paypal_process'),
    url(r'^paypal_payment_success$', paypal_views.paypal_payment_success, name='paypal_payment_success'),

    # #paypal
    url(r'^paypal_treasurebox_create$', paypal_treasurebox_views.create_payment, name='paypal_treasurebox_create'),
    url(r'^paypal_treasurebox_process$', paypal_treasurebox_views.process_payment, name='paypal_treasurebox_process'),
    url(r'^paypal_treasurebox_payment_success$', paypal_treasurebox_views.paypal_payment_success, name='paypal_treasurebox_payment_success'),

]