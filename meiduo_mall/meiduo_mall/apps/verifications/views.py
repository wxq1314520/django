
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
#导入验证码
from django_redis import get_redis_connection

from . import constants
from meiduo_mall.libs.captcha.captcha import captcha

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

