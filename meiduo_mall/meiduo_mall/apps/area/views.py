from .models import Areas
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from .serializers import AreaSerializer,SubAreaSerializer

class AreaView(CacheResponseMixin,ReadOnlyModelViewSet):
    """
    行政区划视图集
    """
    pagination_class=None
    def get_serializer_class(self,*args,**kwargs):
        if self.action=='list':
            return AreaSerializer
        else:
            return SubAreaSerializer
    def get_queryset(self):
        """
        根据不同的动作把顶级的行政区域分离进行查询
        :return:
        """
        if self.action == 'list':

            return Areas.objects.filter(parent=None)
        else:
            return Areas.objects.all()

