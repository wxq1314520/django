import re

from rest_framework import status,mixins
from rest_framework.generics import CreateAPIView, GenericAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .utils import get_user_by_account
from verifications.serializers import ImageCodeCheckSerializer
from . import serializers



class UserNameCountView(APIView):
    """
    用户数量
    """
    def get(self,request,username):
        """
        获取指定用户名数量
        :param request:
        :param username:
        :return:
        """
        count=User.objects.filter(username=username).count()

        data={
            'username':username,
            'count':count,
        }
        return Response(data)
class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self,request,mobile):
        """
        获取指定的手机号数量
        :param request:
        :param mobile:
        :return:
        """
        count=User.objects.filter(mobile=mobile).count()

        data={
            'mobile':mobile,
            'count':count
        }
        return Response(data)

class UserView(CreateAPIView):
    """
    用户注册
    """
    serializer_class = serializers.CreateUserSerializer


class SMSCodeTokenView(GenericAPIView):
    """
    根据账号和图片验证码
    """
    serializer_class = ImageCodeCheckSerializer


    def get(self,request,account):
        serializer=self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user=get_user_by_account(account)
        if user is None:
            return Response({'message':'用户不存在'},status=status.HTTP_404_NOT_FOUND)

        # 生成发送短信的access_token
        access_token=user.generate_send_sms_code_token()

        # 处理手机号
        mobile=re.sub(r'(\d{3})\d{4}(\d{3})',r'\1****\2',user.mobile)
        return Response({'mobile':mobile,'access_token':access_token})

class PasswordTokenView(GenericAPIView):
    """
    凭借短信验证码获取重置密码的access_token
    """
    serializer_class = serializers.CheckSMSCodeSerializer
    def get(self,request,account):
        # 调用序列化器
        serializer=self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user=serializer.user

        # 生成access_token
        access_token=user.generate_set_password_token()

        return Response({
            "user_id":user.id,
            "access_token":access_token,
        })


# class PasswordView(UpdateAPIView):
#
#     queryset = User.objects.all()
#     serializer_class = serializers.ResetPasswordSerializer
#
#     def post(self,request,pk):
#         """
#         凭借access_token进行密码的重置
#         :param request:
#         :param pk:
#         :return:
#         """
#         return self.update(request,pk)
class PasswordView(UpdateAPIView):

    queryset = User.objects.all()
    serializer_class = serializers.ResetPasswordSerializer
    def post(self,request, pk):
        """
        凭借access_token进行密码的重置
        :param pk: user_id
        :return: user
        """
        return self.update(request, pk)