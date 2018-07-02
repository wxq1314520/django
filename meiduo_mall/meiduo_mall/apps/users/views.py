import re

from rest_framework import status,mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, GenericAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
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



class UserDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class =serializers.UserDetailSerializer
    def get_object(self):



        return self.request.user



class EmailView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.EmailSerializer
    def get_object(self):

        return self.request.user


class VerifyEmailView(APIView):
    """

    """
    def get(self,request):
        token=request.query_params.get("token")
        user=User.check_verify_email_token(token)
        if user is None:
            return Response({"message":"无效的token"},status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active=True
            user.save()
            return Response({'message':'ok'})


from rest_framework.viewsets import ModelViewSet

class AddressViewSet(ModelViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = serializers.UserAddressSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset=self.get_queryset()
        serializer=serializers.UserAddressSerializer(queryset,many=True)
        user=self.request.user

        return Response({
            'user_id':user.id,
            'default_address_id':user.default_address_id,
            'limit':20,
            'addresses':serializer.data
        })
    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        #检查用户地址数据数目不能超过上限
        count=request.user.addresses.count()
        if count>=20:
            return Response({'message':'保存地址数据已达到上限'},status=status.HTTP_400_BAD_REQUEST)
        return super().create(request,*args,**kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        address=self.get_object()

        # 进行逻辑删除
        address.is_deleted=True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(methods=['put'],detail=True)
    def status(self,request,pk=None,address_id=None):
        """
        设置默认地址
        :param request:
        :param pk:
        :param address_id:
        :return:
        """
        address=self.get_object()
        request.user.default_address=address
        request.user.save()
        return Response({'message':'ok'},status=status.HTTP_200_OK)
    @action(methods=['put'],detail=True)
    def title(self,request,pk=None,address_id=None):
        """
        修改标题
        :param request:
        :param pk:
        :param address_id:
        :return:
        """
        address=self.get_object()
        serializer=serializers.AddressTitleSerializer(instance=address,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)