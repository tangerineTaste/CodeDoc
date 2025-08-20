import json
import numpy as np
import joblib
import re
import os
from typing import Dict, List, Optional
from functools import lru_cache
import threading

class HighPerformanceFinancialRecommender:
    """고성능 금융상품 추천 시스템"""
    
    def __init__(self):
        import os
        
        print("== 고성능 금융상품 추천 시스템 초기화 중...==")
        
        # Django 앱 내 파일 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_file = os.path.join(current_dir, 'multilabel_lgbm.joblib')
        
        print(f" Django 앱 디렉토리: {current_dir}")
        print(f" 모델 파일 경로: {model_file}")
        print(f" 모델 파일 존재: {' 존재' if os.path.exists(model_file) else ' 없음'}")
        
        # 모델 로드
        self.model = None
        try:
            print(f" 모델 로드 시도중...")
            self.model = joblib.load(model_file)
            print(f" LGBM 모델 로드 성공!")
        except Exception as e:
            print(f" 모델 로드 실패: {e}")
            print(f" 에러 상세: {type(e).__name__}")
        
        # 데이터 로드 및 전처리
        self.products = self._load_products()
        self._precompute_product_features()
        
        # 캐시 초기화
        self._recommendation_cache = {}
        self._cache_lock = threading.Lock()
    
    def _load_products(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        """상품 데이터 로드 - 병렬 처리"""
        products = {}
        
        # Django 앱 내 data 폴더 경로
        data_path = os.path.join(current_dir, 'data')
        
        files = {
            'housing': os.path.join(data_path, 'mortgage_loans.json'),
            'rent': os.path.join(data_path, 'rent_loans.json'),
            'credit': os.path.join(data_path, 'credit_loans.json'),
            'deposit': os.path.join(data_path, 'bank_deposits.json'),
            'saving': os.path.join(data_path, 'bank_savings.json')
        }
        
        print(f" 데이터 폴더 경로: {data_path}")
        print(f" 데이터 폴더 존재: {' 존재' if os.path.exists(data_path) else ' 없음'}")
        
        # 각 파일 존재 여부 확인
        for category, filepath in files.items():
            exists = os.path.exists(filepath)
            print(f" {category} 파일: {filepath} -> {' 존재' if exists else ' 없음'}")
        
        # 간단한 단일 스레드 로드
        for category, filepath in files.items():
            try:
                print(f" {category} 로드 시도: {filepath}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                parsed_products = self._parse_product_data(data, category)
                products[category] = parsed_products
                print(f" {category} 로드 성공: {len(parsed_products)}개 상품")
            except Exception as e:
                print(f" {category} 로드 실패: {e}")
                products[category] = []
        
        return products
    
    def _parse_product_data(self, data, category):
        """JSON 데이터 파싱 - 최적화"""
        try:
            base_list = data['result']['baseList']
            option_list = data['result']['optionList']
            
            # 벡터화된 연산을 위한 딕셔너리 최적화
            rates = {}
            is_loan = category in {'housing', 'rent', 'credit'}  # set 사용으로 O(1) 검색
            
            # 옵션 데이터 빠른 처리
            for option in option_list:
                product_id = option.get('fin_prdt_cd')
                if not product_id:
                    continue
                
                rate = None
                if category == 'credit':
                    if option.get('crdt_lend_rate_type') == 'A':
                        rate = option.get('crdt_grad_1')
                elif is_loan:
                    rate = option.get('lend_rate_min')
                else:
                    rate = option.get('intr_rate2') or option.get('intr_rate')
                
                if rate and rate > 0:
                    rate = float(rate)
                    if product_id not in rates:
                        rates[product_id] = rate
                    else:
                        # 대출은 최저금리, 예적금은 최고금리
                        if is_loan:
                            rates[product_id] = min(rates[product_id], rate)
                        else:
                            rates[product_id] = max(rates[product_id], rate)
            
            # 상품 정보 통합 - 리스트 컴프리헨션으로 최적화
            products = []
            for product in base_list:
                product_id = product.get('fin_prdt_cd')
                if product_id in rates:
                    if category == 'credit':
                        features = f"상품유형: {product.get('crdt_prdt_type_nm', '')}"
                        max_limit = "신용도에 따라 결정"
                    else:
                        features = product.get('spcl_cnd', '') if not is_loan else product.get('loan_inci_expn', '')
                        max_limit = product.get('max_limit') or product.get('loan_lmt', '')
                    
                    products.append({
                        'name': product.get('fin_prdt_nm', ''),
                        'bank': product.get('kor_co_nm', ''),
                        'rate': rates[product_id],
                        'is_loan': is_loan,
                        'join_way': product.get('join_way', '영업점'),
                        'features': features,
                        'max_limit': max_limit,
                        'product_id': product_id
                    })
            
            # 정렬 최적화
            return sorted(products, key=lambda x: x['rate'], reverse=not is_loan)
            
        except Exception as e:
            print(f"파싱 오류: {e}")
            return []
    
    def _precompute_product_features(self):
        """상품 특성 사전 계산으로 성능 향상"""
        print(" 상품 특성 사전 계산 중...")
        
        # 키워드 매핑 사전 정의
        self.keyword_mappings = {
            'term_keywords': {
                'long_term': ['5년', '장기', '미래', '10년'],
                'medium_term': ['3년', '4년', '중기'],
                'short_term': ['1년', '2년', '단기', '6개월']
            },
            'target_keywords': {
                'youth': ['청년', 'MZ', '20대', '30대', '젊은'],
                'premium': ['프리미엄', 'VIP', '골드', '특별', 'GOLD'],
                'simple': ['자유', '간편', '생활', '시작', '기본'],
                'family': ['가족', '부부', '신혼', '패밀리']
            }
        }
        
        # 각 상품별 특성 사전 계산
        for category in self.products:
            for product in self.products[category]:
                name_lower = product['name'].lower()
                features_lower = product['features'].lower()
                text = f"{name_lower} {features_lower}"
                
                # 기간별 특성
                product['term_type'] = 'medium_term'  # 기본값
                for term_type, keywords in self.keyword_mappings['term_keywords'].items():
                    if any(keyword in text for keyword in keywords):
                        product['term_type'] = term_type
                        break
                
                # 타겟별 특성
                product['target_type'] = 'general'  # 기본값
                for target_type, keywords in self.keyword_mappings['target_keywords'].items():
                    if any(keyword in text for keyword in keywords):
                        product['target_type'] = target_type
                        break
                
                # 금리 등급 사전 계산
                rate = product['rate']
                if product['is_loan']:
                    if rate <= 3.0:
                        product['rate_grade'] = 'excellent'
                    elif rate <= 4.0:
                        product['rate_grade'] = 'good'
                    elif rate <= 5.0:
                        product['rate_grade'] = 'average'
                    else:
                        product['rate_grade'] = 'high'
                else:
                    if rate >= 6.0:
                        product['rate_grade'] = 'excellent'
                    elif rate >= 5.0:
                        product['rate_grade'] = 'good'
                    elif rate >= 4.0:
                        product['rate_grade'] = 'average'
                    else:
                        product['rate_grade'] = 'low'
        
        print(" 특성 계산 완료!")
    
    @lru_cache(maxsize=1000)
    def parse_input(self, user_input):
        """사용자 입력 파싱 - 캐싱으로 성능 향상"""
        result = {}
        
        # 정규식 컴파일된 패턴 사용
        age_pattern = re.compile(r'(\d{1,2})살|(\d{1,2})세|(\d{2})대')
        age_match = age_pattern.search(user_input)
        if age_match:
            if age_match.group(3):
                result['age'] = int(age_match.group(3)) + 5
            else:
                result['age'] = int(age_match.group(1) or age_match.group(2))
        
        # 소득 패턴들을 한 번에 처리
        income_patterns = [
            (re.compile(r'월급.*?(\d+)만'), 1),
            (re.compile(r'월.*?(\d+)만'), 1),
            (re.compile(r'연봉.*?(\d+)만'), 12),
            (re.compile(r'소득.*?(\d+)만'), 1)
        ]
        
        for pattern, divisor in income_patterns:
            income_match = pattern.search(user_input)
            if income_match:
                result['monthly_income'] = int(income_match.group(1)) // divisor
                break
        
        # 성별, 결혼 여부 등 빠른 키워드 검색
        if any(word in user_input for word in ['남자', '남성']):
            result['gender'] = 'male'
        elif any(word in user_input for word in ['여자', '여성']):
            result['gender'] = 'female'
        
        if any(word in user_input for word in ['결혼', '신혼', '부부']):
            result['married'] = True
        elif any(word in user_input for word in ['미혼', '독신']):
            result['married'] = False
        
        # 목적 추출 - 우선순위 기반
        purpose_keywords = [
            ('housing', ['주택', '집', '내집마련']),
            ('rent', ['전세']),
            ('credit', ['대출']),
            ('saving', ['적금']),
            ('deposit', ['예금']),
            ('investment', ['투자'])
        ]
        
        for purpose, keywords in purpose_keywords:
            if any(keyword in user_input for keyword in keywords):
                if purpose == 'credit' and any(word in user_input for word in ['주택', '전세']):
                    continue  # 주택대출, 전세대출은 제외
                result['purpose'] = purpose
                break
        
        print(f"파싱 결과: {result}")
        return tuple(sorted(result.items()))  # 튜플로 변환하여 캐싱 가능
    
    def _calculate_advanced_score(self, product, age, income, purpose, married=False):
        """고급 점수 계산 알고리즘 - 수정됨"""
        score = 40  # 기본 점수 낮춤
        
        # 1. 나이별 맞춤 점수 (실제 차이 생성)
        age_score = 0
        if purpose == 'saving':
            if age <= 30:
                # 20-30대: 장기 적금 선호
                if product['term_type'] == 'long_term':
                    age_score = 25
                elif product['term_type'] == 'medium_term':
                    age_score = 15
                else:
                    age_score = 5
            elif age <= 40:
                # 30-40대: 중기 적금 선호
                if product['term_type'] == 'medium_term':
                    age_score = 20
                elif product['term_type'] == 'long_term':
                    age_score = 15
                else:
                    age_score = 10
            else:
                # 40대+: 단기 적금 선호
                if product['term_type'] == 'short_term':
                    age_score = 20
                elif product['term_type'] == 'medium_term':
                    age_score = 12
                else:
                    age_score = 5
        
        elif purpose in ['housing', 'rent']:
            if age <= 35:
                age_score = 20 if product['rate_grade'] in ['excellent', 'good'] else 10
            elif age <= 50:
                age_score = 15 if product['rate_grade'] in ['good', 'average'] else 8
            else:
                age_score = 10 if product['rate_grade'] != 'high' else 5
        
        # 2. 소득별 맞춤 점수 (실제 차이 생성)
        income_score = 0
        if income >= 500:
            # 고소득: 프리미엄 상품 선호
            if product['target_type'] == 'premium':
                income_score = 20
            else:
                income_score = 10
        elif income >= 300:
            # 중간소득: 일반 상품
            income_score = 15
        elif income > 0:
            # 저소득: 간편 상품 선호
            if product['target_type'] == 'simple':
                income_score = 15
            else:
                income_score = 8
        else:
            # 소득 정보 없음
            income_score = 12
        
        # 3. 금리 점수 (실제 금리 기반)
        rate = product['rate']
        if product['is_loan']:
            # 대출: 낮을수록 좋음
            if rate <= 3.0:
                rate_score = 20
            elif rate <= 4.0:
                rate_score = 15
            elif rate <= 5.0:
                rate_score = 10
            else:
                rate_score = 5
        else:
            # 예적금: 높을수록 좋음
            if rate >= 6.0:
                rate_score = 20
            elif rate >= 5.0:
                rate_score = 15
            elif rate >= 4.0:
                rate_score = 10
            elif rate >= 3.0:
                rate_score = 8
            else:
                rate_score = 5
        
        # 4. 특화 보너스
        bonus_score = 0
        
        # 타겟 매칭 보너스
        if age <= 35 and product['target_type'] == 'youth':
            bonus_score += 10
        elif married and product['target_type'] == 'family':
            bonus_score += 8
        
        # 가입 방법 보너스
        if age <= 40 and '스마트폰' in product['join_way']:
            bonus_score += 3
        elif age > 40 and '영업점' in product['join_way']:
            bonus_score += 3
        
        # 은행 신뢰도 보너스
        major_banks = ['국민은행', '신한은행', '하나은행', '우리은행']
        if any(bank in product['bank'] for bank in major_banks):
            bonus_score += 5
        
        total_score = score + age_score + income_score + rate_score + bonus_score
        
        # 디버깅을 위한 로그 (첫 번째 상품만)
        if product == self.products.get('saving', [{}])[0]:
            print(f"점수 계산 예시: 기본({score}) + 나이({age_score}) + 소득({income_score}) + 금리({rate_score}) + 보너스({bonus_score}) = {total_score}")
        
        return min(total_score, 100)
    
    def _customize_products_advanced(self, products, user_profile):
        """고급 상품 맞춤화"""
        age = user_profile.get('age', 30)
        income = user_profile.get('monthly_income', 300)
        purpose = user_profile.get('purpose', 'general')
        married = user_profile.get('married', False)
        
        # 벡터화된 점수 계산
        scored_products = []
        for product in products:
            score = self._calculate_advanced_score(product, age, income, purpose, married)
            
            product_copy = product.copy()
            product_copy['score'] = score
            scored_products.append(product_copy)
        
        # 다중 기준 정렬 (점수 > 금리 > 은행명)
        return sorted(scored_products, 
                     key=lambda x: (x['score'], 
                                   -x['rate'] if not x['is_loan'] else x['rate'],
                                   x['bank']), 
                     reverse=True)
    
    def recommend(self, user_input, top_n=5):
        """고성능 상품 추천"""
        # 파싱 결과를 딕셔너리로 변환
        parsed_tuple = self.parse_input(user_input)
        parsed = dict(parsed_tuple)
        
        # 캐시 키 생성
        cache_key = (parsed_tuple, top_n)
        
        # 캐시 확인
        with self._cache_lock:
            if cache_key in self._recommendation_cache:
                print("캐시에서 결과 반환")
                cached_result = self._recommendation_cache[cache_key].copy()
                cached_result['user_info'] = parsed
                return cached_result
        
        # 기본 추천 상품 선택
        purpose = parsed.get('purpose', 'general')
        
        if purpose == 'housing':
            base_products = self.products['housing']
        elif purpose == 'rent':
            base_products = self.products['rent']
        elif purpose == 'credit':
            base_products = self.products['credit']
        elif purpose == 'deposit':
            base_products = self.products['deposit']
        elif purpose == 'saving':
            base_products = self.products['saving']
        elif purpose == 'investment':
            base_products = self.products['deposit'][:3] + self.products['saving'][:4]
        else:
            base_products = self.products['deposit'][:3] + self.products['saving'][:4]
        
        # 고급 맞춤화 적용
        customized_products = self._customize_products_advanced(base_products, parsed)
        
        # 추천 이유 생성
        recommendation_reason = self._generate_recommendation_reason(parsed, customized_products[0] if customized_products else None)
        
        result = {
            'products': customized_products[:top_n],
            'recommendation_reason': recommendation_reason,
            'total_candidates': len(base_products)
        }
        
        # 캐시에 저장 (사용자 정보 제외)
        with self._cache_lock:
            if len(self._recommendation_cache) > 100:  # 캐시 크기 제한
                # 가장 오래된 항목 제거
                oldest_key = next(iter(self._recommendation_cache))
                del self._recommendation_cache[oldest_key]
            self._recommendation_cache[cache_key] = result.copy()
        
        result['user_info'] = parsed
        return result
    
    def _generate_recommendation_reason(self, user_info, top_product):
        """추천 이유 생성"""
        reasons = []
        age = user_info.get('age', 30)
        income = user_info.get('monthly_income', 300)
        purpose = user_info.get('purpose', 'general')
        
        if purpose == 'saving':
            if age <= 30:
                reasons.append("젊은 연령대로 장기 적금이 유리")
            elif age <= 40:
                reasons.append("중년층으로 중기 적금이 적합")
            else:
                reasons.append("안정적인 단기-중기 적금 추천")
        
        if income >= 500:
            reasons.append("고소득으로 프리미엄 상품 이용 가능")
        elif income >= 300:
            reasons.append("안정적인 소득으로 꾸준한 금융상품 이용 가능")
        
        if top_product:
            if top_product['rate_grade'] == 'excellent':
                reasons.append("최고 등급 금리 상품")
            elif top_product['rate_grade'] == 'good':
                reasons.append("우수한 금리 조건")
        
        return " | ".join(reasons) if reasons else "고객님 상황에 최적화된 상품 추천"
    
    def format_response(self, result):
        """결과 포맷팅 - 최적화"""
        lines = []
        lines.append("금융상품 추천 결과")
        lines.append("=" * 40)
        
        # 사용자 정보
        user_info = result['user_info']
        if user_info:
            lines.append("고객 정보:")
            info_items = []
            if 'age' in user_info:
                info_items.append(f"나이: {user_info['age']}세")
            if 'monthly_income' in user_info:
                info_items.append(f"월수입: {user_info['monthly_income']}만원")
            if 'gender' in user_info:
                gender_text = "남성" if user_info['gender'] == 'male' else "여성"
                info_items.append(f"성별: {gender_text}")
            if 'married' in user_info:
                married_text = "기혼" if user_info['married'] else "미혼"
                info_items.append(f"결혼: {married_text}")
            
            for item in info_items:
                lines.append(f"   {item}")
            lines.append("")
        
        # 추천 이유
        if 'recommendation_reason' in result:
            lines.append("추천 이유:")
            lines.append(f"   {result['recommendation_reason']}")
            lines.append("")
        
        # 추천 상품
        products = result['products']
        if products:
            lines.append(f"맞춤 추천 상품 (총 {result.get('total_candidates', len(products))}개 중 선별):")
            
            for i, product in enumerate(products, 1):
                lines.extend([
                    f"{i}. {product['name']}",
                    f"    {product['bank']}",
                    f"    {'최저금리' if product['is_loan'] else '최고금리'}: {product['rate']:.2f}%",
                    f"    가입방법: {product['join_way']}",
                    f"    맞춤도: {product['score']}/100"
                ])
                
                if product['features']:
                    features = product['features'][:100] + "..." if len(product['features']) > 100 else product['features']
                    lines.append(f"    특징: {features}")
                
                if product['max_limit']:
                    lines.append(f"    한도: {product['max_limit']}")
                lines.append("")
        else:
            lines.append("추천 상품이 없습니다.")
        
        return "\n".join(lines)

def main():
    """메인 실행"""
    recommender = HighPerformanceFinancialRecommender()
    
    print("\n=== 고성능 금융상품 추천 시스템 준비 완료 ===")
    print("팁: 나이, 소득, 목적을 함께 입력하면 더 정확한 추천을 받을 수 있습니다.")
    print("예시: '30대 남성이고 월급 400만원인데 적금 추천해줘'")
    
    while True:
        user_input = input("\n어떤 금융상품을 찾고 계신가요? (종료: quit): ")
        
        if user_input.lower() == 'quit':
            break
            
        import time
        start_time = time.time()
        
        result = recommender.recommend(user_input)
        response = recommender.format_response(result)
        
        end_time = time.time()
        
        print(f"\n{response}")
        print(f"\n처리시간: {(end_time - start_time)*1000:.1f}ms")
        
        # 계속할지 물어보기
        while True:
            continue_choice = input("\n다른 상품을 더 찾아보시겠습니까? (예/아니오): ").strip().lower()
            if continue_choice in ['예', 'y', 'yes', '네']:
                break  # 내부 while 루프 탈출하고 다시 상품 입력받기
            elif continue_choice in ['아니오', 'n', 'no', '아니요']:
                print("\n금융상품 추천 시스템을 종료합니다. 감사합니다!")
                return  # 전체 함수 종료
            else:
                print("'예' 또는 '아니오'로 답해주세요.")

if __name__ == "__main__":
    main()