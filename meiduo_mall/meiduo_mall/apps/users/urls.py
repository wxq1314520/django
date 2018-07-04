from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from . import views
#
# urlpatterns=[
#     url(r'username/(?P<username>\w{5,20})/count/',views.UserNameCountView.as_view()),
#     url(r'mobile/(?P<mobile>1[345789]\d{9})/count/',views.MobileCountView.as_view()),
#     url(r'users/',views.UserView.as_view()),
#     url(r'authorizations/',obtain_jwt_token,name='authorizations'),
#     url(r"accounts/(?P<account>\w{5,20})/sms/token/", views.SMSCodeTokenView.as_view()),
#     url(r"accounts/(?P<account>\w{5,20})/password/token/$", views.PasswordTokenView.as_view()),
#     url(r"users/(?P<pk>\d+)/password/$", views.PasswordView.as_view())
# ]
urlpatterns = [
    url(r'usernames/(?P<username>\w{5,20})/count/$', views.UserNameCountView.as_view()),
    url(r'mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'users/$', views.UserView.as_view()),
    # 用户登陆
    url(r'authorizations/$', obtain_jwt_token, name="authorizations"),
    # 找回第一步
    url(r"accounts/(?P<account>\w{5,20})/sms/token/$", views.SMSCodeTokenView.as_view()),
    url(r"accounts/(?P<account>\w{5,20})/password/token/$", views.PasswordTokenView.as_view()),
    url(r"users/(?P<pk>\d+)/password/$", views.PasswordView.as_view()),
    url(r"^user/$", views.UserDetailView.as_view()),
    url(r'emails/$',views.EmailView.as_view()),
    url(r'emails/verification/$',views.VerifyEmailView.as_view()),
    url(r'changepwd/$',views.UpdatepwdView.as_view()),
]
router=DefaultRouter()
router.register('addresses',views.AddressViewSet,base_name='addresses')
urlpatterns+=router.urls