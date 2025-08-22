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

def product_recommend(request):
    """내게맞는상품찾기 페이지"""
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

def product_detail(request, product_type, product_id):
    """상품상세 페이지"""
    # 추후 구현
    context = {
        'product_type': product_type,
        'product_id': product_id
    }
    return render(request, 'product_recommendation/product_detail.html', context)
