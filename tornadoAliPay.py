#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import traceback

from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.FileItem import FileItem
from alipay.aop.api.domain.AlipayTradeAppPayModel import AlipayTradeAppPayModel
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.AlipayTradePayModel import AlipayTradePayModel
from alipay.aop.api.domain.GoodsDetail import GoodsDetail
from alipay.aop.api.domain.SettleDetailInfo import SettleDetailInfo
from alipay.aop.api.domain.SettleInfo import SettleInfo
from alipay.aop.api.domain.SubMerchant import SubMerchant
from alipay.aop.api.request.AlipayOfflineMaterialImageUploadRequest import AlipayOfflineMaterialImageUploadRequest
from alipay.aop.api.request.AlipayTradeAppPayRequest import AlipayTradeAppPayRequest
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradePayRequest import AlipayTradePayRequest
from alipay.aop.api.response.AlipayOfflineMaterialImageUploadResponse import AlipayOfflineMaterialImageUploadResponse
from alipay.aop.api.response.AlipayTradePayResponse import AlipayTradePayResponse
import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.options
import tornado.websocket
import tornado.autoreload
import tornado.httpclient
from tornado.httputil import url_concat
#import urllib2
import base64
import os
import hashlib
import time
import json
import struct

import datetime
import logging
import urllib
import urllib.request
##need python3
logging.basicConfig(level=logging.INFO,filename='tornadoAliPay.log')
logger = logging.getLogger('')
#alipay public_key
public_key = 'xxxxx'

"""
设置配置，包括支付宝网关地址、app_id、应用私钥、支付宝公钥等，其他配置值可以查看AlipayClientConfig的定义。
"""
#alipay_client_config = AlipayClientConfig()
alipay_client_config = AlipayClientConfig()
#alipay_client_config.server_url = 'https://openapi.alipay.com/gateway.do'
alipay_client_config.app_id = 'xxxxx'
alipay_client_config.app_private_key = 'xxxxxx'
alipay_client_config.alipay_public_key = 'xxxxx'
alipay_client_config.sign_type = 'RSA'
"""
得到客户端对象。
注意，一个alipay_client_config对象对应一个DefaultAlipayClient，定义DefaultAlipayClient对象后，alipay_client_config不得修改，如果想使用不同的配置，请定义不同的DefaultAlipayClient。
logger参数用于打印日志，不传则不打印，建议传递。
"""
client = DefaultAlipayClient(alipay_client_config=alipay_client_config, logger=logger)


url2 = "xxxxx"
appID = "55"
zoneID = "1"
mcash = "1"
platID = "888"

moneyMap = {"0.01":"1","1":"1","0.99":"6","9.99":"65","29.99":"200","49.99":"340","99.99":"680",".99":"600",}

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("")
class AliPay(tornado.web.RequestHandler):
	def get(self):
		model = AlipayTradeAppPayModel()
		model.timeout_express = "90m"
		model.total_amount = self.get_query_argument('amount', '1')
		#model.seller_id = "9youzl@mail.m818.com"
		model.product_code = self.get_query_argument('product', '1_1_')
		#model.body = "Iphone6 16G"
		model.subject = self.get_query_argument('subject', '1_1_')
		model.out_trade_no = str(int(time.time())) + model.subject
		request = AlipayTradeAppPayRequest(biz_model=model)
		request.notify_url = 'http://xxxxxxx/AliPayOk'
		response = client.sdk_execute(request)
		#response = response.replace('&','&amp')
		#logging.info("alipay.trade.app.pay response:" + response)
		self.write(response)

def check_pay( params):  # 定义检查支付结果的函数
	from alipay.aop.api.util.SignatureUtils import verify_with_rsa
	sign = params.pop('sign', None)  # 取出签名
	print('public_key:')
	print(public_key)
	print('sign:')
	print(sign)
	params.pop('sign_type')  # 取出签名类型
	params = sorted(params.items(), key=lambda e: e[0], reverse=False)  # 取出字典元素按key的字母升序排序形成列表
	message = "&".join(u"{}={}".format(k, v) for k, v in params).encode()  # 将列表转为二进制参数字符串
	print('message:')
	print(message)
	# with open(settings.ALIPAY_PUBLIC_KEY_PATH, 'rb') as public_key: # 打开公钥文件
	try:
		status = verify_with_rsa(public_key, message,sign)  # 验证签名并获取结果
		return status  # 返回验证结果
	except Exception as e:
		# 访问异常的错误编号和详细信息
		print(e.args)
		print(str(e))
		print(repr(e))
		return False

class AliPayOk(tornado.web.RequestHandler):
	def post(self):
		params = self.request.arguments
		logging.info("AliPayOk post")
		logging.info(params)
		params2 = {}
		for key in params.keys():
			params2[key] = params[key][0].decode()
		params = params2
		logging.info("------------------------------------------------------")
		logging.info(params)
		if params["trade_status"] != "TRADE_SUCCESS" and params["trade_status"] != "TRADE_FINISHED":
			logging.info("not success")
			return
		if check_pay(params):
			#TODO ok
			logging.info("check ok")
		else:
			logging.info("check error")
			self.write("failed")
		
	def get(self):
		params = self.request.arguments
		logging.info("AliPayOk get")
		logging.info(params)
		params2 = {}
		for key in params.keys():
			params2[key] = params[key][0].decode()
		params = params2
		logging.info("------------------------------------------------------")
		logging.info(params)
		if params["trade_status"] != "TRADE_SUCCESS" and params["trade_status"] != "TRADE_FINISHED":
			logging.info("not success")
			return
		if check_pay(params):
			logging.info("check ok")
			#TODO ok
		else:
			logging.info("check error")
			self.write("failed")
"""
settings = {
	"static_path": os.path.join(os.path.dirname(__file__), "static"),
	"cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
	"login_url": "/login",
	"xsrf_cookies": True,
}
application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/RechargeRank", RechargeRankHandler),
	(r"/(apple-touch-icon\.html)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
], **settings)
"""
class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/AliPay", AliPay),
			(r"/AliPayOk", AliPayOk),
		]
		settings = dict(
			cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			static_url_prefix = "/static/",
			xsrf_cookies=False,
		)
		tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
	tornado.options.parse_command_line()
	app = Application()
	app.listen(8810)
	loop = tornado.ioloop.IOLoop.instance()
	#tornado.autoreload.watch(r'static\temp.js')
	#tornado.autoreload.start(loop)
	tornado.ioloop.IOLoop.instance().start()
	#application.listen(config.WEB_PORT)
	#tornado.ioloop.IOLoop.instance().start()

