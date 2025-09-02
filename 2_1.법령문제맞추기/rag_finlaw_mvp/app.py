import streamlit as st
import os
import sys
import glob
import pandas as pd
from pathlib import Path
from datetime import datetime
import threading
import time
import traceback
import uuid
import re
import subprocess

# 스레드 안전성을 위한 추가 import
try:
    from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
except ImportError:
    add_script_run_ctx = lambda t, ctx=None: None
    get_script_run_ctx = lambda: None

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# utils.log_message import 추가
from rag.utils import log_message  # 추가

# ========== CONFIG 로그 동기화 함수 추가 ==========
def add_to_mgmt_log(message):
    """CONFIG 로그를 관리 로그에 동기화"""
    try:
        if hasattr(st.session_state, 'mgmt_logs'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.mgmt_logs.append(f"[{timestamp}] {message}")
            if len(st.session_state.mgmt_logs) > 50:
                st.session_state.mgmt_logs.pop(0)
    except:
        pass

# ========== 단순화된 로그 라우팅 시스템 ==========
# app.py enhanced_global_log_callback 수정 - 타임스탬프 선택적 제거

def enhanced_global_log_callback(log_type, message, module="", category="evaluation"):
    """로그 라우팅 - 크기 제한 제거"""
    
    formatted_msg = f"[{module}] {message}" if module else message
    
    # 중복 방지
    if hasattr(st.session_state, 'last_log_message') and st.session_state.last_log_message == formatted_msg:
        return
    
    st.session_state.last_log_message = formatted_msg
    print(formatted_msg)
    
    # 세션 상태 초기화 확인
    if 'mgmt_logs' not in st.session_state:
        return
    
    try:
        # 기존의 정교한 라우팅 로직 유지
        if 'temp_question_logs' not in st.session_state:
            st.session_state.temp_question_logs = {}
        if 'current_question' not in st.session_state:
            st.session_state.current_question = None
        
        # 타임스탬프는 관리용만
        timestamp = datetime.now().strftime("%H:%M:%S")
        mgmt_log_entry = f"[{timestamp}] {formatted_msg}"
        
        # 정답/오답용은 타임스탬프 없이
        clean_log_entry = formatted_msg
        
        # 1. 문제 처리 시작 감지
        if "처리 시작" in message and ("MCQ-" in message or "SHORT-" in message):
            question_match = re.search(r"(MCQ|SHORT)-(\d+)", message)
            if question_match:
                q_type, q_num = question_match.groups()
                question_key = f"{q_type}-{q_num}"
                
                st.session_state.temp_question_logs[question_key] = [clean_log_entry]
                st.session_state.current_question = question_key
                
                # 문제별 상태 업데이트
                text_match = re.search(r"'(.+?)'", message)
                if text_match:
                    question_text = text_match.group(1).strip()
                    if q_type == "MCQ":
                        update_mcq_question(int(q_num), question_text, status="processing")
                    else:
                        update_short_question(int(q_num), question_text, status="processing")
                return
        
        # 2. 정답 확정 - 정답 로그창으로 이동
        if "정답:" in message:
            if st.session_state.current_question and st.session_state.current_question in st.session_state.temp_question_logs:
                for temp_log in st.session_state.temp_question_logs[st.session_state.current_question]:
                    st.session_state.correct_process_logs.append(temp_log)
                st.session_state.correct_process_logs.append(clean_log_entry)
                st.session_state.correct_process_logs.append("=" * 50)
                
                update_question_status_correct(st.session_state.current_question, message)
                
                del st.session_state.temp_question_logs[st.session_state.current_question]
                st.session_state.current_question = None
                return
            else:
                st.session_state.correct_process_logs.append(clean_log_entry)
                return
        
        # 3. 오답 확정 - 오답 로그창으로 이동
        if "오답:" in message:
            if st.session_state.current_question and st.session_state.current_question in st.session_state.temp_question_logs:
                for temp_log in st.session_state.temp_question_logs[st.session_state.current_question]:
                    st.session_state.incorrect_process_logs.append(temp_log)
                st.session_state.incorrect_process_logs.append(clean_log_entry)
                st.session_state.incorrect_process_logs.append("=" * 50)
                
                update_question_status_incorrect(st.session_state.current_question, message)
                
                del st.session_state.temp_question_logs[st.session_state.current_question]
                st.session_state.current_question = None
                return
            else:
                st.session_state.incorrect_process_logs.append(clean_log_entry)
                return
        
        # 4. 현재 처리 중인 문제 관련 로그 - 임시 버퍼에 추가
        if st.session_state.current_question:
            if st.session_state.current_question in st.session_state.temp_question_logs:
                st.session_state.temp_question_logs[st.session_state.current_question].append(clean_log_entry)
                return
        
        # 5. 관리 로그는 타임스탬프 유지
        management_keywords = [
            "CONFIG", "config", "API", "키 검증", "설정", "초기화", "로드", "연결",
            "인스턴스", "모듈", "컴포넌트", "시작:", "준비", "환경", "RETRIEVER", 
            "EMBEDDER", "LLM", "Bridge", "Upstage", "OpenAI", "Pinecone", "BM25",
            "평가 시작:", "평가 완료", "통계", "요약", "결과:", "실행 시간:",
            "============", "운영", "완료:", "누적:", "패턴 분석"
        ]
        
        if any(keyword in message for keyword in management_keywords):
            st.session_state.mgmt_logs.append(mgmt_log_entry)
            # *** 크기 제한 제거 - 기존 50개 제한 삭제 ***
            return
        
        # 6. 기타 모든 로그도 관리 로그로
        st.session_state.mgmt_logs.append(mgmt_log_entry)
        # *** 크기 제한 제거 - 기존 50개 제한 삭제 ***
            
    except Exception as e:
        print(f"[LOG-ROUTING-ERROR] {e}")

def update_question_status_correct(question_key, message):
    """정답 문제의 상태 업데이트"""
    try:
        q_type, q_num = question_key.split('-')
        q_num = int(q_num)
        
        if q_type == "MCQ":
            # MCQ 정답 처리
            correct_match = re.search(r"정답: (\d+)", message)
            if correct_match:
                correct_num = int(correct_match.group(1))
                predicted = correct = chr(64 + correct_num)
                
                for q in st.session_state.mcq_question_log:
                    if q.get('number') == q_num:
                        q.update({
                            'predicted': predicted,
                            'correct': correct,
                            'is_correct': True,
                            'status': 'completed'
                        })
                        break
                        
                st.session_state.mcq_stats['correct'] += 1
                st.session_state.mcq_stats['total'] += 1
        
        else:  # SHORT
            # SHORT 정답 처리
            answer_match = re.search(r"정답: '([^']+)'", message)
            if answer_match:
                predicted = correct = answer_match.group(1)
                em_score = f1_score = 1.0  # 정답이므로
                
                for q in st.session_state.short_question_log:
                    if q.get('number') == q_num:
                        q.update({
                            'predicted': predicted,
                            'correct': correct,
                            'em_score': em_score,
                            'f1_score': f1_score,
                            'status': 'completed'
                        })
                        break
                        
                st.session_state.short_stats['correct'] += 1
                st.session_state.short_stats['total'] += 1
                
    except Exception as e:
        print(f"[CORRECT-STATUS-ERROR] {e}")

def update_question_status_incorrect(question_key, message):
    """오답 문제의 상태 업데이트"""
    try:
        q_type, q_num = question_key.split('-')
        q_num = int(q_num)
        
        if q_type == "MCQ":
            # MCQ 오답 처리
            error_match = re.search(r"예측=(\d+), 정답=(\d+)", message)
            if error_match:
                predicted_num = int(error_match.group(1))
                correct_num = int(error_match.group(2))
                predicted = chr(64 + predicted_num)
                correct = chr(64 + correct_num)
                
                for q in st.session_state.mcq_question_log:
                    if q.get('number') == q_num:
                        q.update({
                            'predicted': predicted,
                            'correct': correct,
                            'is_correct': False,
                            'status': 'completed'
                        })
                        break
                        
                st.session_state.mcq_stats['total'] += 1
        
        else:  # SHORT
            # SHORT 오답 처리
            error_match = re.search(r"예측='([^']+)', 정답='([^']+)'.*?EM=([A-Za-z]+|[0-9.]+), F1=([0-9.]+)", message)
            if error_match:
                predicted = error_match.group(1)
                correct = error_match.group(2)
                em_str = error_match.group(3)
                em_score = 1.0 if em_str == "True" else (0.0 if em_str == "False" else float(em_str))
                f1_score = float(error_match.group(4))
                
                for q in st.session_state.short_question_log:
                    if q.get('number') == q_num:
                        q.update({
                            'predicted': predicted,
                            'correct': correct,
                            'em_score': em_score,
                            'f1_score': f1_score,
                            'status': 'completed'
                        })
                        break
                        
                if em_score > 0:
                    st.session_state.short_stats['correct'] += 1
                st.session_state.short_stats['total'] += 1
                
    except Exception as e:
        print(f"[INCORRECT-STATUS-ERROR] {e}")

# ========== 세션 상태 초기화 ==========
def init_session_state():
    """통합 세션 상태 초기화 - evaluator 통계도 포함"""
    session_defaults = {
        'evaluation_running': False,
        'evaluation_completed': False,
        
        # MCQ 문제별 상태 + 통계
        'mcq_question_log': [],
        'mcq_stats': {'correct': 0, 'total': 0},
        
        # 단답형 문제별 상태 + 통계  
        'short_question_log': [],
        'short_stats': {'correct': 0, 'total': 0},
        'short_f1_total': 0.0,  # F1 점수 누적용 추가
        
        # evaluator 오류 패턴 통계 추가
        'mcq_error_patterns': {
            'choice_mapping': 0,
            'context_quality': 0,
            'search_failure': 0,
            'negative_detection': 0,
            'llm_reasoning': 0
        },
        'short_error_patterns': {
            'context_mismatch': 0,
            'extraction_failure': 0,
            'low_bm25_score': 0,
            'no_search_results': 0,
            'normalization_failure': 0
        },
        'search_quality_issues': 0,
        'performance_metrics': {
            'avg_mcq_time': 0.0,
            'avg_short_time': 0.0,
            'total_time': 0.0,
            'search_success_rate': 0.0
        },
        
        # 정답/오답 처리과정 로그
        'correct_process_logs': [],
        'incorrect_process_logs': [],
        
        # 관리 로그
        'mgmt_logs': [],
        'evaluation_progress': {'current': 0, 'total': 0},
        'chat_history': [],
        'session_id': str(uuid.uuid4())[:8],
        
        # 임시 버퍼
        'temp_question_logs': {},
        'current_question': None,
        
        # 관리 작업 상태
        'management_tasks': {
            '벡터 재생성': {'status': 'ready', 'last_run': None},
            'BM25 재생성': {'status': 'ready', 'last_run': None},
            '백업': {'status': 'ready', 'last_run': None}
        },
        
        # 중복 로그 방지용
        'last_log_message': None
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # 글로벌 콜백 함수도 세션 상태에 등록
    if 'global_log_callback' not in st.session_state:
        st.session_state.global_log_callback = enhanced_global_log_callback

# 초기화 실행
init_session_state()

# ========== RAG 시스템 관리 ==========
def get_rag_system():
    """Streamlit 세션 기반 RAG 시스템 관리"""
    if (hasattr(st.session_state, 'rag_retriever') and 
        hasattr(st.session_state, 'rag_llm') and 
        hasattr(st.session_state, 'rag_config')):
        return st.session_state.rag_retriever, st.session_state.rag_llm, st.session_state.rag_config
    
    try:
        # CONFIG 로그 동기화 설정 - 한 번에 import
        from config import get_config, set_web_log_func
        set_web_log_func(add_to_mgmt_log)
        
        from rag.hybrid_retriever import HybridRetriever
        from rag.llm_bridge import HybridLLM
        
        config = get_config()
        retriever = HybridRetriever(config)
        llm = HybridLLM(config)
        
        if not retriever or not llm:
            raise RuntimeError("RAG 컴포넌트 초기화 실패")
        
        st.session_state.rag_retriever = retriever
        st.session_state.rag_llm = llm
        st.session_state.rag_config = config
        
        return retriever, llm, config
        
    except Exception as e:
        log_message("FAILURE", f"RAG 초기화 실패: {e}", "APP")
        return None, None, None

def get_rag_available():
    """RAG 사용 가능 여부 확인"""
    retriever, llm, config = get_rag_system()
    return retriever is not None and llm is not None and config is not None

# ========== 질의응답 기능 ==========
def retrieve(question, top_k=5):
    """검색 함수 - 오류 처리 강화"""
    retriever, llm, config = get_rag_system()
    if not retriever:
        log_message("FAILURE", "검색기를 사용할 수 없습니다", "APP")
        return []
    
    try:
        search_results = retriever.search(question, question_type="short")
        results = []
        
        for result in search_results[:top_k]:
            if hasattr(result, 'content') and hasattr(result, 'score'):
                results.append({
                    'text': result.content, 
                    'score': result.score
                })
            else:
                log_message("FAILURE", "검색 결과 형식 오류", "APP")
        
        return results
        
    except Exception as e:
        log_message("FAILURE", f"검색 실행 오류: {e}", "APP")
        return []

def call_simple_llm(user_prompt, context=""):
    """참고자료 우선 + 일반지식 보완 방식"""
    retriever, llm, config = get_rag_system()
    if not llm:
        return "시스템 오류"
    
    # context가 제공된 경우 참고자료 우선 + 보완 답변
    if context and context.strip():
        system_prompt = """한국 법령 전문가로서 참고자료를 우선 활용하되, 필요시 일반 지식으로 보완하여 답변하세요.

**답변 원칙:**
1. 참고자료에 직접적인 답이 있으면 그것을 우선적으로 사용
2. 참고자료가 부족하거나 불완전하면 일반 지식으로 보완
3. 참고자료와 일반 지식을 구분해서 명시
4. 정확하고 유용한 답변 제공이 목표

**답변 형식:**
- 참고자료 기반 답변이 가능하면: 직접 답변
- 참고자료가 부족하면: "참고자료에는 구체적인 내용이 없지만, 일반적으로 [보완설명]입니다. 정확한 내용은 관련 법령을 직접 확인해주세요."
"""
        
        enhanced_prompt = f"""참고자료:
{context}

질문: {user_prompt}

답변:"""
        
        try:
            return llm._call_llm(system_prompt, enhanced_prompt)
        except Exception as e:
            log_message("FAILURE", f"컨텍스트 기반 LLM 호출 실패: {e}", "APP")
            return "답변 생성에 실패했습니다."
    
    else:
        # context가 없는 경우 일반 질문으로 처리
        system_prompt = """한국 법령 전문가로서 질문에 답하세요.

**답변 원칙:**
- 정확하고 간결하게 답변하세요
- 불확실한 내용은 명시적으로 표시하세요
- 법령 관련 질문의 경우 구체적인 조문이나 기관을 언급하세요

확실하지 않은 경우 "일반적인 내용으로 답변드리며, 정확한 내용은 관련 법령을 직접 확인해주세요"라고 안내하세요."""
        
        try:
            return llm._call_llm(system_prompt, user_prompt)
        except Exception as e:
            log_message("FAILURE", f"일반 LLM 호출 실패: {e}", "APP")
            return "답변 생성에 실패했습니다."


# generate_answer_short 함수도 일관성을 위해 수정

def generate_answer_short(question, contexts):
    """질의응답용 자연스러운 답변 생성 - 수정된 버전"""
    retriever, llm, config = get_rag_system()
    if not llm:
        return "시스템 오류"
        
    if not contexts:
        return "관련 정보를 찾을 수 없습니다."
    
    # 컨텍스트 텍스트 구성
    context_text = "\n".join([ctx['text'] for ctx in contexts])
    
    # call_simple_llm을 사용하여 일관성 유지
    answer = call_simple_llm(question, context_text)
    
    # 답변 후처리
    if not answer or answer.strip() == "":
        return "죄송합니다. 해당 질문에 대한 답변을 찾을 수 없습니다."
    
    return answer.strip()

def format_answer_for_chat(question, raw_answer):
    """질의응답용 답변을 완전한 문장으로 포맷팅"""
    if not raw_answer or raw_answer.strip() == "":
        return "죄송합니다. 해당 질문에 대한 답변을 찾을 수 없습니다."
    
    answer = raw_answer.strip()
    
    if answer.endswith(('.', '다', '요', 'ㅂ', '것', '니다', '습니다', '입니다')):
        return answer
    
    if answer.endswith('으로') or answer.endswith('에서') or answer.endswith('는'):
        return f"{answer} 정해져 있습니다."
    
    if '다음' in answer and ('각 호' in answer or '요건' in answer):
        return f"{answer} 모든 조건을 충족해야 합니다."
    
    return f"{answer}."

def add_to_chat_history(question, answer, contexts=None):
    """채팅 기록에 질문과 답변 추가"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    st.session_state.chat_history.append({
        "type": "user",
        "content": question,
        "timestamp": timestamp
    })
    st.session_state.chat_history.append({
        "type": "assistant", 
        "content": answer,
        "timestamp": timestamp,
        "contexts": contexts or []
    })

def display_chat_history():
    """채팅 기록 표시"""
    if st.session_state.chat_history:
        st.subheader("대화 기록")
        
        chat_container = st.container()
        with chat_container:
            for i, chat in enumerate(st.session_state.chat_history):
                if chat["type"] == "user":
                    st.markdown(f"**사용자 {chat['timestamp']}:** {chat['content']}")
                else:
                    st.markdown(f"**Assistant {chat['timestamp']}:** {chat['content']}")
                    
                    if chat.get('contexts'):
                        with st.expander(f"검색 결과 보기 ({len(chat['contexts'])}개)"):
                            for j, ctx in enumerate(chat['contexts'][:3], 1):
                                st.write(f"**[{j}]** Score: {ctx['score']:.3f}")
                                st.write(f"{ctx['text'][:200]}...")
                
                if i < len(st.session_state.chat_history) - 1:
                    st.markdown("<hr style='margin: 8px 0; border: 1px solid #e0e0e0;'>", unsafe_allow_html=True)

# ========== MCQ/SHORT 문제 상태 업데이트 함수들 ==========
def update_mcq_question(question_num, question_text, choices=None, predicted=None, correct=None, is_correct=None, status="processing"):
    """MCQ 문제 상태 업데이트"""
    try:
        existing_idx = -1
        for i, q in enumerate(st.session_state.mcq_question_log):
            if q.get('number') == question_num:
                existing_idx = i
                break
        
        question_data = {
            'number': question_num,
            'text': question_text,
            'choices': choices or [],
            'predicted': predicted,
            'correct': correct,
            'is_correct': is_correct,
            'status': status,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        
        if existing_idx >= 0:
            st.session_state.mcq_question_log[existing_idx].update(question_data)
        else:
            st.session_state.mcq_question_log.append(question_data)
    
    except Exception as e:
        print(f"[MCQ-UPDATE-ERROR] {e}")

def update_short_question(question_num, question_text, predicted=None, correct=None, em_score=None, f1_score=None, status="processing"):
    """단답형 문제 상태 업데이트"""
    try:
        existing_idx = -1
        for i, q in enumerate(st.session_state.short_question_log):
            if q.get('number') == question_num:
                existing_idx = i
                break
        
        question_data = {
            'number': question_num,
            'text': question_text,
            'predicted': predicted,
            'correct': correct,
            'em_score': em_score,
            'f1_score': f1_score,
            'status': status,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        
        if existing_idx >= 0:
            st.session_state.short_question_log[existing_idx].update(question_data)
        else:
            st.session_state.short_question_log.append(question_data)
    
    except Exception as e:
        print(f"[SHORT-UPDATE-ERROR] {e}")

# ========== 로그 포맷팅 함수들 ==========
def format_question_log(question_log, question_type):
    """통합 문제 로그 포맷팅"""
    if not question_log:
        return f"{question_type} 문제 처리 대기 중..."
    
    log_lines = []
    stats_data = {'total_f1': 0, 'completed_count': 0}
    
    for q in question_log[-10:]:
        question_text = q.get('text', '')[:50] + ('...' if len(q.get('text', '')) > 50 else '')
        
        if q.get('status') == 'processing':
            log_lines.extend([f"문제 {q['number']}: {question_text}", "-> 처리 중...", ""])
            continue
        
        if q.get('status') != 'completed':
            continue
            
        log_lines.append(f"문제 {q['number']}: {question_text}")
        
        if question_type == "MCQ":
            if q.get('choices'):
                choices_str = " ".join([f"{chr(65+i)}) {choice[:20]}{'...' if len(choice) > 20 else ''}" 
                                       for i, choice in enumerate(q['choices'][:4])])
                log_lines.append(f"선택지: {choices_str}")
            
            predicted, correct = q.get('predicted', 'N/A'), q.get('correct', 'N/A')
            status_icon = "O" if q.get('is_correct') else "X"
            log_lines.append(f"-> 예측: {predicted}, 정답: {correct} {status_icon}")
        
        else:  # SHORT
            predicted = q.get('predicted', 'N/A')[:30] + ('...' if len(q.get('predicted', '')) > 30 else '')
            correct = q.get('correct', 'N/A')[:30] + ('...' if len(q.get('correct', '')) > 30 else '')
            
            em_score, f1_score = q.get('em_score', 0), q.get('f1_score', 0)
            status_icon = "O" if em_score > 0 else "X"
            
            log_lines.extend([
                f"-> 예측: '{predicted}' {status_icon}",
                f"   정답: '{correct}'",
                f"   (EM={em_score:.2f}, F1={f1_score:.2f})"
            ])
            
            stats_data['total_f1'] += f1_score
            stats_data['completed_count'] += 1
        
        log_lines.append("")
    
    # 통계 추가
    log_lines.extend(["=" * 30])
    if question_type == "MCQ":
        add_mcq_stats(log_lines)
    else:
        add_short_stats(log_lines, stats_data)
    
    return "\n".join(log_lines)

# app.py - format_question_log 함수에서 통계 출력 부분
def add_mcq_stats(log_lines):
    """MCQ 통계 추가 - 초기값 출력 방지"""
    # 현재 배치 통계 우선 사용
    if hasattr(st.session_state, 'mcq_current_batch_stats'):
        stats = st.session_state.mcq_current_batch_stats
        if stats['total'] > 0:  # 초기값 방지
            log_lines.append(f"MCQ 통계: 정확도 {stats['accuracy']:.1%} ({stats['correct']}/{stats['total']})")
        return
    
    # fallback: 최종 통계
    if hasattr(st.session_state, 'mcq_final_stats'):
        stats = st.session_state.mcq_final_stats
        if stats.get('total', 0) > 0:  # 초기값 방지
            log_lines.append(f"MCQ 통계: 정확도 {stats['accuracy']:.1f}% ({stats['correct']}/{stats['total']})")
        return
    
    # 기존 통계 - 초기값일 때는 출력 안함
    stats = st.session_state.mcq_stats
    if stats['total'] > 0:
        accuracy = stats['correct'] / stats['total']
        log_lines.append(f"MCQ 통계: 정확도 {accuracy:.1%} ({stats['correct']}/{stats['total']})")
    # else: 아무 통계도 출력하지 않음

def add_short_stats(log_lines, stats_data):
    """단답형 통계 추가 - 초기값 출력 방지"""
    # 현재 배치 통계 우선 사용
    if hasattr(st.session_state, 'short_current_batch_stats'):
        stats = st.session_state.short_current_batch_stats
        if stats['total'] > 0:  # 초기값 방지
            log_lines.extend([
                f"단답형 통계: EM {stats['em_avg']:.1%} ({stats['correct']}/{stats['total']})",
                f"평균 F1: {stats['f1_avg']:.2f}"
            ])
        return
    
    # fallback: 최종 통계
    if hasattr(st.session_state, 'short_final_stats'):
        stats = st.session_state.short_final_stats
        if stats.get('total', 0) > 0:  # 초기값 방지
            log_lines.append(f"단답형 통계: EM {stats['em']:.1f}%, F1 {stats['f1']:.1f}%")
        return
    
    # 기존 통계 - 초기값일 때는 출력 안함
    stats = st.session_state.short_stats
    if stats['total'] > 0:
        em_accuracy = stats['correct'] / stats['total']
        f1_total = getattr(st.session_state, 'short_f1_total', 0.0)
        avg_f1 = f1_total / stats['total']
        
        log_lines.extend([
            f"단답형 통계: EM {em_accuracy:.1%} ({stats['correct']}/{stats['total']})",
            f"평균 F1: {avg_f1:.2f}"
        ])
    # else: 아무 통계도 출력하지 않음

def format_mcq_question_log():
    """MCQ 로그 포맷팅"""
    return format_question_log(st.session_state.mcq_question_log, "MCQ")

def format_short_question_log():
    """단답형 로그 포맷팅"""
    return format_question_log(st.session_state.short_question_log, "SHORT")

def display_real_time_monitoring():
    """실시간 평가 모니터링 - 초밀착 간격"""
    
    # 진행률 (이것도 간격 줄이기)
    progress = st.session_state.evaluation_progress
    if st.session_state.evaluation_running and progress['total'] > 0:
        progress_percent = progress['current'] / progress['total']
        st.progress(progress_percent, f"전체 진행: {progress['current']}/{progress['total']} 문제 완료 ({progress_percent:.1%})")
    elif st.session_state.evaluation_running:
        st.progress(0, "평가 준비 중...")
    
    # 추가 간격 제거 CSS (모니터링 전용)
    st.markdown("""
    <style>
        /* 진행률 바 아래 간격 제거 */
        .stProgress {
            margin-bottom: 0px !important;
        }
        
        /* 모니터링 섹션 전체 간격 최소화 */
        .monitoring-section {
            margin: 0px !important;
            padding: 0px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # MCQ vs 단답형 (초밀착)
    col_mcq, col_short = st.columns(2)
    
    with col_mcq:
        st.markdown('<div class="log-title">선다형 (MCQ) 문제별 상태</div>', 
                   unsafe_allow_html=True)
        mcq_log_text = format_mcq_question_log()
        st.text_area("MCQ 상태", value=mcq_log_text, height=200,
                    key="mcq_monitor_area", label_visibility="hidden")
    
    with col_short:
        st.markdown('<div class="log-title">단답형 문제별 상태</div>', 
                   unsafe_allow_html=True)
        short_log_text = format_short_question_log()
        st.text_area("단답형 상태", value=short_log_text, height=200,
                    key="short_monitor_area", label_visibility="hidden")

# ========== 스레드 및 백그라운드 작업 ==========
# get_excel_files 함수에서 로그 사용 예시
def get_excel_files():
    """루트 디렉토리의 Excel 파일 목록"""
    try:
        excel_files = []
        for pattern in ["*.xlsx", "*.xls"]:
            files = glob.glob(str(project_root / pattern))
            excel_files.extend([Path(f).name for f in files if not Path(f).name.startswith("evaluation_")])
        return sorted(excel_files)
    except Exception as e:
        # utils.log_message 사용
        log_message("FAILURE", f"Excel 파일 목록 가져오기 실패: {e}", "APP")
        return []

def create_safe_thread(target_func, args=None, name=None):
    """통합 스레드 생성 함수"""
    thread = threading.Thread(
        target=target_func, 
        args=args or (), 
        name=name or "background_task",
        daemon=True
    )
    
    try:
        ctx = get_script_run_ctx()
        if ctx:
            add_script_run_ctx(thread, ctx)
    except:
        pass
    
    return thread

# app.py의 run_evaluation_task 함수 수정

def run_evaluation_task(excel_file, mcq_limit, short_limit):
    """평가 실행 작업 - 진행률 업데이트만 추가"""
    try:
        retriever, llm, config = get_rag_system()
        if not all([retriever, llm, config]):
            print("RAG 인스턴스 초기화 실패")
            return
            
        from rag.evaluator import UnifiedEvaluator
        evaluator = UnifiedEvaluator(retriever=retriever, llm=llm, config=config)
        
        # *** 진행률 업데이트하는 콜백 함수 추가 ***
        def update_progress_callback(msg):
            try:
                # 기존 로그 콜백 유지
                enhanced_global_log_callback("progress", msg, "EVALUATOR", "evaluation")
                
                # 진행률 업데이트 추가
                if "MCQ-" in msg or "SHORT-" in msg:
                    # MCQ-1, SHORT-1 등에서 숫자 추출
                    import re
                    match = re.search(r"(MCQ|SHORT)-(\d+)", msg)
                    if match:
                        question_num = int(match.group(2))
                        # 현재 진행률 업데이트
                        if hasattr(st.session_state, 'evaluation_progress'):
                            st.session_state.evaluation_progress['current'] = question_num
            except:
                # 오류가 있어도 기존 콜백은 계속 작동
                enhanced_global_log_callback("progress", msg, "EVALUATOR", "evaluation")
        
        file_path = project_root / excel_file
        results = evaluator.evaluate_file(str(file_path), mcq_limit, short_limit, progress_callback=update_progress_callback)
        
        # 나머지 코드는 기존과 동일
        saved_file = None
        if results:
            try:
                from rag.utils import save_evaluation_results
                saved_file = save_evaluation_results(results)
                
                if saved_file:
                    st.session_state.last_saved_file = saved_file
                else:
                    log_message("FAILURE", "결과 저장 실패", "APP")
            except Exception as e:
                log_message("FAILURE", f"결과 저장 오류: {e}", "APP")
        
        st.session_state.evaluation_running = False
        st.session_state.evaluation_completed = bool(results)
        print("평가 완료!" if results else "평가 실행 실패")
        
    except Exception as e:
        print(f"평가 오류: {str(e)}")
        st.session_state.evaluation_running = False

# ========== 관리 작업 관련 함수들 ==========
def check_script_files():
    """스크립트 파일 존재 여부 및 상태 확인"""
    script_files = {
        "reindex_upstage_docx.py": "벡터 재생성",
        "pipeline_bm25_from_docx.py": "BM25 재생성", 
        "rag_backup.py": "백업"
    }
    
    file_status = {}
    
    for script_name, display_name in script_files.items():
        script_path = project_root / script_name
        
        if script_path.exists():
            try:
                file_size = script_path.stat().st_size
                if file_size > 0:
                    file_status[display_name] = {
                        'exists': True,
                        'size': file_size,
                        'readable': os.access(script_path, os.R_OK),
                        'path': str(script_path)
                    }
                else:
                    file_status[display_name] = {
                        'exists': False,
                        'error': '빈 파일'
                    }
            except Exception as e:
                file_status[display_name] = {
                    'exists': False,
                    'error': f'파일 검사 실패: {str(e)}'
                }
        else:
            file_status[display_name] = {
                'exists': False,
                'error': '파일 없음'
            }
    
    return file_status

def run_management_task_with_status(task_name):
    """상태를 업데이트하는 관리 작업 실행"""
    
    def log_mgmt(log_type, message):
        try:
            log_message("FAILURE", f"RAG 초기화 실패: {e}", "APP")
        except:
            print(f"[MANAGEMENT] {message}")
    
    # 작업 시작 상태로 변경
    st.session_state.management_tasks[task_name]['status'] = 'running'
    st.session_state.management_tasks[task_name]['last_run'] = datetime.now()
    
    try:
        log_mgmt("progress", f"{task_name} 시작...")
        
        script_map = {
            "벡터 재생성": ("reindex_upstage_docx.py", 3600),
            "BM25 재생성": ("pipeline_bm25_from_docx.py", 1800), 
            "백업": ("rag_backup.py", 300)
        }
        
        if task_name not in script_map:
            raise ValueError(f"알 수 없는 작업: {task_name}")
        
        script_name, timeout = script_map[task_name]
        script_path = project_root / script_name
        
        if not script_path.exists():
            raise FileNotFoundError(f"스크립트 파일이 존재하지 않음: {script_name}")
        
        # 실행할 명령어 로그에 출력
        command = [sys.executable, str(script_path)]
        log_mgmt("info", f"실행 명령: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=project_root
        )
        
        # 표준 출력 로그에 추가
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    log_mgmt("info", f"[STDOUT] {line}")
        
        # 표준 에러 로그에 추가
        if result.stderr:
            for line in result.stderr.strip().split('\n'):
                if line.strip():
                    log_mgmt("warning", f"[STDERR] {line}")
        
        if result.returncode == 0:
            st.session_state.management_tasks[task_name]['status'] = 'completed'
            log_mgmt("success", f"{task_name} 완료")
        else:
            st.session_state.management_tasks[task_name]['status'] = 'failed'
            log_mgmt("failure", f"{task_name} 실패: return code {result.returncode}")
        
    except subprocess.TimeoutExpired:
        st.session_state.management_tasks[task_name]['status'] = 'failed'
        log_mgmt("failure", f"{task_name} 타임아웃 ({timeout}초 초과)")
    except FileNotFoundError as e:
        st.session_state.management_tasks[task_name]['status'] = 'failed'
        log_mgmt("failure", f"{task_name} 스크립트 파일 없음: {str(e)}")
    except Exception as e:
        st.session_state.management_tasks[task_name]['status'] = 'failed'
        log_mgmt("failure", f"{task_name} 오류: {e}")

def create_management_interface():
    """개선된 관리 도구 인터페이스 - 로그 크기 제한 제거"""
    
    management_tasks = [
        ("벡터 재생성", "벡터 데이터베이스 재생성", 
         ["DOCX 문서 -> 벡터 임베딩 -> Pinecone 업로드", "시간: 약 30분 ~ 2시간"],
         "primary"),
        ("BM25 재생성", "BM25 검색 인덱스 재생성",
         ["DOCX 문서 -> 텍스트 추출 -> BM25 인덱스", "시간: 약 10분 ~ 30분"], 
         "secondary"),
        ("백업", "프로젝트 백업",
         ["모든 .py 파일 압축 -> backup 폴더에 저장", "시간: 약 10초 ~ 1분"],
         "secondary")
    ]
    
    # 실행 파일 상태 확인
    file_status = check_script_files()
    task_names = ["벡터 재생성", "BM25 재생성", "백업"]
    
    button_cols = st.columns(3)
    
    for i, (task_name, subtitle, desc_lines, btn_type) in enumerate(management_tasks):
        with button_cols[i]:
            st.markdown(f"#### {task_name}")
            st.markdown(f"**{subtitle}**")
            
            for line in desc_lines:
                st.markdown(f"- {line}")
            
            # 작업 상태에 따른 버튼 텍스트와 활성화 상태
            task_status = st.session_state.management_tasks[task_name]['status']
            file_exists = file_status[task_name]['exists']
            
            if not file_exists:
                btn_text = f"[파일 없음] {task_name}"
                btn_disabled = True
                btn_type = "secondary"
            elif task_status == 'running':
                btn_text = f"[실행 중...] {task_name}"
                btn_disabled = True
                btn_type = "secondary"
            elif task_status == 'completed':
                last_run = st.session_state.management_tasks[task_name]['last_run']
                if last_run:
                    time_str = last_run.strftime("%H:%M")
                    btn_text = f"[완료 {time_str}] {task_name} 재실행"
                else:
                    btn_text = f"[완료] {task_name} 재실행"
                btn_disabled = False
                btn_type = "success"
            elif task_status == 'failed':
                btn_text = f"[실패] {task_name} 재시도"
                btn_disabled = False
                btn_type = "secondary"
            else:  # ready
                btn_text = f"{task_name} 시작"
                btn_disabled = False
            
            if st.button(btn_text, type=btn_type, key=f"{task_name}_btn", 
                        disabled=btn_disabled, use_container_width=True):
                handle_management_button(task_name)
            
            # 각 버튼 바로 아래에 파일명과 상태 표시
            script_files_map = {
                "벡터 재생성": "reindex_upstage_docx.py",
                "BM25 재생성": "pipeline_bm25_from_docx.py", 
                "백업": "rag_backup.py"
            }
            
            script_file = script_files_map[task_name]
            
            if file_status[task_name]['exists']:
                size_mb = file_status[task_name]['size'] / 1024 / 1024
                status_text = f"{script_file}: 파일존재 {size_mb:.2f}MB"
            else:
                error_msg = file_status[task_name].get('error', '파일없음')
                status_text = f"{script_file}: {error_msg}"
            
            st.markdown(
                f"<div style='text-align: center; color: #666; font-size: 0.8em; margin-top: -5px;'>"
                f"({status_text})"
                f"</div>", 
                unsafe_allow_html=True
            )
    
    st.markdown("---")
    
    # 관리 로그 (제목과 초기화 버튼) 
    col1, col2 = st.columns([7, 1])
    
    with col1:
        st.markdown("#### 관리 로그")
    
    with col2:
        if st.button("로그 초기화", key=f"clear_logs_{st.session_state.session_id}"):
            # 로그 초기화 및 작업 상태 리셋
            for log_key in ['correct_process_logs', 'incorrect_process_logs', 'mgmt_logs']:
                st.session_state[log_key] = []
            
            # 관리 작업 상태도 리셋
            for task_name in st.session_state.management_tasks:
                st.session_state.management_tasks[task_name] = {'status': 'ready', 'last_run': None}
            
            st.success("로그와 작업 상태가 초기화되었습니다.")
            time.sleep(1)
            st.rerun()
    
    try:
        # *** 크기 제한 제거 - [-50:] 삭제 ***
        mgmt_logs = st.session_state.mgmt_logs  # [-50:] 제거
        log_text = "\n".join([str(log) for log in mgmt_logs]) if mgmt_logs else "관리 로그가 없습니다."
    except:
        log_text = "관리 로그가 없습니다."
    
    st.text_area("관리 로그 내용", value=log_text, height=400, 
                key=f"management_logs_{st.session_state.session_id}", 
                label_visibility="hidden")

def run_management_task_safe(task_name):
    """관리 작업 스레드 시작"""
    thread = create_safe_thread(
        target_func=run_management_task_with_status,
        args=(task_name,),
        name=f"mgmt_{task_name.replace(' ', '_')}"
    )
    thread.start()

def start_evaluation_thread_safe(excel_file, mcq_limit, short_limit):
    """평가 스레드 시작"""
    st.session_state.evaluation_running = True
    st.session_state.evaluation_completed = False
    reset_evaluation_state()
    
    thread = create_safe_thread(
        target_func=run_evaluation_task,
        args=(excel_file, mcq_limit, short_limit),
        name="evaluation_thread"
    )
    thread.start()
    return thread

# ========== UI 설정 및 스타일링 ==========
st.set_page_config(page_title="통합 RAG 시스템", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .element-container { margin-bottom: 0rem !important; }
    .stTextArea { margin-top: 0rem !important; }
    
    /* Streamlit 앱 전체를 화면 맨 위로 */
    .main {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }

    /* 뷰포트 상단에 완전히 붙이기 */
    body {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }

    /* 브라우저 기본 마진 제거 */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== UI 핸들러 함수들 ==========
def create_evaluation_controls():
    """평가 시스템 컨트롤 패널"""
    col_title, col_settings = st.columns([1, 2])
    
    with col_title:
        st.markdown("# 평가 시스템")
        st.caption("RAG 시스템 성능 평가 도구")
        
        if st.session_state.evaluation_running:
            if st.button("평가 중지", type="secondary", key="eval_stop", use_container_width=True):
                st.session_state.evaluation_running = False
                st.session_state.evaluation_completed = False
                
        elif st.session_state.evaluation_completed:
            if st.button("새 평가 준비", type="secondary", key="eval_reset", use_container_width=True):
                reset_evaluation_state()
                st.session_state.evaluation_completed = False
                st.rerun()
                
        else:
            excel_files = get_excel_files()
            selected_file = st.session_state.get('selected_file')
            can_start = selected_file and excel_files
            
            if can_start:
                if st.button("평가 시작", type="primary", key="eval_start", use_container_width=True):
                    mcq_limit = st.session_state.get('mcq_limit', 50)
                    short_limit = st.session_state.get('short_limit', 50)
                    handle_evaluation_start(selected_file, mcq_limit, short_limit)
            else:
                st.button("평가 시작", type="primary", disabled=True, key="eval_disabled", use_container_width=True)
    
    with col_settings:
        create_evaluation_settings()

    # 평가 완료 후 저장된 파일 정보 표시
    if st.session_state.evaluation_completed and hasattr(st.session_state, 'last_saved_file'):
        st.success(f"평가 완료! 결과가 저장되었습니다: {st.session_state.last_saved_file}")
        
        # 파일 다운로드 버튼 추가 (선택사항)
        if os.path.exists(st.session_state.last_saved_file):
            with open(st.session_state.last_saved_file, 'rb') as file:
                st.download_button(
                    label="결과 파일 다운로드",
                    data=file.read(),
                    file_name=os.path.basename(st.session_state.last_saved_file),
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

def create_evaluation_settings():
    """평가 설정 패널 - 동적 최대값 및 기본값 적용"""
    st.write("")
    
    excel_files = get_excel_files()
    if not excel_files:
        st.error("루트 디렉토리에 Excel 파일이 없습니다.")
        return
    
    selected_file = st.selectbox(
        "평가할 Excel 파일", excel_files,
        help="루트 디렉토리의 Excel 파일 중 선택"
    )
    st.session_state.selected_file = selected_file
    
    # 세션 상태에서 실제 문제 수 가져오기
    mcq_max = getattr(st.session_state, 'detected_mcq_count', 10000)
    short_max = getattr(st.session_state, 'detected_short_count', 10000)
    
    col_mcq, col_short = st.columns(2)
    with col_mcq:
        mcq_limit = st.number_input(
            "선다형 최대 문제 수", 
            min_value=1, 
            max_value=mcq_max,
            value=mcq_max,  # 기본값을 실제 문제 수로 설정
            step=10
        )
        st.session_state.mcq_limit = mcq_limit
    
    with col_short:
        short_limit = st.number_input(
            "단답형 최대 문제 수", 
            min_value=1, 
            max_value=short_max,
            value=short_max,  # 기본값을 실제 문제 수로 설정
            step=10
        )
        st.session_state.short_limit = short_limit

def reset_evaluation_state():
    """평가 상태 초기화 - 배치 통계 초기화 추가"""
    reset_data = {
        'mcq_question_log': [],
        'short_question_log': [],
        'correct_process_logs': [],
        'incorrect_process_logs': [],
        'mcq_stats': {'correct': 0, 'total': 0},
        'short_stats': {'correct': 0, 'total': 0},
        'short_f1_total': 0.0,
        'evaluation_progress': {'current': 0, 'total': 0},
        'temp_question_logs': {},
        'current_question': None,
        
        # 배치 통계 초기화 (새로 추가)
        'mcq_current_batch_stats': {'correct': 0, 'total': 0, 'accuracy': 0.0},
        'short_current_batch_stats': {'correct': 0, 'total': 0, 'em_avg': 0.0, 'f1_avg': 0.0, 'f1_total': 0.0},
        
        # 오류 패턴 통계 초기화
        'mcq_error_patterns': {
            'choice_mapping': 0, 'context_quality': 0, 'search_failure': 0,
            'negative_detection': 0, 'llm_reasoning': 0
        },
        'short_error_patterns': {
            'context_mismatch': 0, 'extraction_failure': 0, 'low_bm25_score': 0,
            'no_search_results': 0, 'normalization_failure': 0
        },
        'search_quality_issues': 0,
        'performance_metrics': {
            'avg_mcq_time': 0.0, 'avg_short_time': 0.0,
            'total_time': 0.0, 'search_success_rate': 0.0
        }
    }
    
    for key, value in reset_data.items():
        st.session_state[key] = value

def create_chat_interface():
    """질의응답 인터페이스 생성"""
    st.markdown("### 금융 법령 질의응답")
    st.caption("AI 기반 법령 질의응답 시스템 (단답형)")
    
    if not get_rag_available():
        st.error("RAG 시스템을 사용할 수 없습니다. 모듈을 확인해주세요.")
        st.stop()
    
    display_chat_history()
    
    st.markdown("#### 새 질문")
    
    # 질문 입력창과 버튼들을 완전히 정렬 (세로 중앙 + 텍스트 중앙)
    st.markdown("""
    <style>
        /* 폼 컨테이너 정렬 */
        div[data-testid="stForm"] {
            display: flex;
            align-items: center;
        }
        
        /* 질문 레이블 숨기기 */
        div[data-testid="stForm"] div[data-testid="stTextInput"] label {
            display: none;
        }
        
        /* 입력창 세로 중앙 정렬 및 텍스트 중앙 */
        div[data-testid="stForm"] div[data-testid="stTextInput"] {
            display: flex;
            align-items: center;
        }
        
        div[data-testid="stForm"] div[data-testid="stTextInput"] input {
            height: 2.5rem;
            display: flex;
            align-items: center;
            text-align: left;
            vertical-align: middle;
            margin: 0;
            padding: 0 12px;
        }
        
        /* 버튼들 세로 중앙 정렬 */
        div[data-testid="stForm"] button {
            height: 2.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        
        /* 컬럼 내부 정렬 */
        div[data-testid="stForm"] > div > div {
            display: flex;
            align-items: center;
            height: 2.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form(key="question_form", clear_on_submit=True):
        col_input, col_question, col_clear = st.columns([6, 1, 1])
        
        with col_input:
            question = st.text_input(
                "질문", 
                placeholder="예: 은행법 제1조의 목적은 무엇인가요?",
                label_visibility="hidden"
            )
        
        with col_question:
            ask_button = st.form_submit_button("질문", use_container_width=True)
            
        with col_clear:
            clear_button = st.form_submit_button("초기화", use_container_width=True)
    
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()
    
    if ask_button and question.strip():
        process_question(question)
    elif ask_button:
        st.warning("질문을 입력해주세요")

def process_question(question):
    """질문 처리 로직"""
    with st.spinner("검색 중..."):
        try:
            contexts = retrieve(question, top_k=5)
        except Exception as e:
            st.error(f"검색 오류: {e}")
            return
    
    if not contexts:
        answer = "죄송합니다. 관련 문서를 찾을 수 없습니다."
    else:
        with st.spinner("답변 생성 중..."):
            try:
                answer = generate_answer_short(question, contexts)
                answer = format_answer_for_chat(question, answer)
            except Exception as e:
                answer = f"답변 생성 중 오류가 발생했습니다: {e}"
    
    add_to_chat_history(question, answer, contexts)
    st.rerun()

def create_log_display():
    """정답/오답 로그 표시 - 크기 제한 제거"""
    
    # 극도로 간격 제거하는 CSS
    st.markdown("""
    <style>
        .log-title {
            font-weight: bold;
            margin: 0px 0px 2px 0px !important;
            padding: 2px 0px !important;
            border-bottom: 1px solid #e0e0e0;
            line-height: 1.2;
        }
        
        /* 제목 다음 텍스트 영역의 마진 완전 제거 */
        .log-title + div[data-testid="stTextArea"] {
            margin-top: -15px !important;
        }
        
        /* 텍스트 영역 자체의 마진/패딩 제거 */
        .stTextArea {
            margin-top: 0px !important;
            margin-bottom: 0px !important;
        }
        
        /* 컬럼 간격도 줄이기 */
        .stColumns > div {
            padding-left: 0.25rem !important;
            padding-right: 0.25rem !important;
        }
        
        /* 모든 요소의 마진 강제 제거 */
        .element-container {
            margin-bottom: 0px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    log_col1, log_col2 = st.columns(2)
    
    with log_col1:
        st.markdown('<div class="log-title">정답 처리과정 로그</div>', 
                   unsafe_allow_html=True)
        try:
            # *** 크기 제한 제거 - [-100:] 삭제 ***
            logs = st.session_state.correct_process_logs  # [-100:] 제거
            text = "\n".join([str(log) for log in logs]) if logs else "정답 처리과정 대기 중..."
        except:
            text = "정답 처리과정 대기 중..."
        
        st.text_area("정답 로그", value=text, height=300,
                    key="correct_logs_unified", label_visibility="hidden")
    
    with log_col2:
        st.markdown('<div class="log-title">오답 처리과정 로그</div>', 
                   unsafe_allow_html=True)
        try:
            # *** 크기 제한 제거 - 기존 [-100:] 제거 ***
            logs = st.session_state.incorrect_process_logs if st.session_state.incorrect_process_logs else []
            text = "\n".join([str(log) for log in logs]) if logs else "오답 처리과정 대기 중..."
        except:
            text = "오답 처리과정 대기 중..."
        
        st.text_area("오답 로그", value=text, height=300,
                    key="incorrect_logs_unified", label_visibility="hidden")

def handle_evaluation_start(selected_file, mcq_limit, short_limit):
    # 평가 시작 전 강제 세션 리셋
    st.session_state.mcq_stats = {'correct': 0, 'total': 0}
    st.session_state.short_stats = {'correct': 0, 'total': 0}
    st.session_state.short_f1_total = 0.0

    """평가 시작 처리"""
    if not selected_file:
        st.error("파일을 선택해주세요.")
        return
    
    try:
        start_evaluation_thread_safe(selected_file, mcq_limit, short_limit)
        st.rerun()
    except Exception as e:
        st.session_state.evaluation_running = False
        st.error(f"평가 시작 실패: {e}")

def handle_management_button(task_name):
    """관리 도구 버튼 처리"""
    try:
        run_management_task_safe(task_name)
        st.success(f"{task_name}이 시작되었습니다. 진행 상황은 로그를 확인하세요.")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"{task_name} 시작 실패: {e}")

# ========== 메인 UI 라우팅 ==========
st.sidebar.title("금융법령 RAG 시스템")
st.sidebar.markdown("---")

tab_selection = st.sidebar.radio(
    "기능 선택",
    ["질의응답", "평가 시스템", "관리 도구"],
    index=0,
    key=f"nav_{st.session_state.session_id}"
)

if tab_selection == "질의응답":
    create_chat_interface()

elif tab_selection == "평가 시스템":
    if not get_rag_available():
        st.error("RAG 시스템을 사용할 수 없습니다.")
        st.stop()
    
    create_evaluation_controls()
    
    st.markdown("#### 실시간 문제 처리 현황")
    display_real_time_monitoring()
    
    create_log_display()
    
    if st.session_state.evaluation_running:
        time.sleep(1.5)
        st.rerun()

elif tab_selection == "관리 도구":
    create_management_interface()

# 푸터
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666; font-size: 0.8em;'>"
    f"금융법령 통합 RAG 시스템 v3.2 | 현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    f"</div>",
    unsafe_allow_html=True
)