from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Notice

def notice_list(request):
    """공지사항 목록 페이지"""
    notices = Notice.objects.filter(is_active=True).order_by('-created_at')
    
    # 페이지네이션 (10개씩)
    paginator = Paginator(notices, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    
    context = {
        'notices': page_obj,
        'total_count': notices.count()
    }
    
    return render(request, 'customer_support/notice_list.html', context)

def notice_detail(request, notice_id):
    """공지사항 상세 페이지"""
    notice = get_object_or_404(Notice, id=notice_id, is_active=True)
    
    # 조회수 증가
    notice.view_count += 1
    notice.save(update_fields=['view_count'])
    
    context = {'notice': notice}
    return render(request, 'customer_support/notice_detail.html', context)

def service_guide(request):
    """서비스 가이드 페이지 - 서비스 소개"""
    context = {
        'page_title': '서비스 가이드',
    }
    return render(request, 'customer_support/service_guide.html', context)