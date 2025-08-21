from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import News
from .crawler import crawl_and_save_news
import json

def news_list(request):
    """뉴스 목록 페이지"""
    # 카테고리 및 검색어 필터
    category = request.GET.get('category', '')
    search_term = request.GET.get('search', '')
    page_number = int(request.GET.get('page', 1))
    
    # 뉴스 데이터 가져오기
    news_queryset = News.objects.all().order_by('-pub_date')
    
    if category and category != 'all':
        news_queryset = news_queryset.filter(category=category)
    
    if search_term:
        news_queryset = news_queryset.filter(
            Q(title__icontains=search_term) | 
            Q(description__icontains=search_term)
        )
    
    # 총 개수 계산
    total_count = news_queryset.count()
    total_pages = (total_count + 9) // 10  # 올림 계산
    
    # 현재 페이지의 뉴스 10개만 가져오기
    start_index = (page_number - 1) * 10
    end_index = start_index + 10
    current_news = list(news_queryset[start_index:end_index])
    
    # 페이지네이션 정보
    has_previous = page_number > 1
    has_next = page_number < total_pages
    previous_page = page_number - 1 if has_previous else None
    next_page = page_number + 1 if has_next else None
    
    # 페이지 범위 (최대 5개 페이지 번호 표시)
    start_page = max(1, page_number - 2)
    end_page = min(total_pages, start_page + 4)
    if end_page - start_page < 4:
        start_page = max(1, end_page - 4)
    page_range = range(start_page, end_page + 1)
    
    # 카테고리 목록
    categories = News.CATEGORY_CHOICES
    
    # 가짜 페이지 객체 생성 (템플릿 호환성을 위해)
    class CustomPageObj:
        def __init__(self, object_list, number):
            self.object_list = object_list
            self.number = number
            
        def __iter__(self):
            return iter(self.object_list)
            
        def has_previous(self):
            return has_previous
            
        def has_next(self):
            return has_next
            
        def previous_page_number(self):
            return previous_page
            
        def next_page_number(self):
            return next_page
            
        def has_other_pages(self):
            return total_pages > 1
    
    # 가짜 Paginator 객체
    class CustomPaginator:
        def __init__(self):
            self.num_pages = total_pages
            self.page_range = page_range
    
    page_obj = CustomPageObj(current_news, page_number)
    page_obj.paginator = CustomPaginator()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
        'current_search': search_term,
        'total_count': total_count
    }
    
    return render(request, 'news/news_list.html', context)

@require_http_methods(["POST"])
def refresh_news(request):
    """뉴스 새로고침 (AJAX)"""
    try:
        data = json.loads(request.body)
        keywords = data.get('keywords', ['금융', '경제', '투자'])
        
        saved_count, total_count = crawl_and_save_news(keywords)
        
        return JsonResponse({
            'success': True,
            'message': f'총 {total_count}개 중 {saved_count}개 새로 저장됨',
            'saved_count': saved_count,
            'total_count': total_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'오류 발생: {str(e)}'
        })

def news_detail(request, pk):
    """뉴스 상세 페이지"""
    try:
        news = News.objects.get(pk=pk)
        return render(request, 'news/news_detail.html', {'news': news})
    except News.DoesNotExist:
        return render(request, 'news/news_not_found.html')

def news_api(request):
    """뉴스 API (JSON 응답)"""
    category = request.GET.get('category', '')
    limit = int(request.GET.get('limit', 10))
    
    news_queryset = News.objects.all()[:limit]
    
    if category and category != 'all':
        news_queryset = News.objects.filter(category=category)[:limit]
    
    news_data = []
    for news in news_queryset:
        news_data.append({
            'id': news.id,
            'title': news.title,
            'description': news.description,
            'link': news.link,
            'category': news.category,
            'source': news.source,
            'pub_date': news.pub_date,
            'collected_time': news.collected_time.isoformat()
        })
    
    return JsonResponse({
        'success': True,
        'data': news_data,
        'count': len(news_data)
    })