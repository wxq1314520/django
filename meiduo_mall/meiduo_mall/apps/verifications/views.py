import random

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from . import serializers
# Create your views here.
from rest_framework.views import APIView
#导入验证码
from django_redis import get_redis_connection

from . import constants
from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.libs.yuntongxun.sms import CCP

class ImageCodeView(APIView):
    """验证码试图类"""
    def get(self,request,image_code_id):
        # 1 .生成验证码
        text,image=captcha.generate_captcha()
        # 2.吧验证码文本信息保存到redis
            #2.1 获取redis操作对象
        redis_conn =get_redis_connection("verify_codes")
            #2.2把验证码保存到redis

        #3 .返回验证码

        redis_conn.setex("img_%s" % image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)

        return  HttpResponse(image,content_type="images/jpg")

class SMSCodeView(GenericAPIView):
    #给当前视图指定序列化器
    serializer_calss=serializers.ImageCodeCheckSerializer

    """短信验证码视图类"""
    def get(self,request,mobile):
        # 1.调用序列化器检查图片验证码
        # data=指定序列化器中的validate中的attrs属性值
        # 通过request.query_params 可以获取到？号后面的查询字符串
        serializer=self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 2.检查是否在60s内有发送记录
        # 3.生成短信验证码与发送记录
        sms_code = "%06d" % random.randint(0, 999999)
        # 4.保存短信验证码与发送记录

        redis_conn=get_redis_connection("verify_codes")
        # 2.2 把验证码保存到redis
        pl=redis_conn.pipline() #获取redis管道对象，redis能使用的操作，管道对象也可以使用
        pl.multi() #有利于提高效率
        # setex("变量名","有效期【秒】"，“值”)
        pl.setex("sms_%s"% mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        # redis 中维护一个send_flag_<mobile>,60
        pl.setex("send_flag_%s" %mobile,constants.SEND_SMS_CODE_INTERVAL,1)
        pl.execute() #吧上面所以的redis操作一起执行
        # 5.发送短信
        time=str(constants.SMS_CODE_REDIS_EXPIRES)
        ccp=CCP()
        ccp.send_template_sms(mobile,[sms_code,time],1)



        return Response({'message':'0k'},status=status.HTTP_200_OK)
