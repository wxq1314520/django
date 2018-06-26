from django.contrib.auth.models import AbstractUser
from django.db import models

from itsdangerous import TimedJSONWebSignatureSerializer as TJWSerializer, BadData
# # Create your models here.
# class User(AbstractUser):
#     """
#     用户信息
#     """
#     mobile=models.CharField(max_length=11,unique=True,verbose_name='手机号')
#
#
#     class Meta:
#         db_table="tb_users"
#         verbose_name="用户信息"
#         verbose_name_plural=verbose_name
from django.conf import settings


class User(AbstractUser):
    """用户模型类"""
    mobile=models.CharField(max_length=11,unique=True,verbose_name="手机号")

    class Meta:
        db_table="tb_users"
        verbose_name="用户信息"
        verbose_name_plural=verbose_name

    def generate_send_sms_code_token(self):
        """
        使用itsdangerous生成 发送验证码需要的assecc—token
        生成发送短信验证码的token
        :return:
        """
        # 创建临时令牌的对象
        serializer=TJWSerializer(settings.SECRET_KEY,300)

        token=serializer.dumps({'mobile':self.mobile})

        token=token.decode()
        return token

    @staticmethod
    def check_send_sms_code_token(token):
        """
        检验发送短信验证码的token
        :return:
        """
        serializer=TJWSerializer(settings.SECRET_KEY,300)
        try:
            data=serializer.loads(token)
        except BadData:
            return None
        else:
            return data.get('mobile')

    def generate_set_password_token(self):
        """
        使用itsdangerous生成重置密码需要的access_token
        :return:
        """
        # 创建临时令牌的对象
        serializer=TJWSerializer(settings.SECRET_KEY,300)

        token=serializer.dumps({'user_id':self.id})

        token=token.decode()

        return token


    # @staticmethod
    # def check_set_password_token(token,user_id):
    #     """
    #     检验设置密码的token
    #     :param token:
    #     :param user_id:
    #     :return:
    #     """
    #     serializer=TJWSerializer(settings.SECRET_KEY,300)
    #     try:
    #         data=serializer.loads(token)
    #     except BadData:
    #         return False
    #     else:
    #         if user_id !=str(data.get('user_id')):
    #             return False
    #         else:
    #             return True

    @staticmethod
    def check_set_password_token(access_token):
        """校验重置密码的access_token"""
        serializer = TJWSerializer(settings.SECRET_KEY, 300)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        else:
            return data.get('user_id')
