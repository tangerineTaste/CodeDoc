from django.urls import path
from . import views

app_name = 'customer_support'

urlpatterns = [
    path('notice/', views.notice_list, name='notice_list'),  
    path('notices/<int:notice_id>/', views.notice_detail, name='notice_detail'),
    path('guide/', views.service_guide, name='service_guide'),
]