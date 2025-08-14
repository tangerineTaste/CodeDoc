import json
import numpy as np
import joblib
from typing import Dict, List, Optional
from dataclasses import dataclass
from decouple import config
import warnings
import re

warnings.filterwarnings('ignore', category=UserWarning)

@dataclass
class UserProfile:
    """사용자 프로필 데이터 클래스"""
    age: Optional[int] = None
    income: Optional[int] = None
    income_type: str = 'individual'
    marriage_status: Optional[int] = None
    children_count: int = 0
    financial_purpose: Optional[str] = None
    gender: Optional[int] = None
    confidence_score: float = 0.0

class SimpleRuleBasedExtractor:
    """규칙 기반 정보 추출기 (OpenAI 대신 사용)"""
    
    def __init__(self):
        # 나이 패턴
        self.age_patterns = {
            r'(\d{1,2})살': lambda m: int(m.group(1)),
            r'(\d{1,2})세': lambda m: int(m.group(1)),
            r'(\d{2})대\s*초반': lambda m: int(m.group(1)) + 2,
            r'(\d{2})대\s*중반': lambda m: int(m.group(1)) + 5,
            r'(\d{2})대\s*후반': lambda m: int(m.group(1)) + 8,
            r'(\d{2})대': lambda m: int(m.group(1)) + 5,
        }
        
        # 수입 패턴
        self.income_patterns = {
            r'월\s*(\d+)만?원?': lambda m: int(m.group(1)) * 12,
            r'월\s*수입\s*(\d+)만?원?': lambda m: int(m.group(1)) * 12,
            r'월\s*급여\s*(\d+)만?원?': lambda m: int(m.group(1)) * 12,
            r'한달에?\s*(\d+)만?원?': lambda m: int(m.group(1)) * 12,
            r'매월\s*(\d+)만?원?': lambda m: int(m.group(1)) * 12,
            r'연봉\s*(\d+)만?원?': lambda m: int(m.group(1)),
            r'년\s*(\d+)만?원?': lambda m: int(m.group(1)),
            r'(\d+)천만?원?': lambda m: int(m.group(1)) * 1000,
        }
        
        # 성별 패턴
        self.gender_patterns = {
            r'남성': 1,
            r'남자': 1, 
            r'여성': 0,
            r'여자': 0,
        }
        
        # 결혼 상태 패턴
        self.marriage_patterns = {
            r'기혼': 1,
            r'결혼': 1,
            r'부부': 1,
            r'배우자': 1,
            r'신혼': 1,
            r'미혼': 0,
            r'독신': 0,
            r'솔로': 0,
        }
        
        # 자녀 패턴
        self.children_patterns = {
            r'자녀\s*(\d+)명': lambda m: int(m.group(1)),
            r'아이\s*(\d+)명': lambda m: int(m.group(1)),
            r'(\d+)살\s*아이': lambda m: 1,
            r'아기': lambda m: 1,
        }
        
        # 금융 목적 패턴
        self.purpose_patterns = {
            r'주택|집|아파트|매매|구입|구매': 'housing',
            r'전세|월세|임대|보증금': 'rent',
            r'대출|신용|급전|현금': 'credit',
            r'투자|재테크|펀드|주식': 'investment',
            r'교육|학비|등록금': 'education',
            r'노후|연금|퇴직': 'retirement',
            r'적금|저축|모으기': 'savings',
        }
    
    def extract_with_rules(self, user_input: str) -> UserProfile:
        """규칙 기반 정보 추출"""
        print(f"🔍 규칙 기반 분석: {user_input}")
        
        profile = UserProfile()
        confidence_factors = []
        
        # 나이 추출
        for pattern, extractor in self.age_patterns.items():
            match = re.search(pattern, user_input)
            if match:
                profile.age = extractor(match)
                confidence_factors.append(0.3)
                print(f"✅ 나이 추출: {profile.age}세")
                break
        
        # 수입 추출
        for pattern, extractor in self.income_patterns.items():
            match = re.search(pattern, user_input)
            if match:
                profile.income = extractor(match)
                confidence_factors.append(0.3)
                
                # 가구소득 판별
                if '부부' in user_input or '합산' in user_input or '가구' in user_input:
                    profile.income_type = 'household'
                
                print(f"✅ 수입 추출: {profile.income}만원 ({profile.income_type})")
                break
        
        # 성별 추출
        for pattern, value in self.gender_patterns.items():
            if re.search(pattern, user_input):
                profile.gender = value
                confidence_factors.append(0.2)
                print(f"✅ 성별 추출: {'남성' if value == 1 else '여성'}")
                break
        
        # 결혼 상태 추출
        for pattern, value in self.marriage_patterns.items():
            if re.search(pattern, user_input):
                profile.marriage_status = value
                confidence_factors.append(0.1)
                print(f"✅ 결혼상태 추출: {'기혼' if value == 1 else '미혼'}")
                break
        
        # 자녀 수 추출
        for pattern, extractor in self.children_patterns.items():
            match = re.search(pattern, user_input)
            if match:
                profile.children_count = extractor(match)
                confidence_factors.append(0.1)
                print(f"✅ 자녀수 추출: {profile.children_count}명")
                break
        
        # 금융 목적 추출
        for pattern, purpose in self.purpose_patterns.items():
            if re.search(pattern, user_input):
                profile.financial_purpose = purpose
                confidence_factors.append(0.2)
                print(f"✅ 금융목적 추출: {purpose}")
                break
        
        # 신뢰도 계산
        profile.confidence_score = min(sum(confidence_factors), 1.0)
        
        print(f"📊 추출 완료 (신뢰도: {profile.confidence_score:.2f})")
        return profile

class OpenAIExtractor:
    """OpenAI 기반 정보 추출기 (백업용)"""
    
    def __init__(self, api_key: str):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-3.5-turbo"  # 실제 존재하는 모델
            self.available = True
            print("✅ OpenAI API 연결 성공")
        except Exception as e:
            print(f"⚠️ OpenAI API 사용 불가: {e}")
            self.available = False
    
    def extract_with_openai(self, user_input: str) -> UserProfile:
        """OpenAI 기반 정보 추출"""
        if not self.available:
            return UserProfile(confidence_score=0.1)
        
        try:
            prompt = f"""
다음 사용자 입력에서 정보를 추출하여 JSON으로 응답하세요.

사용자 입력: "{user_input}"

**추출 규칙:**
1. 나이 표현 변환:
   - "50대 중반" → 55
   - "30대 후반" → 38
   - "20대 초반" → 22
   
2. 소득 변환:
   - "월 300" → 3600 (월급 × 12)
   - "한달에 500" → 6000
   
3. 가족 관계:
   - "부부 합산" → household 소득
   
4. 금융 목적:
   - 주택구입 관련 → "housing"
   - 전세/월세 → "rent"
   - 투자/재테크 → "investment"
   - 노후준비 → "retirement"

**응답 형식 (JSON만):**
{{
    "age": 55,
    "income": 3600,
    "income_type": "individual",
    "marriage_status": 1,
    "children_count": 0,
    "financial_purpose": "housing",
    "gender": 1,
    "confidence_score": 0.95
}}

JSON 형태로만 응답하세요:
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 정확한 정보 추출 전문가입니다. JSON 형태로만 응답하세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # JSON 정리
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            elif content.startswith('```'):
                content = content.replace('```', '').strip()
            
            extracted_data = json.loads(content)
            
            profile = UserProfile(
                age=extracted_data.get('age'),
                income=extracted_data.get('income'),
                income_type=extracted_data.get('income_type', 'individual'),
                marriage_status=extracted_data.get('marriage_status'),
                children_count=extracted_data.get('children_count', 0),
                financial_purpose=extracted_data.get('financial_purpose'),
                gender=extracted_data.get('gender'),
                confidence_score=extracted_data.get('confidence_score', 0.95)
            )
            
            print(f"✅ OpenAI 추출 성공 (신뢰도: {profile.confidence_score:.2f})")
            return profile
            
        except Exception as e:
            print(f"⚠️ OpenAI 추출 실패: {e}")
            return UserProfile(confidence_score=0.1)

class FinancialChatbot:
    """개선된 금융상품 추천 챗봇"""
    
    def __init__(self, model_path: str = '../4.ML/multilabel_lgbm.joblib'):
        # LGBM 모델 로드
        try:
            self.multilabel_model = joblib.load(model_path)
            print("✅ LGBM 모델 로드 성공!")
        except FileNotFoundError:
            print("⚠️ .joblib 모델 파일을 찾을 수 없습니다.")
            self.multilabel_model = None
        except Exception as e:
            print(f"⚠️ 모델 로드 오류: {e}")
            self.multilabel_model = None
        
        # 추출기 초기화 (규칙 기반 우선, OpenAI 백업)
        self.rule_extractor = SimpleRuleBasedExtractor()
        
        # OpenAI API 키 로드 (선택사항)
        openai_api_key = config('OPENAI_API_KEY', default=None)
        if openai_api_key:
            self.openai_extractor = OpenAIExtractor(openai_api_key)
        else:
            print("ℹ️ OpenAI API 키가 없습니다. 규칙 기반 추출만 사용합니다.")
            self.openai_extractor = None
        
        # 타겟 변수 정의
        self.target_names = {
            'liquid_assets': '유동성자산',
            'certificate_deposit': '양도성예금증서', 
            'non_money_market_fund': '비머니마켓펀드',
            'stock_holdings': '주식보유',
            'retirement_liquidity': '퇴직준비금유동성'
        }
        
        # 라벨과 카테고리 매핑
        self.label_to_category = {
            'liquid_assets': 'bank_deposits',
            'certificate_deposit': 'bank_deposits', 
            'non_money_market_fund': 'bank_savings',
            'stock_holdings': 'credit_loans',
            'retirement_liquidity': 'bank_savings'
        }
        
        # 상품 카테고리 정보
        self.product_categories = {
            'bank_deposits': {
                'name': '예금상품',
                'file': '../1.데이터수집/data/bank_deposits.json',
                'description': '안전한 원금보장 예금상품'
            },
            'bank_savings': {
                'name': '적금상품', 
                'file': '../1.데이터수집/data/bank_savings.json',
                'description': '목돈마련을 위한 적금상품'
            },
            'credit_loans': {
                'name': '개인신용대출상품',
                'file': '../1.데이터수집/data/credit_loans.json', 
                'description': '개인 신용대출 상품'
            },
            'mortgage_loans': {
                'name': '주택담보대출',
                'file': '../1.데이터수집/data/mortgage_loans.json',
                'description': '주택구매 및 담보대출 상품'
            },
            'rent_loans': {
                'name': '전세자금대출',
                'file': '../1.데이터수집/data/rent_loans.json',
                'description': '전세보증금 마련을 위한 대출상품'
            }
        }
    
    def parse_user_input(self, user_input: str) -> Dict:
        """개선된 사용자 입력 파싱"""
        # 1차: 규칙 기반 추출
        profile = self.rule_extractor.extract_with_rules(user_input)
        
        # 2차: OpenAI 백업 (규칙 기반이 부족한 경우)
        if profile.confidence_score < 0.6 and self.openai_extractor and self.openai_extractor.available:
            print("🔄 규칙 기반 추출이 부족하여 OpenAI 백업 시도...")
            openai_profile = self.openai_extractor.extract_with_openai(user_input)
            
            if openai_profile.confidence_score > profile.confidence_score:
                print("✅ OpenAI 결과가 더 좋아서 교체합니다.")
                profile = openai_profile
            else:
                # 두 결과를 병합
                if not profile.age and openai_profile.age:
                    profile.age = openai_profile.age
                if not profile.income and openai_profile.income:
                    profile.income = openai_profile.income
                if not profile.financial_purpose and openai_profile.financial_purpose:
                    profile.financial_purpose = openai_profile.financial_purpose
                if not profile.gender and openai_profile.gender:
                    profile.gender = openai_profile.gender
                
                profile.confidence_score = max(profile.confidence_score, openai_profile.confidence_score * 0.8)
        
        # UserProfile을 Dict로 변환
        parsed_info = {}
        
        if profile.age:
            parsed_info['age'] = profile.age
            # 연령대 분류
            if profile.age < 30: parsed_info['age_group'] = 1
            elif profile.age < 40: parsed_info['age_group'] = 2
            elif profile.age < 50: parsed_info['age_group'] = 3
            elif profile.age < 60: parsed_info['age_group'] = 4
            else: parsed_info['age_group'] = 5
        
        if profile.income:
            parsed_info['salary_income'] = profile.income
            parsed_info['income_type'] = profile.income_type
            
            # 가구소득인 경우 개인소득으로 보수적 추정
            if profile.income_type == 'household':
                parsed_info['household_income'] = profile.income
                parsed_info['salary_income'] = profile.income // 2
        
        if profile.marriage_status is not None:
            parsed_info['marriage_status'] = profile.marriage_status
        
        if profile.children_count:
            parsed_info['children_count'] = profile.children_count
        
        if profile.gender is not None:
            parsed_info['gender'] = profile.gender
        
        # 금융 목적에 따른 상품 매핑
        if profile.financial_purpose:
            purpose_mapping = {
                'housing': 'mortgage_loans',
                'rent': 'rent_loans',
                'credit': 'credit_loans',
                'investment': 'bank_savings',
                'education': 'credit_loans',
                'retirement': 'bank_savings',
                'savings': 'bank_savings'
            }
            
            if profile.financial_purpose in purpose_mapping:
                parsed_info['requested_product'] = purpose_mapping[profile.financial_purpose]
                if profile.financial_purpose == 'investment':
                    parsed_info['investment_alternative'] = True
        
        parsed_info['confidence_score'] = profile.confidence_score
        
        print(f"📊 최종 추출 결과: {parsed_info}")
        return parsed_info
    
    def fill_default_values(self, parsed_info: Dict) -> np.ndarray:
        """파싱된 정보에 기본값을 채워서 모델 입력 형태로 변환"""
        defaults = {
            'age_group': 2,
            'education_level_class': 3,
            'business_income': 0,
            'capital_income': 0, 
            'age': 35,
            'risk_tolerance': 3,
            'saving_status': 1,
            'salary_income': 3000,
            'risk_aversion': 3,
            'education_level': 3,
            'gender': 1,
            'marriage_status': 1,
            'children_count': 0,
            'occupation': 3
        }
        
        # 파싱된 정보로 기본값 업데이트
        for key, value in parsed_info.items():
            if key in defaults:
                defaults[key] = value
        
        # 지능적 기본값 조정
        if defaults['age'] < 25:
            defaults['education_level_class'] = 2
            defaults['education_level'] = 2
            defaults['marriage_status'] = 0
        elif defaults['age'] > 50:
            defaults['risk_aversion'] = min(defaults['risk_aversion'] + 1, 5)
        
        if defaults['salary_income'] >= 8000:
            defaults['occupation'] = 1
            defaults['risk_tolerance'] = min(defaults['risk_tolerance'] + 1, 5)
        elif defaults['salary_income'] >= 5000:
            defaults['occupation'] = 2
        
        if defaults['children_count'] > 0:
            defaults['risk_aversion'] = min(defaults['risk_aversion'] + 1, 5)
            defaults['saving_status'] = 1
        
        if parsed_info.get('income_type') == 'household':
            defaults['risk_tolerance'] = min(defaults['risk_tolerance'] + 1, 5)
        
        # 14개 특성 배열 생성
        features = [
            defaults['age_group'],
            defaults['education_level_class'], 
            defaults['business_income'],
            defaults['capital_income'],
            defaults['age'],
            defaults['risk_tolerance'],
            defaults['saving_status'], 
            defaults['salary_income'],
            defaults['risk_aversion'],
            defaults['education_level'],
            defaults['gender'],
            defaults['marriage_status'],
            defaults['children_count'],
            defaults['occupation']
        ]
        
        return np.array(features)
    
    def load_products(self, category: str) -> Optional[List[Dict]]:
        """상품 데이터 로드"""
        if category not in self.product_categories:
            return None
            
        try:
            file_path = self.product_categories[category]['file']
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # JSON 구조에 따라 상품 추출
            if 'result' in data:
                products = data['result']['baseList']
                options = data['result']['optionList'] 
            else:
                products = data['products'][list(data['products'].keys())[0]]['result']['baseList']
                options = data['products'][list(data['products'].keys())[0]]['result']['optionList']
            
            # 상품별 최고/최저 금리 계산
            product_rates = {}
            for option in options:
                product_id = option['fin_prdt_cd']
                
                if 'loan' in category:
                    rate = option.get('lend_rate_min', option.get('lend_rate_avg', 0))
                    rate_type = '최저금리'
                else:
                    rate = option.get('intr_rate2', option.get('intr_rate', 0))
                    rate_type = '최고금리'
                
                if product_id not in product_rates or rate > product_rates[product_id]['rate']:
                    product_rates[product_id] = {'rate': rate, 'type': rate_type}
            
            # 상품 정보 매칭
            enriched_products = []
            for product in products:
                product_id = product['fin_prdt_cd']
                if product_id in product_rates:
                    enriched_products.append({
                        'id': product_id,
                        'name': product['fin_prdt_nm'],
                        'bank': product['kor_co_nm'], 
                        'rate': product_rates[product_id]['rate'],
                        'rate_type': product_rates[product_id]['type'],
                        'join_way': product.get('join_way', '영업점'),
                        'features': product.get('spcl_cnd', ''),
                        'max_limit': product.get('max_limit'),
                        'etc_note': product.get('etc_note', '')
                    })
            
            # 정렬
            reverse_sort = 'loan' not in category
            return sorted(enriched_products, key=lambda x: x['rate'], reverse=reverse_sort)
            
        except Exception as e:
            print(f"⚠️ {category} 상품 로드 오류: {e}")
            return None
    
    def recommend_products(self, user_input: str, top_n: int = 3) -> Dict:
        """개선된 상품 추천"""
        if self.multilabel_model is None:
            return {"error": "LGBM 모델이 로드되지 않았습니다."}
        
        # 1. 개선된 자연어 파싱
        parsed_info = self.parse_user_input(user_input)
        
        # 2. 모델 입력 형태로 변환
        user_features = self.fill_default_values(parsed_info)
        
        # 3. LGBM 모델 예측
        print("🤖 LGBM 모델 예측 중...")
        user_input_reshaped = user_features.reshape(1, -1)
        probabilities = self.multilabel_model.predict_proba(user_input_reshaped)
        
        # 4. 예측 결과 분석
        recommendations = []
        for i, (label, name) in enumerate(self.target_names.items()):
            prob = probabilities[i][0][1]
            recommendations.append({
                'label': label,
                'name': name,
                'probability': prob,
                'category': self.label_to_category[label]
            })
        
        recommendations.sort(key=lambda x: x['probability'], reverse=True)
        
        # 5. 결과 구성
        result = {
            'user_info': parsed_info,
            'ai_analysis': recommendations,
            'recommended_products': {}
        }
        
        # 6. 상품 매칭
        if 'requested_product' in parsed_info:
            category = parsed_info['requested_product']
            products = self.load_products(category)
            
            if products:
                result['recommended_products'][self.product_categories[category]['name']] = products[:top_n]
        else:
            threshold = 0.3 if parsed_info.get('confidence_score', 0.5) > 0.8 else 0.2
            
            for rec in recommendations[:2]:
                if rec['probability'] >= threshold:
                    category = rec['category']
                    products = self.load_products(category)
                    
                    if products:
                        result['recommended_products'][rec['name']] = products[:top_n]
        
        return result
    
    def format_recommendation_response(self, result: Dict) -> str:
        """추천 결과 포맷팅"""
        if 'error' in result:
            return f"⚠️ {result['error']}"
        
        response = []
        user_info = result['user_info']
        age = user_info.get('age', '정보없음')
        income = user_info.get('salary_income', '정보없음')
        confidence = user_info.get('confidence_score', 0.5)
        
        response.append("✨ **개선된 맞춤형 금융상품 추천 결과** ✨")
        response.append(f"👤 고객님: {age}세, 연봉 {income}만원")
        
        if confidence > 0.9:
            response.append("🎯 매우 정확한 정보 분석을 완료했습니다!")
        elif confidence > 0.7:
            response.append("✅ 높은 신뢰도로 정보를 분석했습니다.")
        elif confidence > 0.5:
            response.append("📊 양호한 신뢰도로 정보를 분석했습니다.")
        else:
            response.append("🔍 기본 분석을 완료했습니다. 더 자세한 정보를 주시면 정확한 추천이 가능합니다.")
        
        if user_info.get('investment_alternative'):
            response.append("💡 투자상품 데이터가 없어 적금상품으로 대안 제시합니다.")
        
        if user_info.get('income_type') == 'household':
            household_income = user_info.get('household_income', income * 2)
            response.append(f"💰 가구소득: {household_income}만원 (개인소득으로 환산: {income}만원)")
        
        response.append("")
        
        # AI 분석 결과
        response.append("🤖 **LGBM 적합도 분석:**")
        for rec in result['ai_analysis'][:3]:
            prob_percent = rec['probability'] * 100
            emoji = "🟢" if rec['probability'] >= 0.5 else "🟡" if rec['probability'] >= 0.3 else "🔴"
            response.append(f"{emoji} {rec['name']}: {prob_percent:.1f}%")
        response.append("")
        
        # 추천 상품
        if result['recommended_products']:
            response.append("🏆 **추천 상품:**")
            response.append("")
            
            for category_name, products in result['recommended_products'].items():
                response.append(f"**📈 {category_name}**")
                
                for i, product in enumerate(products, 1):
                    response.append(f"{i}. **{product['name']}**")
                    response.append(f"   🏦 {product['bank']}")
                    response.append(f"   💰 {product['rate_type']}: **{product['rate']:.2f}%**")
                    response.append(f"   📋 가입방법: {product['join_way']}")
                    
                    if product['features']:
                        features = product['features'][:100] + "..." if len(product['features']) > 100 else product['features']
                        response.append(f"   ⭐ 특징: {features}")
                    response.append("")
        else:
            response.append("ℹ️ 현재 조건에 맞는 추천 상품이 없습니다.")
            if confidence < 0.7:
                response.append("💡 더 자세한 정보를 알려주시면 정확한 추천이 가능합니다.")
        
        return "\n".join(response)

def main():
    """메인 실행 함수"""
    print("🚀 개선된 금융상품 추천 챗봇을 시작합니다!")
    print("=" * 60)
    
    # 챗봇 초기화
    chatbot = FinancialChatbot()
    
    # 테스트 예시
    test_inputs = [
        "50대 중반 남성, 월수익 약 300만원",
        "30대 후반 여성이고, 한달에 500만원 정도 벌어요. 전세자금대출 받고 싶습니다",
        "20대 중반 남성, 매월 250만원 받고 있어요. 적금 상품 추천해주세요"
    ]
    
    print("\n🔍 테스트 예시:")
    for i, test_input in enumerate(test_inputs, 1):
        print(f"{i}. {test_input}")
    
    print("\n" + "="*60)
    
    while True:
        print("\n💬 개선된 상담을 시작하겠습니다!")
        user_input = input("💡 어떤 금융상품을 찾고 계신가요? (종료하려면 'quit/exit/종료' 중 하나를 입력하세요): ")
        
        if user_input.lower() in ['quit', 'exit', '종료']:
            print("👋 감사합니다. 좋은 하루 되세요!")
            break
            
        try:
            # 개선된 추천 실행
            result = chatbot.recommend_products(user_input)
            
            # 결과 출력
            response = chatbot.format_recommendation_response(result)
            print("\n" + "="*60)
            print(response)
            print("="*60)
            
        except Exception as e:
            print(f"⚠️ 오류가 발생했습니다: {e}")
            print("다시 시도해주세요.")

def test_rule_based_system():
    """규칙 기반 시스템 테스트"""
    print("\n🧪 규칙 기반 시스템 테스트")
    print("=" * 50)
    
    chatbot = FinancialChatbot()
    
    test_cases = [
        {
            'input': "50대 중반 남성, 월수익 약 300만원",
            'expected': {'age': 55, 'income': 3600, 'gender': 1}
        },
        {
            'input': "30대 후반 여성이고, 한달에 500만원 정도 벌어요",
            'expected': {'age': 38, 'income': 6000, 'gender': 0}
        },
        {
            'input': "25살 미혼 남성, 연봉 4000만원, 투자 상품 찾아요",
            'expected': {'age': 25, 'income': 4000, 'gender': 1, 'marriage_status': 0, 'financial_purpose': 'investment'}
        },
        {
            'input': "기혼 여성, 35세, 자녀 2명, 주택 구입 계획",
            'expected': {'age': 35, 'gender': 0, 'marriage_status': 1, 'children_count': 2, 'financial_purpose': 'housing'}
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n테스트 {i}: {case['input']}")
        result = chatbot.parse_user_input(case['input'])
        
        print("예상 결과:", case['expected'])
        actual_result = {k: result.get(k) for k in case['expected'].keys() if k in result}
        print("실제 결과:", actual_result)
        
        # 정확도 계산
        correct = sum(1 for k, v in case['expected'].items() if result.get(k) == v)
        accuracy = correct / len(case['expected']) * 100
        confidence = result.get('confidence_score', 0.0)
        
        print(f"정확도: {accuracy:.1f}%, 신뢰도: {confidence:.2f}")
        
        if accuracy >= 80:
            print("✅ 테스트 통과")
        else:
            print("⚠️ 개선 필요")

def test_full_recommendation():
    """전체 추천 시스템 테스트"""
    print("\n🎯 전체 추천 시스템 테스트")
    print("=" * 50)
    
    chatbot = FinancialChatbot()
    
    test_queries = [
        "30대 직장인 남성, 월급 400만원, 결혼 준비 중이라 적금하고 싶어요",
        "40대 기혼 여성, 부부 합산 연봉 8000만원, 아이 둘, 주택구입 고려중",
        "50대 중반 남성, 은퇴 준비하려고 합니다"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n=== 테스트 {i} ===")
        print(f"질의: {query}")
        
        try:
            result = chatbot.recommend_products(query)
            response = chatbot.format_recommendation_response(result)
            print("\n결과:")
            print(response)
            print("\n" + "-"*50)
            
        except Exception as e:
            print(f"❌ 오류: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            test_rule_based_system()
        elif sys.argv[1] == 'full':
            test_full_recommendation()
        else:
            main()
    else:
        main()