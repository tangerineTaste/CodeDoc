import os
import requests
from dotenv import load_dotenv
import json
from datetime import datetime

class FinancialProductAPI:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('FSS_API_KEY')
        self.base_url = 'https://finlife.fss.or.kr/finlifeapi'
        
        if not self.api_key:
            raise ValueError("FSS_API_KEY가 .env 파일에 설정되지 않았습니다.")
        
    def get_deposit_products(self, top_fin_grp_no='020000', page_no=1):
        '''정기예금 상품 조회'''
        try:
            url = f"{self.base_url}/depositProductsSearch.json"
            params = {
                'auth': self.api_key,
                'topFinGrpNo': top_fin_grp_no,
                'pageNo': page_no
            }

            response = requests.get(url, params = params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
                    print(f"정기예금 상품 조회 오류: {e}")
                    raise
        
    def get_saving_products(self, top_fin_grp_no='020000', page_no=1):
        '''적금 상품 조회'''
        try:
            url = f"{self.base_url}/savingProductsSearch.json"
            params = {
                'auth': self.api_key,
                'topFinGrpNo': top_fin_grp_no,
                'pageNo': page_no
            }

            response = requests.get(url, params = params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
                    print(f"적금 상품 조회 오류: {e}")
                    raise
        
    def get_fund_products(self, top_fin_grp_no='020000', page_no=1):
        '''펀드 상품 조회'''
        try:
            # 펀드 데이터는 로컬 JSON 파일에서 읽어옴
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            funds_file = os.path.join(current_dir, 'data', 'funds.json')
            
            with open(funds_file, 'r', encoding='utf-8') as f:
                import json
                return json.load(f)

        except Exception as e:
                    print(f"펀드 상품 조회 오류: {e}")
                    raise
        
    def get_stock_products(self, top_fin_grp_no='020000', page_no=1):
        '''주식 상품 조회'''
        try:
            # 주식 데이터는 로컬 JSON 파일에서 읽어옴
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            stocks_file = os.path.join(current_dir, 'data', 'stocks.json')
            
            with open(stocks_file, 'r', encoding='utf-8') as f:
                import json
                return json.load(f)

        except Exception as e:
                    print(f"주식 상품 조회 오류: {e}")
                    raise
        
    def get_money_market_fund_products(self, top_fin_grp_no='020000', page_no=1):
        '''머니마켓펀드 상품 조회'''
        try:
            # 머니마켓펀드 데이터는 로컬 JSON 파일에서 읽어옴
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            mmf_file = os.path.join(current_dir, 'data', 'money_market_funds.json')
            
            with open(mmf_file, 'r', encoding='utf-8') as f:
                import json
                return json.load(f)

        except Exception as e:
                    print(f"머니마켓펀드 상품 조회 오류: {e}")
                    raise
        
    def get_company_list(self, top_fin_grp_no='020000', page_no=1):
        '''금융회사 목록 조회'''
        try:
            url = f"{self.base_url}/companySearch.json"
            params = {
                'auth': self.api_key,
                'topFinGrpNo': top_fin_grp_no,
                'pageNo': page_no
            }

            response = requests.get(url, params = params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
                    print(f"전세자금대출 상품 조회 오류: {e}")
                    raise
        
    def print_product_summary(self, products, product_type="상품"):
        """상품 정보 요약 출력"""
        if 'result' in products and 'baseList' in products['result']:
            base_list = products['result']['baseList']
            print(f"총 {len(base_list)}개 {product_type} 발견")
            
            for i, product in enumerate(base_list[:5]):  # 처음 5개만 출력
                print(f"\n{i+1}. {product.get('fin_prdt_nm', 'N/A')}")
                print(f"   금융회사: {product.get('kor_co_nm', 'N/A')}")
                print(f"   가입방법: {product.get('join_way', 'N/A')}")
                if 'etc_note' in product:
                    print(f"   기타사항: {product['etc_note'][:50]}...")

    def save_to_json(self, data, filename):
        """개별 데이터를 JSON 파일로 저장 (기존 파일 덮어쓰기)"""
        try:
            os.makedirs("data", exist_ok=True)  # data 폴더 생성
            full_filename = f"data/{filename}.json"
            
            # 기존 파일이 있는지 확인
            if os.path.exists(full_filename):
                print(f"기존 {full_filename} 파일을 업데이트합니다...")
            else:
                print(f"새로운 {full_filename} 파일을 생성합니다...")
            
            with open(full_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"{filename} 데이터가 {full_filename}에 저장되었습니다!")
            return full_filename
            
        except Exception as e:
            print(f"JSON 저장 오류: {e}")
            return None
        
    def save_all_data_to_json(self, filename="financial_data"):
        """모든 금융상품 데이터를 하나의 JSON 파일로 저장 (기존 파일 업데이트)"""
        os.makedirs("data", exist_ok=True)  # data 폴더 생성
        full_filename = f"data/{filename}.json"
        
        # 기존 데이터 로드 (있다면)
        existing_data = {}
        if os.path.exists(full_filename):
            try:
                with open(full_filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                print(f"🔄 기존 {full_filename} 파일을 업데이트합니다...")
                
                # 이전 수집 시간 표시
                if 'last_updated' in existing_data:
                    print(f"  이전 업데이트: {existing_data['last_updated']}")
            except:
                print(f"기존 파일 로드 실패, 새로 생성합니다...")
        else:
            print(f"새로운 {full_filename} 파일을 생성합니다...")
        
        # 새로운 데이터 구조
        all_data = {
            'last_updated': datetime.now().isoformat(),
            'data_source': '금융감독원 금융상품 통합 비교공시',
            'update_history': existing_data.get('update_history', []),
            'products': {}
        }
        
        # 업데이트 히스토리에 추가
        all_data['update_history'].append({
            'update_time': datetime.now().isoformat(),
            'status': 'success'
        })
        
        # 히스토리는 최대 10개만 유지
        if len(all_data['update_history']) > 10:
            all_data['update_history'] = all_data['update_history'][-10:]
        
        try:
            print("📥 데이터 수집 중...")
            
            # 각 상품별 데이터 수집
            print("  - 은행 예금 상품...")
            all_data['products']['bank_deposits'] = self.get_deposit_products('020000')
            
            print("  - 은행 적금 상품...")
            all_data['products']['bank_savings'] = self.get_saving_products('020000')
            
            print("  - 펀드...")
            all_data['products']['funds'] = self.get_fund_products('020000')
            
            print("  - 주식...")
            all_data['products']['stocks'] = self.get_stock_products('020000')
            
            print("  - 머니마켓펀드...")
            all_data['products']['money_market_funds'] = self.get_money_market_fund_products('020000')
            
            print("  - 금융회사 목록...")
            all_data['products']['companies'] = self.get_company_list('020000')
            
            print("  - 저축은행 예금...")
            all_data['products']['savings_bank_deposits'] = self.get_deposit_products('030300')
            
            # JSON 파일로 저장 (덮어쓰기)
            with open(full_filename, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            # 수집 결과 요약
            print(f"\n모든 데이터가 {full_filename}에 업데이트되었습니다!")
            print(f"파일 크기: {os.path.getsize(full_filename) / 1024:.1f} KB")
            print(f"업데이트 시간: {all_data['last_updated']}")
            
            # 데이터 요약 출력
            print(f"\n수집된 데이터 요약:")
            for key, value in all_data['products'].items():
                if 'result' in value and 'baseList' in value['result']:
                    count = len(value['result']['baseList'])
                    product_name = key.replace('_', ' ').title()
                    print(f"  - {product_name}: {count}개")
            
            # 업데이트 히스토리 표시
            print(f"\n업데이트 히스토리 ({len(all_data['update_history'])}회):")
            for i, history in enumerate(all_data['update_history'][-3:], 1):  # 최근 3개만
                update_time = datetime.fromisoformat(history['update_time']).strftime("%m-%d %H:%M")
                print(f"  {i}. {update_time} - {history['status']}")
                    
            return full_filename
            
        except Exception as e:
            print(f"데이터 수집/저장 오류: {e}")
            
            # 오류 시 히스토리에 기록
            if 'all_data' in locals():
                all_data['update_history'][-1]['status'] = f'failed: {str(e)}'
                try:
                    with open(full_filename, 'w', encoding='utf-8') as f:
                        json.dump(all_data, f, ensure_ascii=False, indent=2)
                except:
                    pass
            
            return None
        
    def load_from_json(self, filename):
        """JSON 파일에서 데이터 로드"""
        try:
            with open(f"data/{filename}", 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"{filename}에서 데이터를 로드했습니다!")
            return data
        except Exception as e:
            print(f"JSON 로드 오류: {e}")
            return None

def main():
    """메인 실행 함수"""
    try:
        api = FinancialProductAPI()
        
        print("=== 금융감독원 API 테스트 ===\n")
        
        # 은행 예금 상품 조회
        print("은행 예금 상품 조회")
        deposits = api.get_deposit_products('020000')
        api.print_product_summary(deposits, "예금 상품")
        
        print("\n" + "="*50)
        
        # 은행 적금 상품 조회  
        print("은행 적금 상품 조회")
        savings = api.get_saving_products('020000')
        api.print_product_summary(savings, "적금 상품")

        print("\n" + "="*50)

        # 펀드 상품 조회  
        print("펀드 상품 조회")
        funds = api.get_fund_products('020000')
        api.print_product_summary(funds, "펀드 상품")
        
        print("\n" + "="*50)

        # 주식 상품 조회  
        print("주식 상품 조회")
        stocks = api.get_stock_products('020000')
        api.print_product_summary(stocks, "주식 상품")

        print("\n" + "="*50)

        # 머니마켓펀드 상품 조회  
        print("머니마켓펀드 상품 조회")
        money_market_funds = api.get_money_market_fund_products('020000')
        api.print_product_summary(money_market_funds, "머니마켓펀드 상품")

        print("\n" + "="*50)
        
        # 금융회사 목록 조회
        print("금융회사 목록 조회")
        companies = api.get_company_list('020000')
        
        if 'result' in companies and 'baseList' in companies['result']:
            company_list = companies['result']['baseList']
            print(f"총 {len(company_list)}개 금융회사")
            
            for i, company in enumerate(company_list[:10]):  # 처음 10개만
                print(f"{i+1:2d}. {company.get('kor_co_nm', 'N/A')} "
                    f"(코드: {company.get('fin_co_no', 'N/A')})")
        
        # JSON 저장 여부 선택
        print("\n" + "="*60)
        save_choice = input("""
            📁 데이터를 JSON 파일로 저장하시겠습니까?
            1. 네, 모든 데이터를 financial_data.json에 저장
            2. 네, 상품별로 개별 파일에 저장
            3. 아니요, 콘솔 출력만으로 충분합니다
            선택 (1-3): """)
        
        if save_choice == '1':
            print(f"\n JSON 파일 저장 중...")
            # 이미 조회한 데이터들을 모아서 저장
            all_data = {
                'last_updated': datetime.now().isoformat(),
                'data_source': '금융감독원 금융상품 통합 비교공시',
                'products': {
                    'bank_deposits': deposits,
                    'bank_savings': savings,
                    'funds': funds,
                    'stocks': stocks,
                    'money_market_funds': money_market_funds,
                    'companies': companies,
                }
            }
            
            # 기존 히스토리 보존
            os.makedirs("data", exist_ok=True)  # data 폴더 생성
            filename = "data/financial_data.json"
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    all_data['update_history'] = existing_data.get('update_history', [])
                except:
                    all_data['update_history'] = []
            else:
                all_data['update_history'] = []
            
            # 히스토리 업데이트
            all_data['update_history'].append({
                'update_time': datetime.now().isoformat(),
                'status': 'success'
            })
            
            # 히스토리는 최대 10개만 유지
            if len(all_data['update_history']) > 10:
                all_data['update_history'] = all_data['update_history'][-10:]
            
            # JSON 파일 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 모든 데이터가 {filename}에 저장되었습니다!")
            print(f"📄 파일 크기: {os.path.getsize(filename) / 1024:.1f} KB")
            
        elif save_choice == '2':
            print(f"\n📥 개별 JSON 파일 저장 중...")
            
            # 각 상품별로 개별 파일 저장
            api.save_to_json(deposits, "bank_deposits")
            api.save_to_json(savings, "bank_savings")
            api.save_to_json(funds, "funds")
            api.save_to_json(stocks, "stocks")
            api.save_to_json(money_market_funds, "money_market_funds")
            api.save_to_json(companies, "companies")
            
            print("✅ 모든 개별 파일이 저장되었습니다!")
            
        else:
            print("\n✨ 콘솔 출력 완료! JSON 저장은 생략합니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()