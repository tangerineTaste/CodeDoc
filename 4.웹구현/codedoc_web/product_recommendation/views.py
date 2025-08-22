import json
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from .financial_item_list import FinancialProductAPI
import joblib
import pandas as pd
from datetime import date

def product_list(request):
    """상품소개 페이지"""
    try:
        api = FinancialProductAPI()
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
