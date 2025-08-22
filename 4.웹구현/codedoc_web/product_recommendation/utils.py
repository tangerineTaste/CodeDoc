# product_recommendation/utils.py
import json
import os
from django.conf import settings

class ProductDataLoader:
    """
    파일 기반 상품 데이터 로더
    funds.json, stocks.json, money_market_funds.json 파일에서 데이터를 읽어옴
    """
    
    @staticmethod
    def load_json_file(filename):
        """JSON 파일을 로드하는 헬퍼 함수"""
        try:
            file_path = os.path.join(settings.BASE_DIR, 'data', filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"파일을 찾을 수 없습니다: {filename}")
            return None
        except json.JSONDecodeError:
            print(f"JSON 파싱 오류: {filename}")
            return None

    @staticmethod
    def process_fund_data(fund_data):
        """펀드 데이터를 템플릿에서 사용할 형태로 변환"""
        if not fund_data or 'result' not in fund_data:
            return []
        
        base_list = fund_data['result'].get('baseList', [])
        option_list = fund_data['result'].get('optionList', [])
        
        # optionList를 딕셔너리로 변환 (빠른 검색을 위해)
        options_dict = {item['fin_prdt_cd']: item for item in option_list}
        
        processed_products = []
        for product in base_list:
            # 기본 정보
            processed_product = {
                'fin_prdt_cd': product.get('fin_prdt_cd'),
                'fin_prdt_nm': product.get('fin_prdt_nm'),
                'kor_co_nm': product.get('kor_co_nm'),
                'join_way': product.get('join_way'),
                'fund_type': product.get('fund_type'),
                'risk_level': product.get('risk_level'),
                'fee_info': product.get('fee_info'),
                'min_invest': product.get('min_invest'),
                'product_type': 'fund',
                'product_type_name': '펀드',
                # 기본 템플릿 호환성을 위한 필드
                'current_price': None,
                'change_rate': None,
            }
            
            # 옵션 정보 추가 (수익률 등)
            option_info = options_dict.get(product.get('fin_prdt_cd'))
            if option_info:
                processed_product.update({
                    'return_rate': option_info.get('return_rate', 0),
                    'nav': option_info.get('nav'),
                    'total_assets': option_info.get('total_assets'),
                })
            else:
                processed_product.update({
                    'return_rate': 0,
                    'nav': None,
                    'total_assets': None,
                })
            
            processed_products.append(processed_product)
        
        return processed_products

    @staticmethod
    def process_stock_data(stock_data):
        """주식 데이터를 템플릿에서 사용할 형태로 변환"""
        if not stock_data or 'result' not in stock_data:
            return []
        
        base_list = stock_data['result'].get('baseList', [])
        option_list = stock_data['result'].get('optionList', [])
        
        # optionList를 딕셔너리로 변환
        options_dict = {item['stock_code']: item for item in option_list}
        
        processed_products = []
        for product in base_list:
            # 기본 정보
            processed_product = {
                'stock_code': product.get('stock_code'),
                'stock_nm': product.get('stock_nm'),
                'fin_prdt_nm': product.get('stock_nm'),  # 템플릿 호환성
                'kor_co_nm': product.get('stock_nm'),    # 템플릿 호환성
                'market_div': product.get('market_div'),
                'sector': product.get('sector'),
                'current_price': product.get('current_price'),
                'prev_close': product.get('prev_close'),
                'change_rate': product.get('change_rate'),
                'volume': product.get('volume'),
                'market_cap': product.get('market_cap'),
                'product_type': 'stock',
                'product_type_name': '주식',
                # 기본 템플릿 호환성을 위한 필드
                'join_way': None,
                'return_rate': product.get('change_rate', 0),  # 등락률을 수익률로
            }
            
            # 옵션 정보 추가 (기술적 분석 등)
            option_info = options_dict.get(product.get('stock_code'))
            if option_info:
                processed_product.update({
                    'rsi': option_info.get('rsi'),
                    'macd_signal': option_info.get('macd_signal'),
                    'bollinger_position': option_info.get('bollinger_position'),
                    'target_price': option_info.get('target_price'),
                })
            
            processed_products.append(processed_product)
        
        return processed_products

    @staticmethod
    def process_mmf_data(mmf_data):
        """머니마켓펀드 데이터를 템플릿에서 사용할 형태로 변환"""
        if not mmf_data or 'result' not in mmf_data:
            return []
        
        base_list = mmf_data['result'].get('baseList', [])
        option_list = mmf_data['result'].get('optionList', [])
        
        # optionList를 딕셔너리로 변환
        options_dict = {item['fin_prdt_cd']: item for item in option_list}
        
        processed_products = []
        for product in base_list:
            # 기본 정보
            processed_product = {
                'fin_prdt_cd': product.get('fin_prdt_cd'),
                'fin_prdt_nm': product.get('fin_prdt_nm'),
                'kor_co_nm': product.get('kor_co_nm'),
                'join_way': product.get('join_way'),
                'fund_type': product.get('fund_type'),
                'risk_level': product.get('risk_level'),
                'fee_info': product.get('fee_info'),
                'min_invest': product.get('min_invest'),
                'liquidity': product.get('liquidity'),
                'product_type': 'mmf',
                'product_type_name': '머니마켓펀드',
                # 기본 템플릿 호환성을 위한 필드
                'current_price': None,
                'change_rate': None,
            }
            
            # 옵션 정보 추가 (수익률 등)
            option_info = options_dict.get(product.get('fin_prdt_cd'))
            if option_info:
                processed_product.update({
                    'return_rate': option_info.get('return_rate', 0),
                    'nav': option_info.get('nav'),
                    'total_assets': option_info.get('total_assets'),
                    'yield_today': option_info.get('yield_today'),
                })
            else:
                processed_product.update({
                    'return_rate': 0,
                    'nav': None,
                    'total_assets': None,
                    'yield_today': None,
                })
            
            processed_products.append(processed_product)
        
        return processed_products

    @classmethod
    def get_all_file_based_products(cls):
        """모든 파일 기반 상품 데이터를 로드하고 통합"""
        all_products = []
        
        # 펀드 데이터 로드
        fund_data = cls.load_json_file('funds.json')
        if fund_data:
            funds = cls.process_fund_data(fund_data)
            all_products.extend(funds)
        
        # 주식 데이터 로드
        stock_data = cls.load_json_file('stocks.json')
        if stock_data:
            stocks = cls.process_stock_data(stock_data)
            all_products.extend(stocks)
        
        # 머니마켓펀드 데이터 로드
        mmf_data = cls.load_json_file('money_market_funds.json')
        if mmf_data:
            mmf_products = cls.process_mmf_data(mmf_data)
            all_products.extend(mmf_products)
        
        return all_products

    @classmethod
    def get_funds(cls):
        """펀드 데이터만 반환"""
        fund_data = cls.load_json_file('funds.json')
        return cls.process_fund_data(fund_data) if fund_data else []

    @classmethod
    def get_stocks(cls):
        """주식 데이터만 반환"""
        stock_data = cls.load_json_file('stocks.json')
        return cls.process_stock_data(stock_data) if stock_data else []

    @classmethod
    def get_mmf_products(cls):
        """머니마켓펀드 데이터만 반환"""
        mmf_data = cls.load_json_file('money_market_funds.json')
        return cls.process_mmf_data(mmf_data) if mmf_data else []


# 페이지네이션을 위한 헬퍼 클래스
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class ProductPaginator:
    """상품 리스트 페이지네이션 헬퍼"""
    
    @staticmethod
    def paginate_products(products, page_number, per_page=9):
        """상품 리스트를 페이지네이션"""
        if not products:
            return None, 0
        
        paginator = Paginator(products, per_page)
        
        try:
            paginated_products = paginator.page(page_number)
        except PageNotAnInteger:
            # 페이지 번호가 정수가 아닌 경우 첫 번째 페이지 반환
            paginated_products = paginator.page(1)
        except EmptyPage:
            # 페이지가 범위를 벗어난 경우 마지막 페이지 반환
            paginated_products = paginator.page(paginator.num_pages)
        
        return paginated_products, len(products)