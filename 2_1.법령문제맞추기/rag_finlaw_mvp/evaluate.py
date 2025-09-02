"""
evaluate.py - 웹 호출 가능한 버전 (중복 로그 해결)
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
import traceback
from rag.utils import log_message  # 추가

# 환경변수 로드
load_dotenv()

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def run_evaluation(file_path: str, mcq_limit: int = None, short_limit: int = None, 
                  progress_callback=None) -> dict:
    """평가 실행 함수 - RAG 인스턴스 중복 해소"""
    
    def log(log_type, message):
        """로그 출력 헬퍼"""
        if progress_callback:
            progress_callback(log_type, message)
        else:
            log_message(log_type, message, "EVALUATE")
    
    try:
        log("progress", f"평가 시작: {Path(file_path).name}")
        
        # 파일 검증
        log("progress", "파일 검증 중...")
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            log("failure", f"파일을 찾을 수 없습니다: {file_path}")
            return None
        log("progress", "파일 검증 완료")
        
        # RAG 인스턴스 가져오기 - app.py 우선 사용
        log("progress", "RAG 인스턴스 준비 중...")
        
        try:
            # 웹 환경에서는 app.py 사용
            from app import get_rag_system
            retriever, llm, config = get_rag_system()
            log("progress", "app.py에서 RAG 인스턴스 가져오기 완료")
            
        except ImportError:
            # CLI 환경에서만 직접 생성
            log("progress", "CLI 모드 - 직접 RAG 인스턴스 생성")
            try:
                from rag.hybrid_retriever import HybridRetriever
                from rag.llm_bridge import HybridLLM
                from config import get_config
                
                config = get_config(silent=True)
                retriever = HybridRetriever(config)
                llm = HybridLLM(config)
                log("progress", "CLI용 RAG 인스턴스 생성 완료")
                
            except Exception as e:
                log("failure", f"CLI 모드에서 RAG 생성 실패: {e}")
                return None
        
        if not retriever or not llm or not config:
            log("failure", "RAG 인스턴스 가져오기 실패")
            return None
        
        log("progress", "RAG 인스턴스 준비 완료")
        
        # 3. 평가기 초기화 (기존 인스턴스 전달, 중복 로그 방지)
        log("progress", "평가 시스템 초기화 중...")
        
        try:
            from rag.evaluator import UnifiedEvaluator
            
            # 기존 인스턴스를 전달하여 중복 초기화 방지
            evaluator = UnifiedEvaluator(retriever=retriever, llm=llm, config=config)
            log("progress", "평가 시스템 초기화 완료 (기존 인스턴스 재사용)")
            
        except Exception as e:
            log("failure", f"평가 시스템 초기화 실패: {e}")
            return None
        
        # 4. 평가 실행
        log("progress", "평가 실행 중...")
        
        try:
            # progress_callback 지원하는지 확인
            import inspect
            evaluate_method = getattr(evaluator, 'evaluate_file')
            sig = inspect.signature(evaluate_method)
            
            if 'progress_callback' in sig.parameters:
                # progress_callback 지원
                results = evaluator.evaluate_file(
                    file_path, 
                    mcq_limit, 
                    short_limit,
                    progress_callback=lambda msg: log("progress", msg)
                )
            else:
                # progress_callback 미지원
                log("progress", "progress_callback 미지원 - 기본 평가 실행")
                results = evaluator.evaluate_file(
                    file_path, 
                    mcq_limit, 
                    short_limit
                )
            
            if not results:
                log("failure", "평가할 데이터가 없습니다")
                return None
            
            log("progress", "평가 실행 완료")
            
        except Exception as e:
            log("failure", f"평가 실행 실패: {e}")
            log("failure", f"상세 오류: {traceback.format_exc()}")
            return None
        
        # 5. 결과 저장
        log("progress", "결과 저장 중...")
        
        try:
            saved_file = evaluator.save_results(results)  # 통일된 저장 방식
            
            if saved_file:
                log("success", f"결과 저장 완료: {Path(saved_file).name}")
                results['saved_file'] = saved_file
                return results
            else:
                log("failure", "결과 저장 실패")
                return None
                
        except Exception as e:
            log("failure", f"결과 저장 실패: {e}")
            return None
            
    except Exception as e:
        log("failure", f"예상치 못한 오류: {e}")
        log("failure", f"상세 오류: {traceback.format_exc()}")
        return None

def run_enhanced_evaluation(file_path: str, mcq_limit: int = None, short_limit: int = None) -> bool:
    """
    CLI용 평가 실행 (기존 함수명 유지)
    
    Returns:
        bool: 성공 여부
    """
    results = run_evaluation(file_path, mcq_limit, short_limit)
    return results is not None

def validate_environment():
    """실행 환경 검증 - 조용한 모드"""
    try:
        # 필수 모듈 확인 (조용한 모드로)
        from config import get_config
        config = get_config(silent=True)  # 중복 로그 방지
        
        errors = config.validate(silent=True)  # 중복 로그 방지
        if errors:
            print("[ENV-ERROR] 설정 검증 실패:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("[ENV-OK] 환경 검증 완료")
        return True
        
    except Exception as e:
        print(f"[ENV-ERROR] 환경 검증 중 오류: {e}")
        return False

def main():
    """메인 함수 - CLI 인터페이스"""
    parser = argparse.ArgumentParser(
        description="RAG 시스템 평가 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python evaluate.py test.xlsx --mcq 5 --short 5
  python evaluate.py test.xlsx --mcq 10 --debug
  python evaluate.py test.xlsx --short 20
        """
    )
    
    parser.add_argument('file', nargs='?', help='평가할 Excel 파일 경로')
    parser.add_argument('--mcq', type=int, help='MCQ 문제 수 제한')
    parser.add_argument('--short', type=int, help='단답형 문제 수 제한')
    parser.add_argument('--debug', action='store_true', help='디버그 모드')
    parser.add_argument('--validate-only', action='store_true', help='환경 검증만 실행')
    
    args = parser.parse_args()
    
    # 환경 검증만 실행
    if args.validate_only:
        success = validate_environment()
        sys.exit(0 if success else 1)
    
    if not args.file:
        print("오류: 평가할 파일 경로가 필요합니다.")
        print("사용법: python evaluate.py <excel_file> [--mcq N] [--short N]")
        print("도움말: python evaluate.py --help")
        sys.exit(1)
    
    # 디버그 모드 설정
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("[DEBUG] 디버그 모드 활성화")
    
    # 환경 검증 (조용한 모드)
    print("[CLI] 환경 검증 중...")
    if not validate_environment():
        print("[CLI] 환경 검증 실패 - 실행을 중단합니다.")
        sys.exit(1)
    
    try:
        print(f"[CLI] 평가 시작: {args.file}")
        print(f"[CLI] MCQ 제한: {args.mcq if args.mcq else '제한없음'}")
        print(f"[CLI] 단답형 제한: {args.short if args.short else '제한없음'}")
        
        success = run_enhanced_evaluation(
            file_path=args.file,
            mcq_limit=args.mcq,
            short_limit=args.short
        )
        
        if success:
            print("\n[CLI] 평가가 성공적으로 완료되었습니다!")
            print("[CLI] 결과 파일을 확인하세요.")
        else:
            print("\n[CLI] 평가 실패!")
            print("[CLI] 오류 로그를 확인하고 다시 시도하세요.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n[CLI] 평가가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n[CLI] 예상치 못한 오류 발생: {e}")
        if args.debug:
            import traceback
            print("[CLI-DEBUG] 상세 오류:")
            traceback.print_exc()
        sys.exit(1)

# 웹에서 import할 수 있도록 함수들을 모듈 레벨에서 노출
__all__ = ['run_evaluation', 'run_enhanced_evaluation', 'validate_environment']

if __name__ == "__main__":
    main()