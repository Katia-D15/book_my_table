from . import views
from django.urls import path

urlpatterns = [
    path('', views.MenuList.as_view(), name='home'),
]
