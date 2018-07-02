import re

from django_redis import get_redis_connection
from django.conf import settings
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.utils import get_user_by_account
from .models import User

from django.core.mail import send_mail

from celery_tasks.email.tasks import send_verify_email

class CreateUserSerializer(serializers.ModelSerializer):
    """
    创建用户序列化器
    """
    password2=serializers.CharField(label='确认密码',required=True,allow_null=False,allow_blank=False,write_only=True)
    sms_code=serializers.CharField(label='短信验证码',required=True,allow_blank=False,allow_null=False,write_only=True)
    allow=serializers.CharField(label='短信验证码',required=True,allow_blank=False,allow_null=False,write_only=True)
    token=serializers.CharField(label='登陆状态Token',read_only=True)


    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[345789]\d{9}$',value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """校验用户是否同意协议"""
        if value!='true':
            raise serializers.ValidationError('请同意用户协议')
        return value
    def validate(self, data):
        # 判断两次密码
        if data['password']!=data['password2']:
            raise serializers.ValidationError('两次密码不一致')
        redis_conn=get_redis_connection('verify_codes')
        mobile=data['mobile']

        real_sms_code=redis_conn.get('sms_%s'% mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code']!=real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')
        return data

    def create(self, validated_data):
        """
        创建用户
        :param validated_data:
        :return:
        """
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        user=super().create(validated_data)

        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])
        user.save()
        # 补充生成记录登陆状态的token
        jwt_payload_handler=api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler=api_settings.JWT_ENCODE_HANDLER
        payload=jwt_payload_handler(user)
        token=jwt_encode_handler(payload)
        user.token=token

        return user
    class Meta:
        model=User
        fields=('id','username','password','password2','sms_code','mobile','allow','token')
        extra_kwargs={
            'id':{'read_only':True},
            'username':{
                'min_length':5,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许5-20字符串的用户名',
                    'max_length':'仅允许5-20字符串的用户名',
                }
            },
            'password':{
                'write_only':True,
                'min_length':8,
                'max_length':20,
                'error_messages':{
                    'min_length':'仅允许8-20个字符串的密码',
                    'max_length':'仅允许8-20个字符串的密码'
                }
            }
        }

class CheckSMSCodeSerializer(serializers.Serializer):
    """
    检查sms_code
    """
    sms_code=serializers.CharField(min_length=6,max_length=6)


    def validate_sms_code(self, value):
        account=self.context['view'].kwargs['account']
        # 获取user
        user=get_user_by_account(account)
        if user is None:
            raise serializers.ValidationError('用户不存在')

        redis_conn=get_redis_connection('verify_codes')
        real_sms_code=redis_conn.get('sms_%s' % user.mobile)

        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if value !=real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')
        self.user=user
        return value

#
# class ResetPasswordSerializer(serializers.ModelSerializer):
#     """
#     重置序列化器
#     """
#     password2=serializers.CharField(label="确认密码",write_only=True)
#     access_token=serializers.CharField(label='操作token',write_only=True)
#
#     class Meta:
#         model=User
#
#         fields=('id','password','password2','access_token')
#
#         extra_kwargs={
#             'password':{
#                 'write_only':True,
#                 'min_length':8,
#                 'max_length':20,
#                 'error_message':{
#                     'min_length':'仅允许8-20个字符的密码',
#                     'max_length':'仅允许8-20个字符的密码',
#                 }
#             }
#         }
#
#     def update(self, instance, validated_data):
#         """
#         更新密码
#         :param instance:
#         :param validated_data:
#         :return:
#         """
#         # 调用django用户模型类的设置密码方法
#         instance.set_password(validated_data['password'])
#         instance.save()
#         return instance
#     def validate(self, attrs):
#         """
#         校验数据
#         :param attrs:
#         :return:
#         """
#         #判断两次密码
#         if attrs['password']!=attrs['password2']:
#             raise serializers.ValidationError('两次密码不一致')
#
#         # 判断access_token
#         allow=User.check_set_password_token(attrs['access_token'],self.context['view'].kwargs['pk'])
#
#         if not allow:
#             raise serializers.ValidationError('无效的access token')
#         return attrs
class ResetPasswordSerializer(serializers.ModelSerializer):
    """重置密码的序列化器"""
    # 字段
    password2 = serializers.CharField(label='确认密码',  write_only=True)
    access_token = serializers.CharField(label='重置密码的access_token',  write_only=True)

    # 校验
    def validate(self,attrs):
        # 校验密码和确认密码
        password = attrs['password']
        password2 = attrs['password2']
        access_token = attrs['access_token']
        if password != password2:
            raise serializers.ValidationError("密码和确认密码不一致")

        # 校验重置密码的access_token是否有效
        allow = User.check_set_password_token(access_token)
        if allow is None:
            raise serializers.ValidationError("无效的access_token")

        return attrs

    # 更新
    def update(self, instance, validated_data):
        """
        更新密码
        :param instance: 当前pk值对应的User模型对象
        :param validated_data: 校验完成以后的数据
        :return: user对象
        """
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


    class Meta:
        model = User
        fields = ('id', 'password', 'password2', 'access_token')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }



class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=('id','username','mobile','email','email_active')

class EmailSerializer(serializers.ModelSerializer):

    def update(self,instance,validated_data):
        instance.email=validated_data['email']
        instance.save()
        #生成附带token的激活链接
        token=instance.generate_verify_email_token()
        verify_url= "http://www.meiduo.com:8080/success_verify_email.html?token=" + token
        #发送验证邮件
        # subject="美多商城邮箱验证"
        # to_mail=[instance.email]
        # html_message='<a href="%s">%s</a>' %(url,url)
        # 发送验证邮件
        # subject = "美多商城邮箱验证"
        # to_email = [instance.email]
        # html_message = '<p>尊敬的用户您好！</p>' \
        #                '<p>感谢您使用美多商城。</p>' \
        #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #                '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
        # send_mail(subject,"",settings.EMAIL_HOST_USER, to_email, html_message=html_message)

        # 调用celery通过异步发送激活邮件
        #send_mail(subject,"",settings.EMAIL_HOST_USER,to_mail,html_message=html_message)
        # 手动调用celery_tasks
        send_verify_email.delay([instance.email],verify_url)
        return instance

    class Meta:
        model=User
        fields=('id','email')
        extra_kwargs={
            'email':{
                'required':True
            }
        }

# 用户地址信息
from .models import Address

class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province=serializers.StringRelatedField(read_only=True)
    city=serializers.StringRelatedField(read_only=True)
    district=serializers.StringRelatedField(read_only=True)
    province_id=serializers.IntegerField(label='省ID',required=True)
    city_id=serializers.IntegerField(label='市ID',required=True)
    district_id=serializers.IntegerField(label='区ID',required=True)
    mobile=serializers.RegexField(label='手机号',regex=r'^1[3-9]\d{9}$')

    class Meta:
        model=Address
        exclude=('user','is_deleted','create_time','update_time')

    def create(self, validated_data):
        """
        保存
        :param validated_data:
        :return:
        """
        #address模型类中有user属性，将user对象添加到模型类的创建参数中
        validated_data['user']=self.context['request'].user
        return super().create(validated_data)

class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model=Address
        fields=('title',)



