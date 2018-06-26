#发送短信的异常
from celery_tasks.main import app
from .yuntongxun.sms import CCP
from . import constants
@app.task(name="send_sms_code")
def send_sms_code(mobile,sms_code):
    """
    发送短信的异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证
    :return:
    """
    ccp = CCP()
    time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)

    ccp.send_template_sms(mobile, [sms_code, time], constants.SMS_TEMP_ID)

