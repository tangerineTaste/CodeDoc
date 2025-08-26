# category_recommendations.py
# 카테고리별 AI 추천 기능을 위한 추가 함수들

def get_category_recommendations_for_user(user):
    """
    사용자 맞춤 카테고리별 AI 추천 상품 생성
    각 카테고리(예금, 적금, 펀드, 주식, MMF)별로 3개씩 추천
    """
    category_recs = {}
    
    try:
        profile = user.profile
        
        # 기본 사용자 정보 구성
        base_user_info = []
        
        # 연령대 정보
        age_map = {
            1: '23세', 2: '30세', 3: '40세', 
            4: '50세', 5: '60세', 6: '70세'
        }
        if profile.연령대분류:
            base_user_info.append(age_map.get(profile.연령대분류, '30세'))
        
        # 성별 정보
        if profile.가구주성별 == 1:
            base_user_info.append('남성')
        elif profile.가구주성별 == 2:
            base_user_info.append('여성')
        
        # 결혼 상태
        if profile.결혼상태 == 1:
            base_user_info.append('기혼')
        elif profile.결혼상태 == 2:
            base_user_info.append('미혼')
        
        # 소득 추정
        income_map = {
            1: '월급 350만원', 2: '월급 600만원',
            3: '연금 수급자', 4: '월급 200만원'
        }
        if profile.직업분류1:
            base_user_info.append(income_map.get(profile.직업분류1, '월급 300만원'))
        
        base_info_str = ' '.join(base_user_info)
        
        # AI 추천 시스템 임포트
        from .matching import HighPerformanceFinancialRecommender
        recommender = HighPerformanceFinancialRecommender()
        
        # 각 카테고리별 추천 생성
        categories = {
            'deposit': '안전한 예금상품',
            'saving': '꾸준한 적금상품', 
            'fund': '펀드 투자',
            'stock': '주식 투자',
            'mmf': 'MMF 단기투자'
        }
        
        for category_key, category_desc in categories.items():
            try:
                # 카테고리별 맞춤 입력 생성
                category_input = f"{base_info_str} {category_desc} 추천해주세요"
                print(f"카테고리 {category_key} AI 추천 입력: {category_input}")
                
                # AI 추천 실행
                result = recommender.recommend(category_input, top_n=3)
                
                # 결과 변환 - 카테고리 필터링 없이 모든 추천 상품 사용
                category_products = []
                for product in result.get('products', []):
                    from .views import get_product_type_from_ai_result, get_product_type_name_from_ai_result
                    product_type = get_product_type_from_ai_result(product)
                    
                    converted_product = {
                        'fin_prdt_nm': product['name'],
                        'kor_co_nm': product['bank'],
                        'join_way': product.get('join_way', '온라인 가입 가능'),
                        'product_type': product_type,
                        'product_type_name': get_product_type_name_from_ai_result(product),
                        'rate': product.get('rate', 0),
                        'score': product.get('score', 0)
                    }
                    category_products.append(converted_product)
                
                # 추천 상품이 3개 미만인 경우 기본 상품으로 채우기
                if len(category_products) < 3:
                    category_products.extend(get_default_products_by_category(category_key, 3 - len(category_products)))
                    print(f"카테고리 {category_key}: AI 추천 {len(result.get('products', []))}개 + 기본 상품 {3 - len(category_products)}개 보충")
                
                category_recs[f'recommended_{category_key}'] = category_products[:3]
                print(f"카테고리 {category_key} 추천 완료: {len(category_products[:3])}개 상품")
                
            except Exception as e:
                print(f"카테고리 {category_key} 추천 오류: {e}")
                # 오류 발생 시 기본 상품 제공
                category_recs[f'recommended_{category_key}'] = get_default_products_by_category(category_key, 3)
        
        print(f"전체 카테고리별 추천 완료: {len(category_recs)}개 카테고리")
        return category_recs
        
    except Exception as e:
        print(f"카테고리별 추천 전체 오류: {e}")
        import traceback
        traceback.print_exc()
        return {}


def get_default_products_by_category(category, count=3):
    """
    카테고리별 기본 상품 데이터 제공
    AI 추천이 실패하거나 부족할 때 사용
    """
    default_products = {
        'deposit': [
            {
                'fin_prdt_nm': 'AI 추천 정기예금',
                'kor_co_nm': '시중은행',
                'join_way': '온라인 가입 가능',
                'product_type': 'deposit',
                'product_type_name': '예금',
                'rate': 3.5,
                'score': 85
            },
            {
                'fin_prdt_nm': 'AI 추천 자유예금',
                'kor_co_nm': '시중은행',
                'join_way': '온라인 가입 가능',
                'product_type': 'deposit',
                'product_type_name': '예금',
                'rate': 2.8,
                'score': 80
            },
            {
                'fin_prdt_nm': 'AI 추천 특판예금',
                'kor_co_nm': '시중은행',
                'join_way': '온라인 가입 가능',
                'product_type': 'deposit',
                'product_type_name': '예금',
                'rate': 4.2,
                'score': 90
            }
        ],
        'saving': [
            {
                'fin_prdt_nm': 'AI 추천 정기적금',
                'kor_co_nm': '시중은행',
                'join_way': '온라인 가입 가능',
                'product_type': 'saving',
                'product_type_name': '적금',
                'rate': 3.8,
                'score': 85
            },
            {
                'fin_prdt_nm': 'AI 추천 자유적금',
                'kor_co_nm': '시중은행',
                'join_way': '온라인 가입 가능',
                'product_type': 'saving',
                'product_type_name': '적금',
                'rate': 3.5,
                'score': 82
            },
            {
                'fin_prdt_nm': 'AI 추천 청년적금',
                'kor_co_nm': '시중은행',
                'join_way': '온라인 가입 가능',
                'product_type': 'saving',
                'product_type_name': '적금',
                'rate': 4.5,
                'score': 88
            }
        ],
        'fund': [
            {
                'fin_prdt_nm': '삼성자산운용 안정형펀드',
                'kor_co_nm': '삼성자산운용',
                'join_way': '온라인 가입 가능',
                'product_type': 'fund',
                'product_type_name': '펀드',
                'rate': 5.2,
                'score': 78
            },
            {
                'fin_prdt_nm': '미래자산 성장형펀드',
                'kor_co_nm': '미래자산운용',
                'join_way': '온라인 가입 가능',
                'product_type': 'fund',
                'product_type_name': '펀드',
                'rate': 8.1,
                'score': 75
            },
            {
                'fin_prdt_nm': '한투자증권 혼합형펀드',
                'kor_co_nm': '한투자증권',
                'join_way': '온라인 가입 가능',
                'product_type': 'fund',
                'product_type_name': '펀드',
                'rate': 6.8,
                'score': 72
            }
        ],
        'stock': [
            {
                'fin_prdt_nm': '삼성전자',
                'kor_co_nm': '삼성전자',
                'join_way': '온라인 거래 가능',
                'product_type': 'stock',
                'product_type_name': '주식',
                'rate': 12.5,
                'score': 68
            },
            {
                'fin_prdt_nm': 'SK하이닉스',
                'kor_co_nm': 'SK하이닉스',
                'join_way': '온라인 거래 가능',
                'product_type': 'stock',
                'product_type_name': '주식',
                'rate': 15.2,
                'score': 65
            },
            {
                'fin_prdt_nm': 'LG화학',
                'kor_co_nm': 'LG화학',
                'join_way': '온라인 거래 가능',
                'product_type': 'stock',
                'product_type_name': '주식',
                'rate': 8.7,
                'score': 70
            }
        ],
        'mmf': [
            {
                'fin_prdt_nm': '대신 단기자금MMF',
                'kor_co_nm': '대신자산운용',
                'join_way': '온라인 가입 가능',
                'product_type': 'mmf',
                'product_type_name': '머니마켓펀드',
                'rate': 3.2,
                'score': 85
            },
            {
                'fin_prdt_nm': '삼성 고수익MMF',
                'kor_co_nm': '삼성자산운용',
                'join_way': '온라인 가입 가능',
                'product_type': 'mmf',
                'product_type_name': '머니마켓펀드',
                'rate': 3.8,
                'score': 88
            },
            {
                'fin_prdt_nm': '미래자산 안정형MMF',
                'kor_co_nm': '미래자산운용',
                'join_way': '온라인 가입 가능',
                'product_type': 'mmf',
                'product_type_name': '머니마켓펀드',
                'rate': 2.9,
                'score': 90
            }
        ]
    }
    
    return default_products.get(category, [])[:count]
