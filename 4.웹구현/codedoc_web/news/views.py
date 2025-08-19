from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from .models import News
from .crawler import crawl_and_save_news
import json

def news_list(request):
    """뉴스 목록 페이지"""
    # 카테고리 필터
    category = request.GET.get('category', '')
    
    # 뉴스 데이터 가져오기
    news_queryset = News.objects.all()
    
    if category and category != 'all':
        news_queryset = news_queryset.filter(category=category)
    
    # 페이지네이션
    paginator = Paginator(news_queryset, 20)  # 페이지당 20개
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 카테고리 목록
    categories = News.CATEGORY_CHOICES
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
        'total_count': news_queryset.count()
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
