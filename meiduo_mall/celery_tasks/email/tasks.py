from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import app

@app.task(name="send_verify_email")
def send_verify_email(to_email,verify_url):
    """
    发送邮件
    :param to_email:
    :param verify_url:
    :return:
    """

    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    send_mail(subject,"",settings.EMAIL_HOST_USER, to_email, html_message=html_message)
