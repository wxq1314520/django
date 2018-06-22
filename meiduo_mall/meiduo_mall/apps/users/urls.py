from django.conf.urls import url

from . import views

urlpatterns=[
    url(r'username/(?P<username>\w{5,20})/count/',views.UserNameCountView.as_view())
]