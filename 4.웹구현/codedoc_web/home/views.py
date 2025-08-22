# home/views.py
from django.shortcuts import render
from customer_support.models import Notice

def index(request):
    """메인페이지 뷰 - 최신 공지사항 4개를 가져와서 표시"""
    
    # 활성화된 최신 공지사항 4개 가져오기
    recent_notices = Notice.objects.filter(
        is_active=True
    ).order_by('-created_at')[:4]
    
    context = {
        'recent_notices': recent_notices,
    }
    
    # 경로를 home/index.html로 수정
    return render(request, 'home/index.html', context)