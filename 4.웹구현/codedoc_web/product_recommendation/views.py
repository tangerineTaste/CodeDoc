# product_recommendation/views.py
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from .utils import ProductDataLoader, ProductPaginator
import requests
import os

def product_list(request):
    """
    상품 목록 페이지
    기존 API 데이터(예금/적금) + 새로운 파일 기반 데이터(펀드/주식/MMF) 통합
    """
    context = {}
    
    try:
        # 1. 기존 API 데이터 (예금, 적금) - 실제 API 호출
        deposits = get_deposit_products()
        savings = get_saving_products()
        
        # 2. 새로운 파일 기반 데이터 로드
        print("파일 기반 데이터 로딩 시작...")
        funds = ProductDataLoader.get_funds()
        stocks = ProductDataLoader.get_stocks()
        mmf_products = ProductDataLoader.get_mmf_products()
        
        print(f"로드된 데이터: 예금 {len(deposits)}개, 적금 {len(savings)}개, 펀드 {len(funds)}개, 주식 {len(stocks)}개, MMF {len(mmf_products)}개")
        
        # 3. 전체 상품 통합 (API + 파일 기반)
        all_products_list = []
        
        # API 데이터를 통합 형식으로 변환
        for deposit in deposits:
            deposit['product_type'] = 'deposit'
            deposit['product_type_name'] = '예금'
            all_products_list.append(deposit)
        
        for saving in savings:
            saving['product_type'] = 'saving' 
            saving['product_type_name'] = '적금'
            all_products_list.append(saving)
        
        # 파일 기반 데이터 추가 (이미 변환됨)
        all_products_list.extend(funds)
        all_products_list.extend(stocks)
        all_products_list.extend(mmf_products)
        
        print(f"전체 통합 상품 수: {len(all_products_list)}개")
        
        # 4. 페이지네이션 처리
        page = request.GET.get('page', 1)
        deposits_page = request.GET.get('deposits_page', 1)
        savings_page = request.GET.get('savings_page', 1)
        funds_page = request.GET.get('funds_page', 1)
        stocks_page = request.GET.get('stocks_page', 1)
        mmf_page = request.GET.get('mmf_page', 1)
        
        # 전체 상품 페이지네이션
        all_products_paginated, all_total = ProductPaginator.paginate_products(
            all_products_list, page, per_page=9
        )
        
        # 개별 카테고리 페이지네이션
        deposits_paginated, deposits_total = ProductPaginator.paginate_products(
            deposits, deposits_page, per_page=9
        )
        
        savings_paginated, savings_total = ProductPaginator.paginate_products(
            savings, savings_page, per_page=9
        )
        
        funds_paginated, funds_total = ProductPaginator.paginate_products(
            funds, funds_page, per_page=9
        )
        
        stocks_paginated, stocks_total = ProductPaginator.paginate_products(
            stocks, stocks_page, per_page=9
        )
        
        mmf_paginated, mmf_total = ProductPaginator.paginate_products(
            mmf_products, mmf_page, per_page=9
        )
        
        # 5. 컨텍스트 구성
        context.update({
            # 전체 상품
            'all_products': all_products_paginated,
            'all_total': all_total,
            
            # 기존 API 상품 (예금, 적금)
            'deposits': deposits_paginated,
            'deposits_total': deposits_total,
            'savings': savings_paginated,
            'savings_total': savings_total,
            
            # 새로운 파일 기반 상품 (펀드, 주식, MMF)
            'funds': funds_paginated,
            'funds_total': funds_total,
            'stocks': stocks_paginated,
            'stocks_total': stocks_total,
            'mmf_products': mmf_paginated,
            'mmf_total': mmf_total,
        })
        
        print(f"컨텍스트 구성 완료: 전체 {all_total}개 상품")
        
    except Exception as e:
        context['error'] = f'상품 정보를 불러오는 중 오류가 발생했습니다: {str(e)}'
        print(f"Product list error: {e}")
        import traceback
        traceback.print_exc()
    
    return render(request, 'product_recommendation/product_list.html', context)


def get_deposit_products():
    """
    예금 상품 API 호출 (환경변수에서 FSS_API_KEY 가져오기)
    """
    try:
        # 환경변수에서 API 키 가져오기
        api_key = os.getenv('FSS_API_KEY') or getattr(settings, 'FSS_API_KEY', None)
        
        if not api_key:
            print("FSS_API_KEY가 설정되지 않았습니다. 테스트 데이터를 반환합니다.")
            return get_test_deposit_data()
        
        print("예금 상품 API 호출 중...")
        url = "http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
        params = {
            'auth': api_key,
            'topFinGrpNo': '020000',
            'pageNo': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get('result') and data['result'].get('baseList'):
            print(f"예금 상품 API 성공: {len(data['result']['baseList'])}개 상품")
            return data['result']['baseList']
        else:
            print("예금 상품 API 응답에 데이터가 없습니다.")
            return get_test_deposit_data()
        
    except Exception as e:
        print(f"예금 상품 API 오류: {e}")
        return get_test_deposit_data()


def get_saving_products():
    """
    적금 상품 API 호출 (환경변수에서 FSS_API_KEY 가져오기)
    """
    try:
        # 환경변수에서 API 키 가져오기
        api_key = os.getenv('FSS_API_KEY') or getattr(settings, 'FSS_API_KEY', None)
        
        if not api_key:
            print("FSS_API_KEY가 설정되지 않았습니다. 테스트 데이터를 반환합니다.")
            return get_test_saving_data()
        
        print("적금 상품 API 호출 중...")
        url = "http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"
        params = {
            'auth': api_key,
            'topFinGrpNo': '020000',
            'pageNo': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get('result') and data['result'].get('baseList'):
            print(f"적금 상품 API 성공: {len(data['result']['baseList'])}개 상품")
            return data['result']['baseList']
        else:
            print("적금 상품 API 응답에 데이터가 없습니다.")
            return get_test_saving_data()
        
    except Exception as e:
        print(f"적금 상품 API 오류: {e}")
        return get_test_saving_data()


def get_test_deposit_data():
    """테스트용 예금 데이터"""
    return [
        {
            'fin_prdt_nm': 'KB스타정기예금',
            'kor_co_nm': 'KB국민은행',
            'join_way': '온라인,영업점',
            'dcls_strt_day': '20250101',
        },
        {
            'fin_prdt_nm': '신한쏠편한정기예금',
            'kor_co_nm': '신한은행',
            'join_way': '온라인,영업점',
            'dcls_strt_day': '20250101',
        },
        {
            'fin_prdt_nm': '우리WON정기예금',
            'kor_co_nm': '우리은행',
            'join_way': '온라인,영업점',
            'dcls_strt_day': '20250101',
        }
    ]


def get_test_saving_data():
    """테스트용 적금 데이터"""
    return [
        {
            'fin_prdt_nm': 'KB Star 적금',
            'kor_co_nm': 'KB국민은행',
            'join_way': '온라인,영업점',
            'dcls_strt_day': '20250101',
        },
        {
            'fin_prdt_nm': '신한 쏠편한적금',
            'kor_co_nm': '신한은행',
            'join_way': '온라인,영업점',
            'dcls_strt_day': '20250101',
        },
        {
            'fin_prdt_nm': '우리WON적금',
            'kor_co_nm': '우리은행',
            'join_way': '온라인,영업점',
            'dcls_strt_day': '20250101',
        }
    ]


def product_detail(request, product_id):
    """
    상품 상세 페이지 (추후 구현)
    """
    context = {
        'product_id': product_id,
    }
    return render(request, 'product_recommendation/product_detail.html', context)


def product_recommend(request):
    """
    상품 추천 메인 페이지 (기존 유지)
    """
    return render(request, 'product_recommendation/product_recommend.html')


def product_recommend_ai(request):
    """
    AI 상품 추천 페이지 (기존 유지)
    """
    context = {}
    
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        
        if user_input:
            try:
                # AI 추천 로직 (기존 유지)
                recommendations = get_ai_recommendations(user_input)
                context['recommendations'] = recommendations
                context['user_input'] = user_input
                
            except Exception as e:
                context['error'] = f'추천 처리 중 오류가 발생했습니다: {str(e)}'
    
    return render(request, 'product_recommendation/product_recommend_ai.html', context)


def get_ai_recommendations(user_input):
    """
    AI 기반 상품 추천 로직 (기존 유지)
    """
    return {
        'user_info': {
            'age': 30,
            'monthly_income': 400,
            'gender': 'male',
            'married': False
        },
        'recommendation_reason': '고객님의 연령과 소득 수준을 고려한 추천입니다.',
        'products': [],
        'total_candidates': 50
    }