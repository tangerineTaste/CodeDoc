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
    
    # 원본 SCFP2022 데이터인 경우 바로 타겟 변수 생성
    target_amount_columns = ['유동성자산', '양도성예금증서', '비머니마켓펀드', '주식보유', '퇴직준비금유동성']
    has_amount_columns = any(col in df.columns for col in target_amount_columns)
    
    if has_amount_columns:
        print("🎯 SCFP2022 원본 데이터 감지 - 타겟 변수 생성 중...")
        # 금액 컬럼에서 타겟 변수 생성
        target_mapping = {
            'LIQ': '유동성자산',
            'CDS': '양도성예금증서', 
            'NMMF': '비머니마켓펀드',
            'STOCKS': '주식보유',
            'RETQLIQ': '퇴직준비금유동성'
        }
        
        for target, amount_col in target_mapping.items():
            if amount_col in df.columns:
                df[target] = (df[amount_col] > 0).astype(int)
                holding_rate = df[target].mean()
                print(f"  ✅ {target} ({amount_col}): 보유율 {holding_rate*100:.1f}%")
    
    # cleaned_scf_data.csv인 경우 필요한 컬럼만 선택
    if df.shape[1] > 100:  # 전체 데이터인 경우
        print("🔧 전체 데이터에서 필요한 컬럼만 선택 중...")
        
        # 필요한 독립변수 (12개)
        feature_columns = [
            # 최고 중요도 (4개)
            '연령대분류', '교육수준분류', '사업농업소득', '자본이득소득',
            
            # 기본 변수 (4개)
            '연령', '총소득', '금융위험감수', '저축여부',
            
            # 추가 보완 (4개)
            '급여소득', '금융위험회피', '교육수준', '가구주성별',

            # 모든 상품에서 안정적으로 중요한 변수들 (4개)
            '결혼상태', '자녀수', '직업분류1', '총자산'
        ]
        
        # 종속변수 (5개) - 생성된 것 또는 기존 것
        target_columns = ['LIQ', 'CDS', 'NMMF', 'STOCKS', 'RETQLIQ']
        
        # 존재하는 컬럼만 필터링
        all_needed_columns = []
        
        for col in feature_columns + target_columns:
            if col in df.columns:
                all_needed_columns.append(col)
        
        if len(all_needed_columns) > 0:
            df = df[all_needed_columns].copy()
            print(f"선택된 컬럼 수: {len(all_needed_columns)}개")
    
    print(f"정제 후 데이터 크기: {df.shape}")
    print(f"컬럼 수: {len(df.columns)}개")
    
    return df

def check_data_quality(df):
    """데이터 품질 확인"""
    
    print("\n🔍 데이터 품질 확인...")
    
    # 결측값 확인
    missing_count = df.isnull().sum().sum()
    print(f"총 결측값: {missing_count}개")
    
    if missing_count == 0:
        print("✅ 결측값 없음 - 데이터 품질 양호!")
    else:
        print("⚠️ 결측값 발견 - 처리 필요")
    
    # 기본 통계 확인
    print(f"\n📊 기본 정보:")
    print(f"  - 총 샘플 수: {len(df):,}개")
    print(f"  - 총 변수 수: {len(df.columns)}개")
    print(f"  - 메모리 사용량: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    
    return df

def remove_outliers(df):
    """이상값 제거"""
    
    print("\n🚨 이상값 제거 중...")
    original_len = len(df)
    
    # 나이 이상값 (18-100세 범위)
    if '연령' in df.columns:
        df = df[(df['연령'] >= 18) & (df['연령'] <= 100)]
        print(f"  - 연령 이상값 제거 완료")
    
    # 소득 이상값 (상위 1%, 하위 1% 제거)
    if '총소득' in df.columns:
        income_q1 = df['총소득'].quantile(0.01)
        income_q99 = df['총소득'].quantile(0.99)
        df = df[(df['총소득'] >= income_q1) & (df['총소득'] <= income_q99)]
        print(f"  - 총소득 이상값 제거 완료")
    
    # 자산 이상값 (음수 제거, 상위 1% 제거)
    if '총자산' in df.columns:
        asset_q99 = df['총자산'].quantile(0.99)
        df = df[(df['총자산'] >= 0) & (df['총자산'] <= asset_q99)]
        print(f"  - 총자산 이상값 제거 완료")
    
    # 순자산 극단값 제거
    if '순자산' in df.columns:
        networth_q1 = df['순자산'].quantile(0.01)
        networth_q99 = df['순자산'].quantile(0.99)
        df = df[(df['순자산'] >= networth_q1) & (df['순자산'] <= networth_q99)]
        print(f"  - 순자산 이상값 제거 완료")
    
    removed_count = original_len - len(df)
    print(f"✅ 이상값 {removed_count}개 제거 완료 ({removed_count/original_len*100:.1f}%)")
    print(f"정제 후 데이터 크기: {df.shape}")
    
    return df

def create_derived_features(df):
    """필요한 파생 변수 생성"""
    
    print("\n🔧 파생 변수 생성 중...")
    
    # 연령대분류 생성 (없는 경우)
    if '연령대분류' not in df.columns and '연령' in df.columns:
        df['연령대분류'] = pd.cut(df['연령'], 
                                bins=[0, 30, 40, 50, 60, 100],
                                labels=[1, 2, 3, 4, 5])
        print("  - 연령대분류 생성 완료")
    
    # 교육수준분류 생성 (없는 경우)
    if '교육수준분류' not in df.columns and '교육수준' in df.columns:
        def map_education_level(edu_code):
            if edu_code <= 7:
                return 1  # 고등학교 이하
            elif edu_code == 8:
                return 2  # 고등학교 졸업
            elif edu_code <= 11:
                return 3  # 전문대/대학교
            else:
                return 4  # 대학교 졸업 이상
        
        df['교육수준분류'] = df['교육수준'].apply(map_education_level)
        print("  - 교육수준분류 생성 완료")
    
    print("✅ 파생 변수 생성 완료")
    
    return df

def create_target_variable(df):
    """SCFP2022 실제 금융상품 보유 데이터 기반 타겟 생성"""
    
    print("\n🎯 종속변수 생성 중 (5개 실제 금융상품)...")
    
    # SCFP2022의 실제 금액 컬럼명에 맞춰 종속변수 생성
    target_mapping = {
        'LIQ': '유동성자산',           # 유동성자산 금액이 0 이상이면 1
        'CDS': '양도성예금증서',       # 양도성예금증서 금액이 0 이상이면 1  
        'NMMF': '비머니마켓펀드',      # 비머니마켓펀드 금액이 0 이상이면 1
        'STOCKS': '주식보유',         # 주식보유 금액이 0 이상이면 1
        'RETQLIQ': '퇴직준비금유동성'  # 퇴직준비금유동성 금액이 0 이상이면 1
    }
    
    print("=== 타겟 변수 생성 결과 ===")
    created_targets = []
    
    for target, amount_col in target_mapping.items():
        if amount_col in df.columns:
            # 금액이 0보다 크면 1(보유), 아니면 0(미보유)
            df[target] = (df[amount_col] > 0).astype(int)
            
            # 보유율 확인
            holding_rate = df[target].mean()
            print(f"  ✅ {target} ({amount_col}): 보유율 {holding_rate*100:.1f}%")
            created_targets.append(target)
        else:
            print(f"  ⚠️ {amount_col} 컬럼을 찾을 수 없습니다.")
            
            # 대안: 보유여부 컬럼 사용
            backup_col = amount_col + '보유여부'
            if backup_col in df.columns:
                df[target] = df[backup_col]
                holding_rate = df[target].mean()
                print(f"  ✅ {target} (대안: {backup_col}): 보유율 {holding_rate*100:.1f}%")
                created_targets.append(target)
            else:
                print(f"      대안 컬럼({backup_col})도 없음")
    
    print(f"\n생성된 타겟 변수: {len(created_targets)}개")
    return df

def prepare_ml_features(df):
    """특성 중요도 분석 결과 기반 ML용 특성 데이터 준비"""
    
    print("\n⚙️ 특성 중요도 분석 결과 기반 ML 특성 데이터 준비 중...")
    
    # 16개 독립변수 (고정)
    all_features = [
        # 최고 중요도 (4개)
        '연령대분류', '교육수준분류', '사업농업소득', '자본이득소득',
        
        # 기본 변수 (4개)
        '연령', '총소득', '금융위험감수', '저축여부',
        
        # 추가 보완 (4개)
        '급여소득', '금융위험회피', '교육수준', '가구주성별',

        # 모든 상품에서 안정적으로 중요한 변수들 (4개)
        '결혼상태', '자녀수', '직업분류1', '총자산'
    ]
    
    # 5개 종속변수 (고정)
    target_features = ['LIQ', 'CDS', 'NMMF', 'STOCKS', 'RETQLIQ']
    
    # 존재하는 컬럼만 선택
    available_features = [col for col in all_features if col in df.columns]
    missing_features = [col for col in all_features if col not in df.columns]
    available_targets = [col for col in target_features if col in df.columns]
    
    # 특성 데이터와 타겟 데이터 분리
    if len(available_features) > 0:
        X = df[available_features].copy()
    else:
        print("⚠️ 사용 가능한 독립변수가 없습니다!")
        X = pd.DataFrame()
    
    y_dict = {}
    for target in available_targets:
        y_dict[target] = df[target].copy()
    
    print(f"✅ 선택된 특성 변수: {len(available_features)}개")
    if missing_features:
        print(f"⚠️ 누락된 특성 변수: {len(missing_features)}개")
    print(f"✅ 타겟 변수: {len(available_targets)}개")
    print(f"✅ 샘플 수: {len(X)}개")
    
    if missing_features:
        print(f"\n⚠️ 누락된 특성 변수:")
        for feature in missing_features:
            print(f"  - {feature}")
    
    print(f"\n📊 사용된 특성 변수:")
    for i, feature in enumerate(available_features):
        print(f"  {i+1}. {feature}")
    
    print(f"\n🎯 타겟 변수 (5개 실제 금융상품):")
    product_names = {
        'LIQ': '유동성자산',
        'CDS': '양도성예금증서', 
        'NMMF': '비머니마켓펀드',
        'STOCKS': '주식보유',
        'RETQLIQ': '퇴직준비금유동성'
    }
    
    for target in available_targets:
        holding_rate = df[target].mean() if target in df.columns else 0
        product_name = product_names.get(target, target)
        print(f"  - {product_name} ({target}): {holding_rate:.1%}")
    
    return X, y_dict, available_features

def encode_categorical_variables(df):
    """SCFP2022 데이터에 맞는 범주형 변수 처리"""
    
    print("\n🔤 범주형 변수 처리 중...")
    
    # SCFP2022는 대부분 수치형 코드로 되어있으므로 Tree-based 모델에 적합
    # 필요한 전처리만 수행
    
    processed_count = 0
    
    # 연령대분류 확인 및 정리
    if '연령대분류' in df.columns:
        df['연령대분류'] = df['연령대분류'].astype(int)
        processed_count += 1
    
    # 교육수준분류 확인 및 정리
    if '교육수준분류' in df.columns:
        df['교육수준분류'] = df['교육수준분류'].astype(int)
        processed_count += 1
    
    print(f"✅ 범주형 변수 처리 완료: {processed_count}개")
    print("  - 대부분 수치형 코드로 유지 (Tree-based 모델에 적합)")
    
    return df, {}

def data_summary(df, X, y_dict):
    """데이터 요약 정보 출력"""
    
    print("\n📊 최종 데이터 요약")
    print("=" * 60)
    print(f"총 샘플 수: {len(df):,}개")
    print(f"총 변수 수: {len(df.columns)}개")
    print(f"독립변수 수: {len(X.columns)}개")
    print(f"타겟변수 수: {len(y_dict)}개")
    
    print("\n주요 통계:")
    summary_cols = ['연령', '총소득', '총자산', '순자산']
    for col in summary_cols:
        if col in df.columns:
            print(f"  {col}: 평균 {df[col].mean():.0f}, 중앙값 {df[col].median():.0f}")
    
    print("\n타겟 변수 분포:")
    for target, target_data in y_dict.items():
        pos_rate = target_data.mean()
        print(f"  {target}: {pos_rate:.1%} 보유")
    
    print("\n메모리 사용량:")
    print(f"  전체 데이터: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    print(f"  독립변수: {X.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

def main_preprocessing_pipeline(file_path):
    """전체 전처리 파이프라인"""
    
    print("🚀 SCF 데이터 전처리 시작!")
    print("=" * 60)
    
    try:
        # 1. 데이터 로드 (여기서 SCFP2022 원본이면 타겟 변수도 자동 생성)
        df = load_and_clean_scf_data(file_path)
        
        # 2. 데이터 품질 확인
        df = check_data_quality(df)
        
        # 타겟 변수가 있는지 확인
        target_exists = any(col in df.columns for col in ['LIQ', 'CDS', 'NMMF', 'STOCKS', 'RETQLIQ'])
        
        if not target_exists:
            print("\n🎯 타겟 변수가 없어서 추가 처리가 필요합니다!")
            
            # 3. 이상값 제거
            df = remove_outliers(df)
            
            # 4. 파생 변수 생성
            df = create_derived_features(df)
            
            # 5. 종속변수 생성 (필요한 경우만)
            df = create_target_variable(df)
            
            # 6. 범주형 변수 처리
            df, encoders = encode_categorical_variables(df)
        else:
            print("\n✅ 타겟 변수가 이미 존재합니다!")
            # 간단한 처리만 수행
            df = remove_outliers(df)
            df = create_derived_features(df)
            df, encoders = encode_categorical_variables(df)
        
        # 7. ML용 특성 준비
        X, y_dict, feature_names = prepare_ml_features(df)
        
        # 8. 데이터 요약
        data_summary(df, X, y_dict)
        
        print("\n✅ 전처리 완료!")
        
        return df, X, y_dict, feature_names, encoders
        
    except Exception as e:
        print(f"\n❌ 전처리 중 오류 발생: {str(e)}")
        raise e

# 실행 예시
if __name__ == "__main__":
    # 파일 경로 설정
    file_path = "data/SCFP/SCFP2022_한글.csv"
    
    try:
        # 전처리 실행
        print("데이터 전처리 시작...")
        cleaned_df, X, y_dict, features, encoders = main_preprocessing_pipeline(file_path)
        
        # 결과 확인
        print("\n📊 최종 결과:")
        print(f"독립변수: {len(features)}개")
        print(f"타겟변수: {len(y_dict)}개")
        print(f"샘플 수: {len(X)}개")
        
        # 타겟 변수별 보유율 출력
        print("\n🎯 상품별 보유율:")
        for target, target_data in y_dict.items():
            print(f"  {target}: {target_data.mean():.1%}")
        
        # 결과 저장 (기존 코드와 동일한 형식으로)
        cleaned_df.to_csv("data/SCFP/cleaned_scf_data.csv", index=False, encoding='utf-8')
        print("\n💾 정제된 데이터가 'cleaned_scf_data.csv'로 저장되었습니다!")
        
        # 기존 변수명 호환을 위해 y_dict를 y로 변환 (선택사항)
        y = y_dict  # 또는 필요에 따라 특정 타겟만 선택
        
        # 다음 단계 안내
#        print("\n🔄 다음 단계:")
#        print("1. Random Forest 모델 학습")
#        print("2. 특성 중요도 분석")
#        print("3. 모델 성능 평가")
#        print("4. Django API 구축")
        
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        print("파일 경로를 확인해주세요.")
        
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {str(e)}")
        print("데이터 파일의 형식이나 컬럼명을 확인해주세요.")