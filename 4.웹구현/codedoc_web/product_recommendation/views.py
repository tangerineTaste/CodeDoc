from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from .financial_item_list import FinancialProductAPI
from django.contrib.auth.decorators import login_required
import json

def calculate_risk_preference(금융위험태도):
    """
    금융위험태도 점수를 바탕으로 위험감수형/위험회피형 추출
    금융위험태도 >= 0 : 위험회피형 = 1, 위험감수형 = 0
    금융위험태도 < 0 : 위험감수형 = 1, 위험회피형 = 0
    """
    위험감수형 = 0
    위험회피형 = 0
    
    if 금융위험태도 >= 0:
        위험회피형 = 1
    else:
        위험감수형 = 1
    
    return 위험감수형, 위험회피형

def update_financial_risk_attitude(user, chat_message):
    """
    채팅 내용을 분석하여 금융위험태도 점수 업데이트
    위험감수형 패턴 감지 시: -1 점
    위험회피형 패턴 감지 시: +1 점
    """
    if not user.is_authenticated or not hasattr(user, 'profile'):
        return
    
    # 위험감수형 키워드 예시 (필요에 따라 수정 가능)
    risk_taking_keywords = ['위험', '도전', '투자', '수익', '주식', '비트코인', '고수익', '모험']
    risk_averse_keywords = ['안전', '예금', '적금', '보수', '안정', '담보', '저위험']
    
    chat_lower = chat_message.lower()
    
    # 위험감수형 패턴 감지
    if any(keyword in chat_lower for keyword in risk_taking_keywords):
        user.profile.금융위험태도 = (user.profile.금융위험태도 or 0) - 1
        user.profile.save()
        return -1  # 위험감수형 패턴
    
    # 위험회피형 패턴 감지
    elif any(keyword in chat_lower for keyword in risk_averse_keywords):
        user.profile.금융위험태도 = (user.profile.금융위험태도 or 0) + 1
        user.profile.save()
        return 1  # 위험회피형 패턴
    
    return 0  # 패턴 미감지

def product_list(request):
    """상품소개 페이지"""
    try:
        api = FinancialProductAPI()
        
        # 로그인된 사용자의 금융위험태도 처리
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            금융위험태도 = request.user.profile.금융위험태도 or 0
            위험감수형, 위험회피형 = calculate_risk_preference(금융위험태도)
        else:
            위험감수형, 위험회피형 = 0, 0
        
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
            '위험감수형': 위험감수형,
            '위험회피형': 위험회피형,
            '금융위험태도': 금융위험태도 if request.user.is_authenticated and hasattr(request.user, 'profile') else 0,
        }
        
        return render(request, 'product_recommendation/product_list.html', context)
    
    except Exception as e:
        return render(request, 'product_recommendation/product_list.html', {'error': str(e)})

def product_recommend(request):
    """내게맞는상품찾기 페이지"""
    return render(request, 'product_recommendation/product_recommend.html')

def product_detail(request, product_type, product_id):
    """상품상세 페이지"""
    # 추후 구현
    context = {
        'product_type': product_type,
        'product_id': product_id
    }
    return render(request, 'product_recommendation/product_detail.html', context)