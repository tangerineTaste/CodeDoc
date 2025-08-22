
# product_recommendation/views.py
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from .utils import ProductDataLoader, ProductPaginator
import requests
import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from .financial_item_list import FinancialProductAPI
from django.contrib.auth.decorators import login_required
import json
import joblib
import pandas as pd
from datetime import date


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
        # 기본적으로 은행 예금 상품 가져오기
        recommended_products = []

        # AI 추천 로직 (로그인 사용자 대상)
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                
                # 1. 사용자 데이터 -> 모델 입력 변수 변환 (수정 필요)
                # 이 부분은 사용자의 실제 데이터와 모델의 요구사항에 맞춰 정교한 변환 로직이 필요합니다.
                # 현재는 플레이스홀더 값으로 채웁니다.
                
                # '연령' 및 '연령대분류' 계산
                today = date.today()
                age = today.year - profile.birth_date.year - ((today.month, today.day) < (profile.birth_date.month, profile.birth_date.day))
                
                # TODO: '연령대분류'의 정확한 코드로 변환하는 로직 필요 (예: 30대 -> 3)
                age_group_code = age // 10

                # TODO: 각 텍스트 선택지를 모델이 학습한 숫자 코드로 변환하는 로직 필요
                education_level_code = 12 # 예: '대졸' -> 12
                education_category_code = 4 # 예: '대졸' -> 4
                gender_code = 1 if profile.gender == 'M' else 2
                marital_status_code = 1 if profile.marital_status == 'MARRIED' else 2
                children_count = 1 if profile.has_children else 0 # 자녀 유무를 수로 변환 (가정)
                job_code = 1 # 예: '전문직' -> 1
                
                # TODO: 위험감수, 위험회피 성향 변환 로직 필요
                risk_taking_code = 1
                risk_averse_code = 0

                # TODO: 저축여부 변환 로직 필요
                saving_status_code = 3

                model_input_data = {
                    '연령대분류': age_group_code,
                    '교육수준분류': education_category_code,
                    '사업농업소득': 0,  # 누락된 정보, 0으로 가정
                    '자본이득소득': 0,  # 누락된 정보, 0으로 가정
                    '연령': age,
                    '금융위험감수': risk_taking_code,
                    '저축여부': saving_status_code,
                    '급여소득': profile.income or 0,
                    '금융위험회피': risk_averse_code,
                    '교육수준': education_level_code,
                    '가구주성별': gender_code,
                    '결혼상태': marital_status_code,
                    '자녀수': children_count,
                    '직업분류1': job_code,
                }
                
                # 2. 모델 로드 및 예측
                model_path = 'product_recommendation/multilabel_lgbm.joblib'
                model = joblib.load(model_path)
                
                # 모델 입력을 DataFrame으로 변환
                input_df = pd.DataFrame([model_input_data])
                
                # 예측 실행
                probabilities = model.predict_proba(input_df)
                
                # 3. 예측 결과 처리
                PRODUCT_CATEGORIES = ['MMMF', 'CDS', 'NMMF', 'STOCKS', 'RETQLIQ']
                
                # 가장 확률이 높은 카테고리 찾기
                top_category_index = probabilities[0].argmax()
                top_category = PRODUCT_CATEGORIES[top_category_index]

                # 'CDS' (예금)일 경우에만 추천 상품 가져오기
                if top_category == 'CDS':
                    deposits_data = api.get_deposit_products('020000')
                    deposits_list = deposits_data.get('result', {}).get('baseList', [])
                    recommended_products = deposits_list[:3] # 상위 3개 상품 추천
                    for product in recommended_products:
                        product['product_type_name'] = 'AI 추천 예금'


            except Exception as e:
                print(f"AI 추천 시스템 오류: {e}")
                # 오류가 발생해도 전체 페이지는 정상적으로 로드되도록 함
                recommended_products = []


        # 기존 상품 목록 로직
        deposits_data = api.get_deposit_products('020000')
        savings_data = api.get_saving_products('020000')
        
        deposits_list = deposits_data.get('result', {}).get('baseList', [])
        savings_list = savings_data.get('result', {}).get('baseList', [])
        
        for product in deposits_list:
            product['product_type'] = 'deposit'
            product['product_type_name'] = '예금'
            
        for product in savings_list:
            product['product_type'] = 'saving'
            product['product_type_name'] = '적금'
        
        all_products = deposits_list + savings_list
        
        all_paginator = Paginator(all_products, 9)
        all_page = request.GET.get('page', 1)
        all_page_obj = all_paginator.get_page(all_page)
        
        deposits_paginator = Paginator(deposits_list, 9)
        deposits_page = request.GET.get('deposits_page', 1)
        deposits_page_obj = deposits_paginator.get_page(deposits_page)
        
        savings_paginator = Paginator(savings_list, 9)
        savings_page = request.GET.get('savings_page', 1)
        savings_page_obj = savings_paginator.get_page(savings_page)

        
        
        context = {
            'recommended_products': recommended_products, # 추천 상품 추가
            'all_products': all_page_obj,
            'deposits': deposits_page_obj,
            'savings': savings_page_obj,
            'all_total': len(all_products),
            'deposits_total': len(deposits_list),
            'savings_total': len(savings_list),
            '위험감수형': 위험감수형,
            '위험회피형': 위험회피형,
            '금융위험태도': 금융위험태도 if request.user.is_authenticated and hasattr(request.user, 'profile') else 0,
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
def product_recommend_ai(request):
    """AI 금융상품 추천 페이지"""
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        
        # 여기에 AI 추천 로직 추가
        recommendations = {
            'user_info': {'age': 30, 'monthly_income': 400, 'gender': 'male', 'married': False},
            'recommendation_reason': '30대 남성으로, 안정적인 소득을 바탕으로 장기적인 자산 형성에 유리한 적금 상품을 추천합니다.',
            'products': [
                {'name': 'AI 추천 적금 1', 'bank': '코드은행', 'rate': 5.5, 'is_loan': False, 'join_way': '스마트폰', 'score': 95, 'product_type': '적금'},
                {'name': 'AI 추천 적금 2', 'bank': '데이터은행', 'rate': 5.2, 'is_loan': False, 'join_way': '인터넷', 'score': 92, 'product_type': '적금'},
                {'name': 'AI 추천 예금 1', 'bank': '알고은행', 'rate': 4.8, 'is_loan': False, 'join_way': '스마트폰', 'score': 88, 'product_type': '예금'},
            ],
            'total_candidates': 120,
        }
        
        context = {
            'user_input': user_input,
            'recommendations': recommendations,
            'processing_time': 123.45
        }
        return render(request, 'product_recommendation/product_recommend_ai.html', context)
    
    return render(request, 'product_recommendation/product_recommend_ai.html')
