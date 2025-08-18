import json
import numpy as np
import joblib
import re
import os
from typing import Dict, List, Optional

class SimpleFinancialRecommender:
    """간단한 금융상품 추천 시스템"""
    
    def __init__(self):
        import os
        
        print("== 금융상품 추천 시스템 초기화 중...==")
        
        # 현재 폴더의 파일 직접 로드
        model_file = 'multilabel_lgbm.joblib'
        
        print(f" 현재 작업 디렉토리: {os.getcwd()}")
        print(f" 파일 존재 확인: {model_file} -> {' 존재' if os.path.exists(model_file) else ' 없음'}")
        
        # 모델 로드
        self.model = None
        try:
            print(f" 모델 로드 시도중...")
            self.model = joblib.load(model_file)
            print(f" LGBM 모델 로드 성공!")
        except Exception as e:
            print(f" 모델 로드 실패: {e}")
            print(f" 에러 상세: {type(e).__name__}")
        
        # 데이터 로드
        self.products = self._load_products()
    
    def _load_products(self):
        """상품 데이터 로드"""
        products = {}
        files = {
            'housing': '../1.데이터수집/data/mortgage_loans.json',
            'rent': '../1.데이터수집/data/rent_loans.json',
            'credit': '../1.데이터수집/data/credit_loans.json',
            'deposit': '../1.데이터수집/data/bank_deposits.json',
            'saving': '../1.데이터수집/data/bank_savings.json'
        }
        
        for category, filepath in files.items():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                products[category] = self._parse_product_data(data, category)
                print(f" {category} 로드: {len(products[category])}개")
            except:
                print(f" {filepath} 로드 실패")
                products[category] = []
        
        return products
    
    def _parse_product_data(self, data, category):
        """JSON 데이터 파싱"""
        try:
            # 모든 JSON은 동일한 구조: result.baseList, result.optionList
            base_list = data['result']['baseList']
            option_list = data['result']['optionList']
            
            # 상품별 최적 금리 계산
            rates = {}
            is_loan = category in ['housing', 'rent', 'credit']
            
            for option in option_list:
                product_id = option.get('fin_prdt_cd')
                if not product_id:
                    continue
                
                if category == 'credit':
                    # 신용대출: crdt_lend_rate_type이 "A"(대출금리)인 경우만
                    if option.get('crdt_lend_rate_type') == 'A':
                        # crdt_grad_1이 가장 좋은 등급 금리
                        rate = option.get('crdt_grad_1')
                        if rate and rate > 0:
                            if product_id not in rates or rate < rates[product_id]:
                                rates[product_id] = float(rate)
                elif is_loan:
                    # 주택/전세대출: lend_rate_min 사용
                    rate = option.get('lend_rate_min')
                    if rate and rate > 0:
                        if product_id not in rates or rate < rates[product_id]:
                            rates[product_id] = float(rate)
                else:
                    # 예적금: intr_rate2 또는 intr_rate 사용
                    rate = option.get('intr_rate2') or option.get('intr_rate')
                    if rate and rate > 0:
                        if product_id not in rates or rate > rates[product_id]:
                            rates[product_id] = float(rate)
            
            # 상품 정보 통합
            products = []
            for product in base_list:
                product_id = product.get('fin_prdt_cd')
                if product_id in rates:
                    # 신용대출의 경우 추가 필드
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
                        'max_limit': max_limit
                    })
            
            # 정렬 (대출: 낮은 금리순, 예적금: 높은 금리순)
            return sorted(products, key=lambda x: x['rate'], reverse=not is_loan)
            
        except Exception as e:
            print(f"파싱 오류: {e}")
            return []
    
    def parse_input(self, user_input):
        """사용자 입력 파싱"""
        result = {}
        
        # 나이 추출
        age_match = re.search(r'(\d{1,2})살|(\d{1,2})세|(\d{2})대', user_input)
        if age_match:
            if age_match.group(3):  # XX대
                result['age'] = int(age_match.group(3)) + 5
            else:
                result['age'] = int(age_match.group(1) or age_match.group(2))
        
        # 월급 추출
        income_match = re.search(r'월급.*?(\d+)만|월.*?(\d+)만', user_input)
        if income_match:
            result['monthly_income'] = int(income_match.group(1) or income_match.group(2))
        
        # 가족 수 추출
        family_match = re.search(r'가족.*?(\d+)명|(\d+)명.*?가족', user_input)
        if family_match:
            result['family_size'] = int(family_match.group(1) or family_match.group(2))
        
        # 목적 추출
        if '주택' in user_input or '집' in user_input:
            result['purpose'] = 'housing'
        elif '전세' in user_input:
            result['purpose'] = 'rent'
        elif '대출' in user_input and '주택' not in user_input:
            result['purpose'] = 'credit'
        elif '투자' in user_input or '적금' in user_input or '예금' in user_input:
            result['purpose'] = 'investment'
        
        print(f"파싱 결과: {result}")
        return result
    
    def recommend(self, user_input, top_n=5):
        """상품 추천"""
        # 입력 파싱
        parsed = self.parse_input(user_input)
        
        # 목적별 추천
        if parsed.get('purpose') == 'housing':
            recommended = self.products['housing'][:top_n]
        elif parsed.get('purpose') == 'rent':
            recommended = self.products['rent'][:top_n]
        elif parsed.get('purpose') == 'credit':
            recommended = self.products['credit'][:top_n]
        elif parsed.get('purpose') == 'investment':
            recommended = self.products['deposit'][:2] + self.products['saving'][:3]
        else:
            # 일반 추천
            recommended = self.products['deposit'][:2] + self.products['saving'][:3]
        
        return {
            'user_info': parsed,
            'products': recommended
        }
    
    def format_response(self, result):
        """결과 포맷팅"""
        response = []
        response.append(" 금융상품 추천 결과")
        response.append("=" * 40)
        
        # 사용자 정보
        user_info = result['user_info']
        if user_info:
            response.append(" 고객 정보:")
            if 'age' in user_info:
                response.append(f"   나이: {user_info['age']}세")
            if 'monthly_income' in user_info:
                response.append(f"   월수입: {user_info['monthly_income']}만원")
            if 'family_size' in user_info:
                response.append(f"   가족: {user_info['family_size']}명")
            response.append("")
        
        # 추천 상품
        products = result['products']
        if products:
            response.append("🏆 추천 상품:")
            for i, product in enumerate(products, 1):
                response.append(f"{i}. {product['name']}")
                response.append(f"    {product['bank']}")
                if product['is_loan']:
                    response.append(f"    최저금리: {product['rate']:.2f}%")
                else:
                    response.append(f"    최고금리: {product['rate']:.2f}%")
                response.append(f"    가입방법: {product['join_way']}")
                
                if product['features']:
                    features = product['features'][:100] + "..." if len(product['features']) > 100 else product['features']
                    response.append(f"    특징: {features}")
                
                if product['max_limit']:
                    response.append(f"    한도: {product['max_limit']}")
                response.append("")
        else:
            response.append(" 추천 상품이 없습니다.")
        
        return "\n".join(response)

def main():
    """메인 실행"""
    recommender = SimpleFinancialRecommender()
    
    while True:
        user_input = input("\n💡 어떤 금융상품을 찾고 계신가요? (종료: quit): ")
        
        if user_input.lower() == 'quit':
            break
            
        result = recommender.recommend(user_input)
        response = recommender.format_response(result)
        print("\n" + response)

if __name__ == "__main__":
    main()