from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from .financial_item_list import FinancialProductAPI
from .matching import HighPerformanceFinancialRecommender
import json
import logging

# 로거 설정
logger = logging.getLogger(__name__)

# 전역 변수로 추천 시스템 초기화 (한 번만 로드)
_recommender = None

def get_recommender():
    """추천 시스템 싱글톤 패턴으로 초기화"""
    global _recommender
    if _recommender is None:
        try:
            logger.info("금융상품 추천 시스템 초기화 중...")
            _recommender = HighPerformanceFinancialRecommender()
            logger.info("추천 시스템 초기화 완료")
        except Exception as e:
            logger.error(f"추천 시스템 초기화 실패: {e}")
            _recommender = None
    return _recommender

def product_list(request):
    """상품소개 페이지"""
    try:
        api = FinancialProductAPI()
        
        # 기본적으로 은행 예금 상품 가져오기
        deposits_data = api.get_deposit_products('020000')
        savings_data = api.get_saving_products('020000')
        
        # 데이터 추출
        deposits_list = deposits_data.get('result', {}).get('baseList', [])
        savings_list = savings_data.get('result', {}).get('baseList', [])
        
        # 상품 타입 추가 (구분을 위해)
        for product in deposits_list:
            product['product_type'] = 'deposit'
            product['product_type_name'] = '예금'
            
        for product in savings_list:
            product['product_type'] = 'saving'
            product['product_type_name'] = '적금'
        
        # 전체 상품 통합
        all_products = deposits_list + savings_list
        
        # 페이지네이션 - 전체 상품
        all_paginator = Paginator(all_products, 9)
        all_page = request.GET.get('page', 1)
        all_page_obj = all_paginator.get_page(all_page)
        
        # 페이지네이션 - 예금만
        deposits_paginator = Paginator(deposits_list, 9)
        deposits_page = request.GET.get('deposits_page', 1)
        deposits_page_obj = deposits_paginator.get_page(deposits_page)
        
        # 페이지네이션 - 적금만
        savings_paginator = Paginator(savings_list, 9)
        savings_page = request.GET.get('savings_page', 1)
        savings_page_obj = savings_paginator.get_page(savings_page)
        
        context = {
            'all_products': all_page_obj,  # 전체 상품
            'deposits': deposits_page_obj,
            'savings': savings_page_obj,
            'all_total': len(all_products),
            'deposits_total': len(deposits_list),
            'savings_total': len(savings_list),
        }
        
        return render(request, 'product_recommendation/product_list.html', context)
    
    except Exception as e:
        return render(request, 'product_recommendation/product_list.html', {'error': str(e)})

def product_recommend(request):
    """내게맞는상품찾기 페이지 - 서비스 소개"""
    return render(request, 'product_recommendation/product_recommend.html')

def product_recommend_ai(request):
    """내게맞는상품찾기 페이지 - AI 추천 시스템"""
    context = {
        'recommendations': None,
        'user_input': '',
        'error': None,
        'processing_time': 0
    }
    
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        
        if user_input:
            try:
                import time
                start_time = time.time()
                
                # 추천 시스템 가져오기
                recommender = get_recommender()
                
                if recommender:
                    # AI 추천 실행
                    result = recommender.recommend(user_input, top_n=6)
                    
                    # 처리 시간 계산
                    processing_time = (time.time() - start_time) * 1000
                    
                    context.update({
                        'recommendations': result,
                        'user_input': user_input,
                        'processing_time': round(processing_time, 1)
                    })
                    
                    logger.info(f"추천 완료: {user_input} ({processing_time:.1f}ms)")
                else:
                    context['error'] = "추천 시스템이 초기화되지 않았습니다. 관리자에게 문의하세요."
                    
            except Exception as e:
                logger.error(f"추천 처리 중 오류: {e}")
                context['error'] = f"추천 처리 중 오류가 발생했습니다: {str(e)}"
        else:
            context['error'] = "검색어를 입력해주세요."
    
    return render(request, 'product_recommendation/product_recommend_ai.html', context)

def product_detail(request, product_type, product_id):
    """상품상세 페이지"""
    # 추후 구현
    context = {
        'product_type': product_type,
        'product_id': product_id
    }
    return render(request, 'product_recommendation/product_detail.html', context)

# Ajax 요청을 위한 추가 뷰
def get_recommendation_ajax(request):
    """AJAX용 추천 API"""
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        
        if not user_input:
            return JsonResponse({'error': '검색어를 입력해주세요.'}, status=400)
        
        try:
            import time
            start_time = time.time()
            
            recommender = get_recommender()
            if not recommender:
                return JsonResponse({'error': '추천 시스템이 초기화되지 않았습니다.'}, status=500)
            
            result = recommender.recommend(user_input, top_n=6)
            processing_time = (time.time() - start_time) * 1000
            
            # JSON 직렬화를 위해 데이터 정제
            response_data = {
                'success': True,
                'user_info': result.get('user_info', {}),
                'recommendation_reason': result.get('recommendation_reason', ''),
                'products': result.get('products', []),
                'total_candidates': result.get('total_candidates', 0),
                'processing_time': round(processing_time, 1)
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"AJAX 추천 처리 중 오류: {e}")
            return JsonResponse({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)