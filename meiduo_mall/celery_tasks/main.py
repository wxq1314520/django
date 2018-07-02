from celery import Celery
# 为celery使用django配置文件进行设置
import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 创建celery应用
app = Celery('meiduo')

# 导入celery配置
app.config_from_object('celery_tasks.config')

# 自动注册celery任务
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])


# 最终在终端里面运行celery
# celery -A 主程序的包路径 worker -l info
# 一般从后端的项目根目录下，执行上面的命令
# celery -A celery_tasks.main worker -l info