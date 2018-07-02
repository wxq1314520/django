from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'area', views.AreaView, base_name='area')

urlpatterns = []

urlpatterns += router.urls
