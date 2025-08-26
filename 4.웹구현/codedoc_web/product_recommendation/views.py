# product_recommendation/views.py
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from .utils import ProductDataLoader, ProductPaginator
from .category_recommendations import get_category_recommendations_for_user, get_default_products_by_category
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
    """
    상품 목록 페이지
    기존 API 데이터(예금/적금) + 새로운 파일 기반 데이터(펀드/주식/MMF) 통합
    + 카테고리별 사용자 맞춤 AI 추천 기능
    """
    context = {}
    
    try:
        # 1. 로그인한 사용자에게 AI 추천 상품 제공
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            try:
                # 전체 카테고리 추천
                recommended_products = get_ai_recommendations_for_user(request.user)
                if recommended_products:
                    context['recommended_products'] = recommended_products
                    print(f"사용자 {request.user.username}에게 AI 추천 상품 {len(recommended_products)}개 제공")
                
                # 카테고리별 추천 상품 생성
                category_recommendations = get_category_recommendations_for_user(request.user)
                context.update(category_recommendations)
                
            except Exception as e:
                print(f"AI 추천 시스템 오류: {e}")
                # 오류가 발생해도 전체 페이지는 정상 로드
        
        # 2. 기존 API 데이터 (예금, 적금) - 실제 API 호출
        deposits = get_deposit_products()
        savings = get_saving_products()
        
        # 3. 새로운 파일 기반 데이터 로드
        print("파일 기반 데이터 로딩 시작...")
        funds = ProductDataLoader.get_funds()
        stocks = ProductDataLoader.get_stocks()
        mmf_products = ProductDataLoader.get_mmf_products()
        
        print(f"로드된 데이터: 예금 {len(deposits)}개, 적금 {len(savings)}개, 펀드 {len(funds)}개, 주식 {len(stocks)}개, MMF {len(mmf_products)}개")
        
        # 4. 전체 상품 통합 (API + 파일 기반)
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
        
        # 5. 페이지네이션 처리
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
        
        # 6. 컨텍스트 구성
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
    """AI 추천 페이지"""
    import time
    context = {}
    
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        context['user_input'] = user_input
        
        if user_input:
            try:
                # 실제 AI 추천 시스템 사용
                print(f"AI 추천 시작: {user_input}")
                start_time = time.time()
                
                # HighPerformanceFinancialRecommender 임포트 및 실행
                from .matching import HighPerformanceFinancialRecommender
                
                # 추천 시스템 초기화 및 실행
                recommender = HighPerformanceFinancialRecommender()
                result = recommender.recommend(user_input, top_n=6)  # 6개 추천
                
                end_time = time.time()
                processing_time = int((end_time - start_time) * 1000)  # 밀리초로 변환
                
                print(f"AI 추천 완료: {len(result.get('products', []))}개 상품, {processing_time}ms")
                
                # 결과 포맷팅
                context['recommendations'] = {
                    'user_info': result.get('user_info', {}),
                    'recommendation_reason': result.get('recommendation_reason', '고객님에게 최적화된 상품을 추천했습니다.'),
                    'products': result.get('products', []),
                    'total_candidates': result.get('total_candidates', 0)
                }
                context['processing_time'] = processing_time
                
                # 각 상품에 product_type 추가 (HTML 템플릿에서 사용)
                for product in context['recommendations']['products']:
                    if product.get('is_investment', False):
                        product['product_type'] = '투자상품'
                    else:
                        product['product_type'] = '예적금'
                        
                print(f"추천 결과: {context['recommendations']['total_candidates']}개 후보 중 {len(context['recommendations']['products'])}개 추천")
                
            except Exception as e:
                print(f"AI 추천 시스템 오류: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # 오류 발생 시 기본 추천 제공
                context['recommendations'] = {
                    'user_info': {'age': 30, 'monthly_income': 300},
                    'recommendation_reason': f'추천 시스템 일시 오류로 인해 기본 상품을 안내드립니다. (오류: {str(e)})',
                    'products': [
                        {
                            'name': '기본 정기예금',
                            'bank': '시중은행',
                            'rate': 3.5,
                            'is_loan': False,
                            'product_type': '예금',
                            'join_way': '온라인/영업점',
                            'score': 75
                        },
                        {
                            'name': '기본 정기적금',
                            'bank': '시중은행',
                            'rate': 3.8,
                            'is_loan': False,
                            'product_type': '적금',
                            'join_way': '온라인/영업점',
                            'score': 70
                        }
                    ],
                    'total_candidates': 2
                }
                context['error'] = f'추천 시스템 일시 오류: {str(e)}'
    
    return render(request, 'product_recommendation/product_recommend_ai.html', context)


def get_ai_recommendations_for_user(user):
    """
    로그인한 사용자에게 AI 추천 상품 제공
    사용자의 프로필 정보를 바탕으로 머신러닝 추천
    '전체' 카테고리에서는 사용자가 선호할 가능성이 가장 높은 카테고리 상품 3개 추천
    """
    try:
        profile = user.profile
        
        # 사용자 선호도 분석
        preferred_category = analyze_user_preference(profile)
        print(f"사용자 {user.username}의 선호 카테고리: {preferred_category}")
        
        # 선호 카테고리 기반으로 추천 입력 생성
        user_input_parts = []
        
        # 연령대 정보
        age_map = {
            1: '23세',  # 18-25세
            2: '30세',  # 26-35세 
            3: '40세',  # 36-45세
            4: '50세',  # 46-55세
            5: '60세',  # 56-65세
            6: '70세'   # 66세 이상
        }
        
        if profile.연령대분류:
            user_input_parts.append(age_map.get(profile.연령대분류, '30세'))
        
        # 성별 정보
        if profile.가구주성별 == 1:
            user_input_parts.append('남성')
        elif profile.가구주성별 == 2:
            user_input_parts.append('여성')
        
        # 결혼 상태
        if profile.결혼상태 == 1:
            user_input_parts.append('기혼')
        elif profile.결혼상태 == 2:
            user_input_parts.append('미혼')
        
        # 직업 및 소득 추정
        income_map = {
            1: '월급 350만원',  # 일반 직장인
            2: '월급 600만원',  # 고소득 전문직
            3: '연금 수급자',   # 은퇴자
            4: '월급 200만원'   # 저소득층
        }
        
        if profile.직업분류1:
            user_input_parts.append(income_map.get(profile.직업분류1, '월급 300만원'))
        
        # 선호 카테고리에 따른 목적 결정
        category_purpose_map = {
            'deposit': '안전한 예금상품',
            'saving': '꾸준한 적금상품',
            'fund': '전문가 운용 펀드',
            'stock': '성장 가능성 높은 주식',
            'mmf': '유동성 좋은 머니마켓펀드'
        }
        purpose = category_purpose_map.get(preferred_category, '적금')
        user_input_parts.append(purpose)
        
        # 가상 사용자 입력 생성
        user_input = ' '.join(user_input_parts) + ' 추천해주세요'
        
        print(f"사용자 {user.username}에 대한 AI 추천 입력: {user_input}")
        
        # AI 추천 시스템 호출
        from .matching import HighPerformanceFinancialRecommender
        recommender = HighPerformanceFinancialRecommender()
        result = recommender.recommend(user_input, top_n=3)  # 3개 추천
        
        # 추천 결과를 템플릿에서 사용할 수 있는 형식으로 변환
        recommended_products = []
        for product in result.get('products', []):
            # 기존 상품 형식에 맞게 변환
            converted_product = {
                'fin_prdt_nm': product['name'],
                'kor_co_nm': product['bank'],
                'join_way': product.get('join_way', '온라인 가입 가능'),
                'product_type': get_product_type_from_ai_result(product),
                'product_type_name': get_product_type_name_from_ai_result(product),
                'rate': product.get('rate', 0),
                'return_rate': product.get('rate', 0),  # 펀드/MMF용
                'score': product.get('score', 0),
                'preferred_category': preferred_category  # 선호 카테고리 추가
            }
            recommended_products.append(converted_product)
        
        print(f"AI 추천 완료: {len(recommended_products)}개 상품 추천 (선호 카테고리: {preferred_category})")
        return recommended_products
        
    except Exception as e:
        print(f"AI 추천 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_user_preference(profile):
    """
    사용자 프로필을 분석하여 선호할 가능성이 가장 높은 상품 카테고리 결정
    펀드, 주식, MMF도 더 선호되도록 개선
    """
    # 기본값 설정
    risk_attitude = profile.금융위험태도 or 0
    savings_habit = profile.저축여부 or 2
    age_group = profile.연령대분류 or 2
    
    # 점수 기반 선호도 계산 (몽든 카테고리에 기회를 주도록 개선)
    scores = {
        'deposit': 1,
        'saving': 1, 
        'fund': 1,
        'stock': 1,
        'mmf': 1
    }
    
    # 1. 연령대별 점수 (더 균형적으로 조정)
    if age_group <= 2:  # 35세 이하 - 다양한 투자 선호
        scores['fund'] += 3
        scores['stock'] += 2
        scores['mmf'] += 2
        scores['saving'] += 1
    elif age_group <= 4:  # 36-55세 - 안정성 및 수익성 균형
        scores['fund'] += 4
        scores['mmf'] += 3
        scores['saving'] += 2
        scores['stock'] += 1
    else:  # 56세 이상 - 안정성 중심 하지만 다양성 유지
        scores['mmf'] += 3
        scores['deposit'] += 3
        scores['saving'] += 2
        scores['fund'] += 1
    
    # 2. 금융위험태도별 점수 (투자상품에 더 많은 기회)
    if risk_attitude < -1:  # 고위험 선호
        scores['stock'] += 4
        scores['fund'] += 3
        scores['mmf'] += 1
    elif risk_attitude < 0:  # 중간 위험
        scores['fund'] += 4
        scores['stock'] += 2
        scores['mmf'] += 3
    elif risk_attitude <= 1:  # 안정 선호
        scores['mmf'] += 3
        scores['saving'] += 3
        scores['deposit'] += 2
        scores['fund'] += 1
    else:  # 초안정 선호
        scores['deposit'] += 3
        scores['saving'] += 2
        scores['mmf'] += 1
    
    # 3. 저축여부별 점수
    if savings_habit == 3:  # 적극적 저축
        scores['saving'] += 2
        scores['fund'] += 1
        scores['deposit'] += 1
    elif savings_habit == 2:  # 일부 저축
        scores['fund'] += 2
        scores['mmf'] += 1
        scores['saving'] += 1
    # savings_habit == 1 (저축 안함) - 투자상품 선호
    else:
        scores['fund'] += 2
        scores['stock'] += 1
    
    # 가장 높은 점수의 카테고리 반환
    preferred_category = max(scores, key=scores.get)
    
    print(f"사용자 선호도 점수: {scores}")
    print(f"최종 선호 카테고리: {preferred_category}")
    
    return preferred_category


def determine_investment_purpose(profile):
    """
    사용자 프로필을 기반으로 투자 목적 결정
    """
    # 금융위험태도가 0 이상이면 위험회피형, 미만이면 위험감수형
    risk_attitude = profile.금융위험태도 or 0
    savings_habit = profile.저축여부 or 2  # 기본값: 일부 저축
    age_group = profile.연령대분류 or 2  # 기본값: 26-35세
    
    # 연령대가 높고 위험회피형이면 예금/적금 선호
    if age_group >= 4 and risk_attitude >= 0:  # 46세 이상, 위험회피
        if savings_habit == 3:  # 적극적 저축
            return '적금'
        else:
            return '예금'
    
    # 젊고 위험감수형이면 투자상품 선호
    elif age_group <= 2 and risk_attitude < 0:  # 35세 이하, 위험감수
        return '주식 투자'
    
    # 중간 연령대와 중간 위험 성향이면 펀드 선호
    elif 2 <= age_group <= 3:  # 26-45세
        return '펀드 투자'
    
    # 기본값은 적금
    else:
        return '적금'


def get_product_type_from_ai_result(product):
    """
    AI 추천 결과에서 상품 타입 추출 (개선된 버전)
    """
    product_name = product.get('name', '').lower()
    product_id = product.get('product_id', '').lower()
    
    # 1. 명시적인 키워드로 판단
    if '펀드' in product_name or 'fund' in product_name:
        return 'fund'
    elif 'mmf' in product_name or '머니마켓' in product_name or 'money' in product_name:
        return 'mmf'
    elif '주식' in product_name or 'stock' in product_name or product_id.startswith('stock'):
        return 'stock'
    elif '적금' in product_name or 'saving' in product_name:
        return 'saving'
    elif '예금' in product_name or 'deposit' in product_name:
        return 'deposit'
    
    # 2. is_investment 필드로 대분류 판단
    if product.get('is_investment', False):
        # 투자상품인 경우 - 더 세밀하게 분류
        if any(keyword in product_name for keyword in ['성장', '배당', '대형', '업종', '주가']):
            return 'stock'
        elif any(keyword in product_name for keyword in ['단기', '현금', '유동성']):
            return 'mmf'
        else:
            return 'fund'  # 기본 투자상품은 펀드
    else:
        # 비투자상품인 경우
        if any(keyword in product_name for keyword in ['모으기', '저축', '매월']):
            return 'saving'
        else:
            return 'deposit'  # 기본 비투자상품은 예금


def get_product_type_name_from_ai_result(product):
    """
    AI 추천 결과에서 상품 타입 이름 추출
    """
    product_type = get_product_type_from_ai_result(product)
    type_name_map = {
        'deposit': '예금',
        'saving': '적금',
        'fund': '펀드',
        'stock': '주식',
        'mmf': '머니마켓펀드'
    }
    return type_name_map.get(product_type, '금융상품')


# 기존 product_list 함수 백업 (참고용)
def product_list_old(request):
    """상품소개 페이지 (기존 백업 버전)"""
    try:
        print("상품 데이터 로딩 시작...")
        api = FinancialProductAPI()
        print("API 객체 생성 성공")
        
        # 로그인된 사용자의 금융위험태도 처리
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            금융위험태도 = request.user.profile.금융위험태도 or 0
            위험감수형, 위험회피형 = calculate_risk_preference(금융위험태도)
        else:
            위험감수형, 위험회피형 = 0, 0
        
        print("\n=== 디버깅 정보 ===")
        print(f"로그인 상태: {request.user.is_authenticated}")
        if request.user.is_authenticated:
            print(f"사용자: {request.user.username}")
            print(f"금융위험태도: {금융위험태도}")
            print(f"위험감수형: {위험감수형}")
            print(f"위험회피형: {위험회피형}")
            
            if hasattr(request.user, 'profile'):
                profile = request.user.profile
                print(f"교육수준: {profile.교육수준분류}")
                print(f"연령대: {profile.연령대분류}")
                print(f"성별: {profile.가구주성별}")
                print(f"결혼상태: {profile.결혼상태}")
                print(f"저축여부: {profile.저축여부}")
                print(f"직업분류: {profile.직업분류1}")
            else:
                print("프로필 없음")
        else:
            print("비로그인 사용자")
        print("=====================\n")
        
        print("예금 상품 데이터 가져오는 중...")
        
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
