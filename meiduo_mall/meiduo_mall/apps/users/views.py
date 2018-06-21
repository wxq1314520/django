# import random
#
# from django.db.models import constants
# from django.http import HttpResponse
# from django.shortcuts import render
#
# # Create your views here.
# from django_redis import get_redis_connection
# from redis import RedisError
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# from meiduo_mall.meiduo_mall.libs.captcha import captcha
# from meiduo_mall.meiduo_mall.utils.exceptions import logger
#
#
# class ImageCodeView(APIView):
#     """
#     图片验证码
#     """
#     def get(self,request,code_id):
#         """
#         获取图片验证马
#         :param request:
#         :param code_id:
#         :return:
#         """
#         #生成验证码
#         text,image=captcha.generate_captcha()
#         redis_conn=get_redis_connection("verify_codes")
#         redis_conn.setex("img_%s"% code_id,constants.IMAGE_CODE_EXPIRES,text)
#         return HttpResponse(image,content_type="images/jpg")
#
# class SMSCodeView(APIView):
#     """
#     短信验证码
#     """
#
#     def get(self,request,mobile):
#         """
#         创建短信验证码
#         :param request:
#         :param mobile:
#         :return:
#         """
#         #检验图片验证码
#         image_code_id=request.query_params.get("codeId")
#         image_code_text=request.query_params.get("text")
#         if not all([image_code_id,image_code_text]):
#             return Response({"message":"缺少图片验证码"},status=status.HTTP_400_BAD_REQUEST)
#
#         redis_conn=get_redis_connection("verify_codes")
#         try:
#             real_image_code_text=redis_conn.get("img_%s"% image_code_id)
#         except RedisError as e:
#             logger.error(e)
#             return Response({"message":"服务器内部错误"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#
#         # 图片验证码不存在或者已过期
#         if not real_image_code_text:
#             return Response({"message":"无效的图片验证码"},status=status.HTTP_400_BAD_REQUEST)
#
#         # 删除图片验证码
#
#         try:
#             redis_conn.delete("img_%s" %image_code_id)
#         except RedisError as e:
#             logger.error(e)
#
#         # 比较图片验证码是否正确
#         real_image_code_text=real_image_code_text.decode()
#         if real_image_code_text.lower() !=image_code_text.lower():
#             return Response({"message":"图片验证码错误"},status=status.HTTP_400_BAD_REQUEST)
#
#         # 判断是否在60s内
#         redis_conn=get_redis_connection('verify_codes')
#         send_flag=redis_conn.get("send_flag_%s" % mobile)
#         if send_flag:
#             return Response({"message":"请求次数过于频繁"},status=status.HTTP_429_TOO_MANY_REQUESTS)
#
#         # 生成短信验证码与发送记录
#         sms_code="%06d"% random.randint(0,999999)
#
#         # 保存短信验证码与发送记录
#         p1=redis_conn.pipeline()
#         p1.multi()
#         p1.setex("sms_%s"% mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
#         p1.setex("send_flag_%s" % mobile,constants.SEND_SMS_CODE_INTERVAL,1)
#         p1.execute()
#
#
#         # 发送短信验证码
#         sms_code_expires=str(constants.SMS_CODE_REDIS_EXPIRES//60)
#         sms_tasks.send_sms_code.delay(mobile,sms_code,sms_code_expires)
#
#         return Response({"message":"ok"},status.HTTP_200_OK)
