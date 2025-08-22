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
    """상품소개 페이지"""
    '''
    # ===== 실제 머신러닝 모델 테스트 =====
    print("\n" + "="*60)
    print("   실제 머신러닝 모델 추천 테스트!")
    print("="*60)
    
    try:
        # 머신러닝 모델 로드
        import joblib
        import numpy as np
        import os
        
        model_path = os.path.join(os.path.dirname(__file__), 'multilabel_lgbm.joblib')
        print(f"모델 파일 경로: {model_path}")
        print(f"모델 파일 존재 여부: {os.path.exists(model_path)}")
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print(f"모델 로드 성공: {type(model)}")
            
            # 모델 정보 상세 확인
            print(f"모델 타입: {type(model)}")
            
            # MultiOutputClassifier인 경우 내부 estimator 확인
            if hasattr(model, 'estimators_'):
                print(f"내부 estimator 개수: {len(model.estimators_)}")
                if len(model.estimators_) > 0:
                    first_estimator = model.estimators_[0]
                    print(f"첫 번째 estimator 타입: {type(first_estimator)}")
                    
                    # LGBMClassifier의 피처 정보 확인
                    if hasattr(first_estimator, 'feature_name_'):
                        print(f"피처 이름들: {first_estimator.feature_name_}")
                    if hasattr(first_estimator, 'n_features_in_'):
                        print(f"기대하는 피처 개수: {first_estimator.n_features_in_}")
                    if hasattr(first_estimator, 'feature_importances_'):
                        print(f"피처 중요도: {first_estimator.feature_importances_}")
            
            # 전체 모델의 피처 정보
            if hasattr(model, 'n_features_in_'):
                print(f"전체 모델 기대 피처 개수: {model.n_features_in_}")
            
            # 테스트 데이터 준비
            test_data = {
                '교육수준분류': 3,    # 대학교 중퇴/전문대 졸업
                '연령대분류': 2,      # 26-35세
                '가구주성별': 1,      # 남성
                '결혼상태': 2,        # 미혼/기타
                '저축여부': 2,        # 일부 저축
                '직업분류1': 1,       # 일반 직장인/중간관리직
                '금융위험태도': -2  # 위험감수형
            }
            
            # 위험성향 계산
            금융위험태도 = test_data['금융위험태도']
            위험감수형, 위험회피형 = calculate_risk_preference(금융위험태도)
            
            # 모델이 기대하는 피처와 우리가 가진 피처 매핑
            print("\n=== 피처 매핑 시도 ===")
            
            # 우리가 가진 8개 데이터
            our_features = {
                '교육수준분류': test_data['교육수준분류'],
                '연령대분류': test_data['연령대분류'], 
                '가구주성별': test_data['가구주성별'],
                '결혼상태': test_data['결혼상태'],
                '저축여부': test_data['저축여부'],
                '직업분류1': test_data['직업분류1'],
                '위험감수형': 위험감수형,
                '위험회피형': 위험회피형
            }
            
            print(f"우리가 가진 8개 피처: {list(our_features.keys())}")
            
            # 모델이 기대하는 피처 이름 확인
            expected_features = []
            if hasattr(model, 'estimators_') and len(model.estimators_) > 0:
                first_estimator = model.estimators_[0]
                if hasattr(first_estimator, 'feature_name_'):
                    expected_features = first_estimator.feature_name_
                    print(f"모델이 기대하는 11개 피처: {expected_features}")
            
            if len(expected_features) == 11:
                print("\n=== 해결 방안 ===")
                print("방법 1: 부족한 3개 피처를 기본값(0)으로 채우기")
                print("방법 2: 8개 피처만으로 새 모델 재학습")
                print("방법 3: 가장 중요한 8개 피처만 선택")
                
                # 일단 기본값으로 채워서 테스트
                print("\n*** 방법 1 시도: 부족한 3개를 0으로 채우기 ***")
                
                # 모델이 기대하는 정확한 순서로 11개 피처 배열 생성
                input_features = np.zeros(11)
                
                # 모델 기대 순서: ['교육수준분류', '연령대분류', '금융위험감수', '금융위험회피', '저축여부', '급여소득', '연령', '가구주성별', '결혼상태', '자녀수', '직업분류1']
                input_features[0] = test_data['교육수준분류']    # 교육수준분류
                input_features[1] = test_data['연령대분류']      # 연령대분류
                input_features[2] = 위험감수형                   # 금융위험감수 (위험감수형으로 매핑)
                input_features[3] = 위험회피형                   # 금융위험회피 (위험회피형으로 매핑)
                input_features[4] = test_data['저축여부']        # 저축여부
                input_features[5] = 300                        # 급여소득 (기본값: 300만원)
                input_features[6] = 30                         # 연령 (기본값: 30세)
                input_features[7] = test_data['가구주성별']       # 가구주성별
                input_features[8] = test_data['결혼상태']        # 결혼상태
                input_features[9] = 0                          # 자녀수 (기본값: 0명)
                input_features[10] = test_data['직업분류1']      # 직업분류1
                
                input_features = input_features.reshape(1, -1)
                
            else:
                print("피처 이름 정보를 가져올 수 없습니다. 기본 방법으로 시도합니다.")
                # 기본 11개 배열 (8개 + 3개 기본값)
                input_features = np.array([
                    test_data['교육수준분류'],
                    test_data['연령대분류'],
                    test_data['가구주성별'],
                    test_data['결혼상태'],
                    test_data['저축여부'],
                    test_data['직업분류1'],
                    위험감수형,
                    위험회피형,
                    0, 0, 0  # 부족한 3개를 0으로 채움
                ]).reshape(1, -1)
            
            print(f"\n정확한 순서로 입력 데이터 준비:")
            model_feature_names = ['교육수준분류', '연령대분류', '금융위험감수', '금융위험회피', '저축여부', '급여소득', '연령', '가구주성별', '결혼상태', '자녀수', '직업분류1']
            for i, (name, value) in enumerate(zip(model_feature_names, input_features[0])):
                status = "✅ 실제값" if value != 0 or name in ['교육수준분류', '연령대뵐류', '자녀수'] else "🔸 기본값"
                print(f"  {i:2d}. {name}: {value} {status}")
            
            print(f"\n입력 데이터 shape: {input_features.shape}")
            print(f"입력 데이터: {input_features}")
            
            # 머신러닝 모델로 예측
            print("\n머신러닝 모델 예측 실행 중...")
            
            # 확률 예측 (predict_proba) 먼저 확인
            print("\n=== 확률 예측 결과 ====")
            try:
                # MultiOutputClassifier에서 각 estimator의 확률 구하기
                probabilities = []
                for i, estimator in enumerate(model.estimators_):
                    proba = estimator.predict_proba(input_features)
                    # 클래스 1(양성)의 확률만 추출
                    if len(proba[0]) > 1:  # 이진 분류인 경우
                        prob_positive = proba[0][1]  # 클래스 1의 확률
                    else:
                        prob_positive = proba[0][0]  # 단일 클래스인 경우
                    probabilities.append(prob_positive)
                    print(f"  카테고리 {i} 확률: {prob_positive:.4f}")
                
                print(f"\n전체 확률 배열: {probabilities}")
                
                # 임계값 조정해서 예측
                thresholds = [0.3, 0.2, 0.1]  # 다양한 임계값 시도
                
                for threshold in thresholds:
                    predictions = [1 if prob > threshold else 0 for prob in probabilities]
                    print(f"\n임계값 {threshold}: {predictions} (추천 카테고리 수: {sum(predictions)})")
                    
                    if sum(predictions) > 0:  # 하나라도 추천되면
                        print(f"  → 임계값 {threshold}에서 추천 성공!")
                        break
                else:
                    print("\n모든 임계값에서 추천 실패. 가장 높은 확률 카테고리 선택...")
                    if probabilities:
                        max_idx = probabilities.index(max(probabilities))
                        predictions = [0] * len(probabilities)
                        predictions[max_idx] = 1
                        print(f"  → 최고 확률 카테고리 {max_idx} 선택: {predictions}")
                
            except Exception as e:
                print(f"확률 예측 실패: {e}")
                # 기본 predict 방법 사용
                predictions = model.predict(input_features)
                print(f"기본 예측 결과: {predictions}")
            
            # 기존 predict 결과도 확인
            prediction = model.predict(input_features)
            
            print(f"예측 결과 shape: {prediction.shape}")
            print(f"예측 결과: {prediction}")
            
            # 예측 결과 해석 및 상품 매칭
            print(f"\n=== 머신러닝 추천 결과 ====")
            
            # 확률 기반으로 얻은 predictions 사용 (위에서 계산된 것)
            if 'predictions' in locals() and sum(predictions) > 0:
                final_predictions = predictions
                print(f"확률 기반 최종 예측: {final_predictions}")
            else:
                # 확률 기반 예측이 실패한 경우 기본 예측 사용
                final_predictions = prediction[0] if len(prediction) > 0 else [0, 0, 0, 0, 0]
                print(f"기본 예측 사용: {final_predictions}")
            
            # 카테고리 매핑 (matching.py 기준으로 추정)
            category_mapping = {
                0: '예금상품',
                1: '적금상품', 
                2: '주택대출',
                3: '신용대출',
                4: '전세대출'
            }
            
            print(f"\n추천된 상품 카테고리:")
            recommended_categories = []
            for i, pred in enumerate(final_predictions):
                if pred == 1:
                    category_name = category_mapping.get(i, f'카테고리 {i}')
                    recommended_categories.append(category_name)
                    print(f"  ✅ {category_name} (카테고리 {i})")
            
            if not recommended_categories:
                print("  ❌ 추천된 카테고리가 없습니다.")
                # 가장 높은 확률의 카테고리라도 보여주기
                if 'probabilities' in locals():
                    max_idx = probabilities.index(max(probabilities))
                    max_category = category_mapping.get(max_idx, f'카테고리 {max_idx}')
                    print(f"  🔸 가장 적합한 카테고리: {max_category} (확률: {max(probabilities):.4f})")
            else:
                print(f"\n총 {len(recommended_categories)}개 카테고리 추천: {', '.join(recommended_categories)}")
                
                # 실제 상품 데이터 가져오기
                print("\n=== 실제 상품 추천 ====")
                try:
                    from .matching import HighPerformanceFinancialRecommender
                    recommender = HighPerformanceFinancialRecommender()
                    print("하이퍼포먼스 추천시스템 로드 성공")
                    
                    # 신용대출 상품 보여주기
                    if '신용대출' in recommended_categories:
                        credit_products = recommender.products.get('credit', [])
                        print(f"\n신용대출 상품 {len(credit_products)}개 발견:")
                        for i, product in enumerate(credit_products[:3], 1):
                            print(f"  {i}. {product['name']} - {product['bank']} - 금리: {product['rate']:.2f}%")
                except Exception as e:
                    print(f"상품 데이터 로드 오류: {e}")
                
        else:
            print("오류: 머신러닝 모델 파일을 찾을 수 없습니다!")
            
    except Exception as e:
        print(f"머신러닝 모델 테스트 오류: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("="*60)
    print("   머신러닝 모델 테스트 완료!")
    print("="*60 + "\n")
    # ===== 머신러닝 테스트 끝 =====
    '''
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
