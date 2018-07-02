from rest_framework import serializers

from .models import Areas


class AreaSerializer(serializers.ModelSerializer):
    """
    省级列表序列器
    """
    class Meta:
        model = Areas
        fields=('id','name')


class SubAreaSerializer(serializers.ModelSerializer):
    """
    子行政区划区域序列化
    """
    subs = AreaSerializer(many=True, read_only=True)
    class Meta:
        model=Areas
        #在模型声明字段时，设置related_name可以解决多个模型间
        fields=('id','name','subs')