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

from meiduo_mall.utils.models import BaseModel


class User(AbstractUser):
    """用户模型类"""
    mobile=models.CharField(max_length=11,unique=True,verbose_name="手机号")
    email_active=models.BooleanField(default=False,verbose_name='邮箱激活状态')
    default_address=models.ForeignKey('Address',related_name='users',null=True,blank=True,on_delete=models.SET_NULL,verbose_name='默认地址')

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



    def generate_verify_email_token(self):
        serializer = TJWSerializer(settings.SECRET_KEY, 60*60*24)

        token = serializer.dumps({'user_id': self.id,'email':self.email})

        token = token.decode()

        return token

    @staticmethod
    def check_verify_email_token(access_token):
        """校验重置密码的access_token"""
        serializer = TJWSerializer(settings.SECRET_KEY, 300)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        else:
            email=data.get('email')
            user_id=data.get('user_id')
            try:
                user=User.objects.get(id=user_id,email=email)
            except User.DoesNotExist:
                return None
            return user

# 地址信息
class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('area.Areas', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('area.Areas', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('area.Areas', on_delete=models.PROTECT, related_name='district_addresses',verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']
