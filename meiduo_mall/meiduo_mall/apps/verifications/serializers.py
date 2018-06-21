#序列化器
from django_redis import get_redis_connection
from redis import RedisError
from rest_framework import serializers

from meiduo_mall.utils.exceptions import logger


class ImageCodeCheckSerializer(serializers.Serializer):
    """校验图形验证码的序列化器"""
    #声明验证码规则
    image_code=serializers.CharField(max_length=4,min_length=4)
    #uuidfield 专门用来校验uuid格式类型的字符串
    image_code_id=serializers.UUIDField()

    def validate(self, attrs):
        #接收具体的校验数据
        image_code=attrs['image_code']
        image_code_id=attrs['image_code_id']

        # 从redis中获取真实图片验证码
        redis_conn=get_redis_connection('verify_codes')
        real_image_code_text=redis_conn.get('img_%s' % image_code_id)

        # 如果根据当前的image_code_id获取不到值
        if not real_image_code_text:
            raise serializers.ValidationError('图片验证码无效')

        # 图形验证码只能使用一次，所以接下来，需要删除验证码
        try:
            redis_conn.delete('img_%s'%image_code_id)
        except RedisError as e:
            logger.error(e)

        # python中直接从redis中读取到的数据都是bytes类型
        real_image_code_text=real_image_code_text.decode()
        # 比较图片验证码
        if real_image_code_text.lower() !=image_code.lower():
            raise serializers.ValidationError('图片验证码错误')

        #检查是否在60s内有发送记录
        #在序列化器中要获取数据
        mobile=self.context['view'].kwargs['mobile']
        send_flag=redis_conn.get('send_flag_%s'% mobile)
        #如果redis中有这个数据则标识60s发送过短信
        if send_flag:
            raise serializers.ValidationError("请求国语频繁")

        return attrs