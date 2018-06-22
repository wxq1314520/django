#发送短信的异常
from celery_tasks.main import app

@app.task(name="send_sms_code")
def send_sms_code():
    ccp = CCP()
    time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)

    ccp.send_template_sms(mobile, [sms_code, time], constants.SMS_TEMP_ID)

