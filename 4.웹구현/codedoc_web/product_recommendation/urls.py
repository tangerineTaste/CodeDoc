from django.urls import path
from . import views

app_name = 'product_recommendation'

urlpatterns = [
    path('list/', views.product_list, name='product_list'),           # 상품소개
    path('recommend/', views.product_recommend, name='product_recommend'),  # 내게맞는상품찾기 (서비스 소개)
    path('recommend/ai/', views.product_recommend_ai, name='product_recommend_ai'),  # AI 추천 시스템
    path('recommend/ajax/', views.get_recommendation_ajax, name='recommendation_ajax'),  # AJAX 추천 API
    path('detail/<str:product_type>/<str:product_id>/', views.product_detail, name='product_detail'),  # 상품상세
]