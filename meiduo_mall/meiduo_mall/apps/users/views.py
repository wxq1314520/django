from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User


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