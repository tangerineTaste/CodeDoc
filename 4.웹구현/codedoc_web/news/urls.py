from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('detail/<int:pk>/', views.news_detail, name='news_detail'),
    path('refresh/', views.refresh_news, name='refresh_news'),
    path('api/', views.news_api, name='news_api'),
]
