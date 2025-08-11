import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

def load_and_clean_scf_data(file_path):
    """SCF 데이터 로드 및 기본 정제"""
    
    print("📥 데이터 로드 중...")
    df = pd.read_csv(file_path)
    print(f"원본 데이터 크기: {df.shape}")
    
    # 첫 번째 컬럼(인덱스) 제거
    if df.columns[0] == 'Unnamed: 0' or df.columns[0] == '':
        df = df.drop(df.columns[0], axis=1)
    
    print(f"정제 후 데이터 크기: {df.shape}")
    print(f"컬럼 목록: {list(df.columns)}")
    
    return df

def check_data_quality(df): #결측값 없음 확인
    """데이터 품질 확인"""
    
    print("\n🔍 데이터 품질 확인...")
    
    # 결측값 확인
    missing_count = df.isnull().sum().sum()
    print(f"총 결측값: {missing_count}개")
    
    if missing_count == 0:
        print("✅ 결측값 없음 - 데이터 품질 양호!")
    
    # 기본 통계 확인
    print(f"\n📊 기본 정보:")
    print(f"  - 총 샘플 수: {len(df):,}개")
    print(f"  - 총 변수 수: {len(df.columns)}개")
    print(f"  - 메모리 사용량: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    
    return df

def remove_outliers(df): #극단적인 값 제거
    """이상값 제거"""
    
    print("\n🚨 이상값 제거 중...")
    original_len = len(df)
    
    # 나이 이상값 (18-100세 범위)
    df = df[(df['연령'] >= 18) & (df['연령'] <= 100)]
    
    # 소득 이상값 (상위 1%, 하위 1% 제거)
    income_q1 = df['총소득'].quantile(0.01)
    income_q99 = df['총소득'].quantile(0.99)
    df = df[(df['총소득'] >= income_q1) & (df['총소득'] <= income_q99)]
    
    # 자산 이상값 (음수 제거, 상위 1% 제거)
    asset_q99 = df['총자산'].quantile(0.99)
    df = df[(df['총자산'] >= 0) & (df['총자산'] <= asset_q99)]
    
    # 순자산 극단값 제거
    networth_q1 = df['순자산'].quantile(0.01)
    networth_q99 = df['순자산'].quantile(0.99)
    df = df[(df['순자산'] >= networth_q1) & (df['순자산'] <= networth_q99)]
    
    removed_count = original_len - len(df)
    print(f"✅ 이상값 {removed_count}개 제거 완료 ({removed_count/original_len*100:.1f}%)")
    print(f"정제 후 데이터 크기: {df.shape}")
    
    return df

def create_derived_features(df):
    """독립변수 설계 문서 기반으로 파생 변수 생성"""
    
    print("\n🔧 독립변수 설계 문서 기반 파생 변수 생성 중...")
    
    # === 1. 사용자 기본 프로필 ===
    
    # 나이 (연속형) - 이미 존재
    
    # 소득수준 (구간화: 하/중/상)
    df['소득수준'] = pd.cut(df['총소득'], 
                        bins=[-np.inf, 50000, 100000, np.inf],
                        labels=['하', '중', '상'])
    
    # 직업 (화이트칼라/블루칼라/자영업/기타)
    def map_occupation(job_code):
        if job_code in [1, 2, 3]:  # 관리/전문직 등
            return '화이트칼라'
        elif job_code in [4, 5, 6]:  # 생산/기능직 등
            return '블루칼라'
        elif job_code in [7, 8]:  # 자영업 등
            return '자영업'
        else:
            return '기타'
    
    df['직업분류'] = df['직업분류1'].apply(map_occupation)
    
    # 가족상태 (미혼/기혼/자녀유무)
    def get_family_status(row):
        if row['결혼상태'] != 1:  # 미혼
            return '미혼'
        elif row['자녀수'] > 0:   # 기혼+자녀
            return '기혼_자녀있음'
        else:                    # 기혼+자녀없음
            return '기혼_자녀없음'
    
    df['가족상태분류'] = df.apply(get_family_status, axis=1)
    
    # 자산규모 (구간화: 1천만원 이하/1천~5천/5천만원 이상)
    df['자산규모분류'] = pd.cut(df['총자산'] / 10000,  # 만원 단위
                        bins=[-np.inf, 1000, 5000, np.inf],
                        labels=['1천만원이하', '1천~5천만원', '5천만원이상'])
    
    # 월저축률 (소득 대비 %)
    df['월저축률'] = np.where(df['총소득'] > 0, 
                          (df['저축함'] / df['총소득']) * 100, 0)
    
    # 현재 보유상품 (예적금/펀드/주식/보험 여부)
    df['예적금보유'] = ((df['저축여부'] == 1) | 
                    (df['당좌예금보유여부'] == 1)).astype(int)
    df['펀드보유'] = df['비머니마켓펀드보유여부']
    df['주식보유'] = df['주식보유여부'] 
    df['보험보유'] = df['현금가치생명보험보유여부']
    
    # === 2. 투자 성향 ===
    
    # 위험성향 (보수적/중간/적극적)
    def determine_risk_tolerance(row):
        # 위험 감수 성향 점수 계산
        risk_score = (row['금융위험감수'] - row['금융위험회피'] + 
                     row['주식보유여부'] * 2 + 
                     (row['거래횟수'] > 10) * 1 +
                     row['비머니마켓펀드보유여부'] * 1)
        
        if risk_score >= 2:
            return '적극적'
        elif risk_score >= -1:
            return '중간'
        else:
            return '보수적'
    
    df['위험성향분류'] = df.apply(determine_risk_tolerance, axis=1)
    
    # 투자경험 (초보/중급/고급)
    # 보유상품 다양성 + 거래 경험으로 판단
    experience_score = (df['주식보유여부'] + 
                        df['비머니마켓펀드보유여부'] + 
                        df['IRA계좌보유여부'] + 
                        (df['거래횟수'] > 5).astype(int) +
                        (df['주식보유수'] > 3).astype(int))
    
    df['투자경험분류'] = pd.cut(experience_score, 
                            bins=[-1, 0, 2, 10],
                            labels=['초보', '중급', '고급'])
    
    # 투자목적 (단기수익/장기자산/노후준비/비상자금)
    # 나이와 가족상태로 추정
    def determine_investment_purpose(row):
        age = row['연령']
        has_kids = row['자녀수'] > 0
        married = row['결혼상태'] == 1
        
        if age >= 55:
            return '노후준비'
        elif has_kids and married:
            return '장기자산'
        elif age < 35 and not married:
            return '단기수익'
        else:
            return '비상자금'
    
    df['투자목적분류'] = df.apply(determine_investment_purpose, axis=1)
    
    # 투자기간 (1년 이하/1-3년/3-5년/5년 이상)
    # 나이로 추정 (젊을수록 장기 투자 가능)
    def determine_investment_period(age):
        if age < 30:
            return '3-5년'
        elif age < 40:
            return '5년이상'
        elif age < 55:
            return '1-3년'
        else:
            return '1년이하'
    
    df['투자기간분류'] = df['연령'].apply(determine_investment_period)
    
    # === 3. 행동 데이터 (시뮬레이션) ===
    
    # 질문 카테고리 (예적금/투자/보험/세금/정보탐색)
    # 보유 상품으로 관심 분야 추정
    def determine_question_category(row):
        if row['주식보유여부'] == 1 or row['비머니마켓펀드보유여부'] == 1:
            return '투자'
        elif row['현금가치생명보험보유여부'] == 1:
            return '보험'
        elif row['저축여부'] == 1:
            return '예적금'
        else:
            return '정보탐색'
    
    df['질문카테고리'] = df.apply(determine_question_category, axis=1)
    
    # 질문 복잡도 (기초/중급/고급)
    # 투자경험과 연동
    complexity_mapping = {'초보': '기초', '중급': '중급', '고급': '고급'}
    df['질문복잡도'] = df['투자경험분류'].map(complexity_mapping)
    
    print("✅ 독립변수 설계 문서 기반 파생 변수 생성 완료:")
    
    new_features = [
        '소득수준', '직업분류', '가족상태분류', '자산규모분류', '월저축률',
        '예적금보유', '펀드보유', '주식보유', '보험보유',
        '위험성향분류', '투자경험분류', '투자목적분류', '투자기간분류',
        '질문카테고리', '질문복잡도'
    ]
    
    for feature in new_features:
        print(f"  - {feature}")
    
    return df

def create_target_variable(df):
    """독립변수 문서의 종속변수 8개 상품 기반으로 타겟 생성"""
    
    print("\n🎯 종속변수 생성 중 (8개 한국 금융상품)...")
    
    # 8개 한국 금융상품 정의
    korean_products = {
        'deposits': {'name': '예금', 'risk_level': 1},
        'savings': {'name': '적금', 'risk_level': 1},
        'time_deposits': {'name': '정기예금', 'risk_level': 1},
        'bond_funds': {'name': '채권형펀드', 'risk_level': 2},
        'balanced_funds': {'name': '혼합형펀드', 'risk_level': 3},
        'equity_funds': {'name': '주식형펀드', 'risk_level': 4},
        'etf': {'name': 'ETF', 'risk_level': 3.5},
        'pension': {'name': '연금저축', 'risk_level': 2.5}
    }
    
    def calculate_product_preference(row, product_risk):
        """사용자 특성에 따른 상품 선호도 계산"""
        score = 0.0
        
        # 위험성향 매칭
        risk_mapping = {'보수적': 1, '중간': 2, '적극적': 3}
        user_risk = risk_mapping.get(row['위험성향분류'], 2)
        
        # 위험도 차이가 적을수록 높은 점수
        risk_diff = abs(user_risk - product_risk)
        score += max(0, 3 - risk_diff)
        
        # 나이별 선호도
        age = row['연령']
        if product_risk <= 2 and age > 50:  # 안전 상품 + 고연령
            score += 2
        elif product_risk >= 3 and age < 35:  # 위험 상품 + 젊은 나이
            score += 2
        elif product_risk == 2.5 and 35 <= age <= 50:  # 중간 상품 + 중년
            score += 1.5
        
        # 투자목적 매칭
        purpose = row['투자목적분류']
        if purpose == '노후준비' and product_risk <= 2.5:
            score += 2
        elif purpose == '비상자금' and product_risk <= 1:
            score += 3
        elif purpose == '단기수익' and product_risk >= 3:
            score += 1
        elif purpose == '장기자산' and 2 <= product_risk <= 3:
            score += 1.5
        
        # 가족상태 고려
        if row['가족상태분류'] == '기혼_자녀있음' and product_risk <= 2:
            score += 1
        elif row['가족상태분류'] == '미혼' and product_risk >= 3:
            score += 0.5
        
        # 소득수준 고려
        if row['소득수준'] == '상' and product_risk >= 3:
            score += 1
        elif row['소득수준'] == '하' and product_risk <= 1:
            score += 1
        
        # 투자경험 고려
        if row['투자경험분류'] == '고급' and product_risk >= 3:
            score += 1
        elif row['투자경험분류'] == '초보' and product_risk <= 2:
            score += 1
        
        return score
    
    # 각 상품별 선호도 점수 계산 및 라벨링
    for product_code, product_info in korean_products.items():
        # 선호도 점수 계산
        scores = df.apply(lambda row: calculate_product_preference(row, product_info['risk_level']), axis=1)
        
        # 점수를 확률로 변환 (시그모이드 함수)
        probabilities = 1 / (1 + np.exp(-(scores - 3)))  # 임계값 3
        
        # 상위 30%를 선호하는 것으로 라벨링
        threshold = probabilities.quantile(0.7)
        df[f'{product_code}_preference'] = (probabilities >= threshold).astype(int)
        
        pos_rate = df[f'{product_code}_preference'].mean()
        print(f"  - {product_info['name']}: {pos_rate:.1%} 선호")
    
    # 전체 투자성향도 기존처럼 유지 (참고용)
    def determine_overall_investment_type(row):
        """전체적인 투자성향 결정"""
        if row['위험성향분류'] == '적극적' and row['투자경험분류'] in ['중급', '고급']:
            return 'aggressive'
        elif row['위험성향분류'] == '보수적' or row['연령'] > 60:
            return 'conservative'
        else:
            return 'moderate'
    
    df['전체투자성향'] = df.apply(determine_overall_investment_type, axis=1)
    
    # 분포 확인
    print("\n전체 투자성향 분포:")
    distribution = df['전체투자성향'].value_counts()
    for category, count in distribution.items():
        print(f"  - {category}: {count}명 ({count/len(df)*100:.1f}%)")
    
    return df

def encode_categorical_variables(df):
    """독립변수 문서 기반 범주형 변수 인코딩"""
    
    print("\n🔤 범주형 변수 인코딩 중...")
    
    # 인코딩할 범주형 변수들 (독립변수 문서 기반)
    categorical_cols = [
        '소득수준', '직업분류', '가족상태분류', '자산규모분류',
        '위험성향분류', '투자경험분류', '투자목적분류', '투자기간분류',
        '질문카테고리', '질문복잡도', '전체투자성향'
    ]
    
    encoders = {}
    
    for col in categorical_cols:
        if col in df.columns:
            # 원핫 인코딩 적용
            dummies = pd.get_dummies(df[col], prefix=col)
            df = pd.concat([df, dummies], axis=1)
            
            # 기존 범주형 컬럼은 유지 (참고용)
            print(f"✅ {col} 원핫 인코딩 완료 ({len(dummies.columns)}개 변수)")
    
    return df, encoders

def prepare_ml_features(df):
    """독립변수 문서 기반 ML용 특성 데이터 준비"""
    
    print("\n⚙️ ML 특성 데이터 준비 중...")
    
    # 독립변수 문서의 필수 입력 특성들
    essential_features = [
        # 사용자가 직접 입력 (필수 4개)
        '연령',  # 나이
        # 소득수준 원핫 인코딩된 변수들
        '월저축률',  # 금융 프로필
        
        # 사용자가 직접 입력 (추가 4개)
        # 직업분류, 가족상태분류 원핫 인코딩된 변수들
        # 투자경험분류, 투자기간분류 원핫 인코딩된 변수들
        
        # 금융기관 자동 수집 (5개) 
        '총자산', '순자산',  # 자산규모 대신 원본값 사용
        '예적금보유', '펀드보유', '주식보유', '보험보유',  # 보유상품
        # 질문카테고리, 질문복잡도는 원핫 인코딩된 변수들
    ]
    
    # 원핫 인코딩된 범주형 변수들 찾기
    categorical_encoded_features = []
    categorical_prefixes = [
        '소득수준_', '직업분류_', '가족상태분류_', '자산규모분류_',
        '위험성향분류_', '투자경험분류_', '투자목적분류_', '투자기간분류_',
        '질문카테고리_', '질문복잡도_'
    ]
    
    for prefix in categorical_prefixes:
        encoded_cols = [col for col in df.columns if col.startswith(prefix)]
        categorical_encoded_features.extend(encoded_cols)
    
    # 전체 특성 리스트
    all_features = essential_features + categorical_encoded_features
    
    # 존재하는 컬럼만 선택
    available_features = [col for col in all_features if col in df.columns]
    
    # 8개 한국 금융상품 타겟 변수들
    target_features = [
        'deposits_preference', 'savings_preference', 'time_deposits_preference',
        'bond_funds_preference', 'balanced_funds_preference', 'equity_funds_preference',
        'etf_preference', 'pension_preference'
    ]
    
    # 존재하는 타겟 변수만 선택
    available_targets = [col for col in target_features if col in df.columns]
    
    # 특성 데이터와 타겟 데이터 분리
    X = df[available_features].copy()
    y_dict = {}
    
    for target in available_targets:
        y_dict[target] = df[target].copy()
    
    print(f"✅ 특성 변수: {len(available_features)}개")
    print(f"✅ 타겟 변수: {len(available_targets)}개")
    print(f"✅ 샘플 수: {len(X)}개")
    
    print(f"\n주요 특성 변수:")
    # 필수 특성 출력
    for feature in essential_features:
        if feature in available_features:
            print(f"  - {feature}")
    
    print(f"\n범주형 인코딩 변수: {len(categorical_encoded_features)}개")
    
    print(f"\n타겟 변수 (8개 한국 금융상품):")
    product_names = ['예금', '적금', '정기예금', '채권형펀드', '혼합형펀드', 
                    '주식형펀드', 'ETF', '연금저축']
    for i, target in enumerate(available_targets):
        if i < len(product_names):
            print(f"  - {product_names[i]} ({target})")
    
    return X, y_dict, available_features

def data_summary(df):
    """데이터 요약 정보 출력"""
    
    print("\n📊 최종 데이터 요약")
    print("=" * 50)
    print(f"총 샘플 수: {len(df):,}개")
    print(f"총 변수 수: {len(df.columns)}개")
    
    print("\n주요 통계:")
    summary_cols = ['연령', '총소득', '총자산', '순자산', '금융복잡도', '위험성향점수']
    for col in summary_cols:
        if col in df.columns:
            print(f"  {col}: 평균 {df[col].mean():.1f}, 중앙값 {df[col].median():.1f}")
    
    print("\n투자성향 분포:")
    if '투자성향' in df.columns:
        dist = df['투자성향'].value_counts()
        for category, count in dist.items():
            print(f"  {category}: {count}명 ({count/len(df)*100:.1f}%)")

def main_preprocessing_pipeline(file_path):
    """전체 전처리 파이프라인"""
    
    print("🚀 SCF 데이터 전처리 시작!")
    print("=" * 60)
    
    # 1. 데이터 로드
    df = load_and_clean_scf_data(file_path)
    
    # 2. 데이터 품질 확인
    df = check_data_quality(df)
    
    # 3. 이상값 제거
    df = remove_outliers(df)
    
    # 4. 파생 변수 생성
    df = create_derived_features(df)
    
    # 5. 종속변수 생성
    df = create_target_variable(df)
    
    # 6. 범주형 변수 인코딩
    df, encoders = encode_categorical_variables(df)
    
    # 7. ML용 특성 준비
    X, y, feature_names = prepare_ml_features(df)
    
    # 8. 데이터 요약
    data_summary(df)
    
    print("\n✅ 전처리 완료!")
    
    return df, X, y, feature_names, encoders

# 실행 예시
if __name__ == "__main__":
    # 파일 경로 설정
    file_path = "data/SCFP/SCFP2022_한글.csv"
    
    # 전처리 실행
    cleaned_df, X, y, features, encoders = main_preprocessing_pipeline(file_path)
    
    # 결과 저장
    cleaned_df.to_csv("data/SCFP/cleaned_scf_data.csv", index=False, encoding='utf-8')
    print("\n💾 정제된 데이터가 'cleaned_scf_data.csv'로 저장되었습니다!")