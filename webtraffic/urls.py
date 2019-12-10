from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from . import views

app_name = 'webtraffic'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('gashow/', views.ga_show, name='ga_show'),
    path('view/<str:view>', views.view_show, name='view_show'),
    path('galist/', views.ga_list, name='ga_list'),
    path('userinfo/', views.userinfo_show, name='userinfo_show'),
    path('panda/<str:view>', views.panda_show, name='panda_show'),
]
