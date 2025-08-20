from django.urls import path
from . import views

app_name = 'customer_support'

urlpatterns = [
    path('notice/', views.notice_list, name='notice_list'),  # 이 name이 중요
    path('guide/', views.service_guide, name='service_guide'),
    path('notice/<int:notice_id>/', views.notice_detail, name='notice_detail'),
]