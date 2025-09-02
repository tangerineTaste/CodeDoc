"""
llm_bridge.py - 후처리 추가 완화 및 질문 유형 자동 감지
"""
import json
import time
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
# import 부분에 parse_mcq_answer 추가
from rag.utils import log_message, detect_negative_question, detect_answer_type_from_question, parse_mcq_answer

# 기존 log_message 함수 전체 삭제 (15줄 정도)

class HybridLLM:
    """개선된 LLM Bridge - MCQ 파싱 연동 + 단답형 후처리 대폭 완화"""
    
    def __init__(self, config, silent=False):
        if not silent:
            log_message("INFO", "LLM Bridge 초기화 중...", "LLM")
        self.config = config
        self._init_llms()
        self._init_prompts()
        
        log_message("SUCCESS", "LLM Bridge 초기화 완료", "LLM")

    def _init_llms(self):
        """LLM 초기화"""
        self.clients = {}
        
        # OpenAI 초기화
        if self.config.openai_api_key:
            try:
                import openai
                self.clients['openai'] = openai.OpenAI(
                    api_key=self.config.openai_api_key,
                    timeout=self.config.llm_timeout
                )
                log_message("SUCCESS", "OpenAI 초기화 완료", "LLM")
            except Exception as e:
                log_message("FAILURE", f"OpenAI 초기화 실패: {e}", "LLM")
        
        # Upstage 초기화
        if self.config.upstage_api_key:
            try:
                import openai
                self.clients['upstage'] = openai.OpenAI(
                    api_key=self.config.upstage_api_key,
                    base_url="https://api.upstage.ai/v1",
                    timeout=self.config.llm_timeout
                )
                log_message("SUCCESS", "Upstage 초기화 완료", "LLM")
            except Exception as e:
                log_message("FAILURE", f"Upstage 초기화 실패: {e}", "LLM")
        
        if not self.clients:
            log_message("FAILURE", "사용 가능한 LLM이 없음", "LLM")

    # 나머지 메서드들도 동일하게 수정...

    def _init_prompts(self):
        """프롬프트 시스템 초기화"""
        self.prompts = {
            # MCQ용 프롬프트
            'mcq_system': """한국 법령 전문가로서 주어진 컨텍스트에서 정답을 선택.

**필수 검증 절차:**
1. 각 선택지를 컨텍스트와 비교하여 선택지의 언급 여부 확인
2. 질문의 정답인 선택지를 선택
3. 컨텍스트에 근거가 있는지 확인

**핵심 원칙:**
- 컨텍스트에 없는 내용 선택 금지
- 추측 금지
- 정답과 가장 유사하고, 근거가 있는 선택지 선택

최종 답변은 반드시 선택지에 명시된 A, B, C, D 혹은 1, 2, 3, 4 중 하나만 출력.
- 설명, 이유, 추론 과정은 절대 포함 금지
- 정보 부족을 답하려면, 컨텍스트와 무관하게 스스로 질문의 답을 찾으시오.""",

            # 부정형용 프롬프트
            'mcq_negative': """한국 법령 전문가로서 주어진 컨텍스트에서 부정형 질문의 정답을 선택.

**핵심 원칙:**
- 부정형 질문에서는 컨텍스트에 명시되지 않은 선택지가 부정형 질문의 정답일 가능성이 큼.
- 각 선택지를 컨텍스트와 대조하여 언급되지 않은 가장 상관이 없는것을 선택.

최종 답변은 반드시 선택지에 명시된 A, B, C, D 혹은 1, 2, 3, 4 중 하나만 출력.
- 설명, 이유, 추론 과정은 절대 포함 금지
- 정보 부족을 답하려면, 컨텍스트와 무관하게 스스로 질문의 답을 찾으시오.""",

            'mcq_user': """컨텍스트:
{context}

질문: {question}

선택지:
A 혹은 1) {choice_a}
B 혹은 2) {choice_b}
C 혹은 3) {choice_c}
D 혹은 4) {choice_d}

답:선택지중 정답 하나를 선택""",

            # 단답형용 프롬프트 (대폭 완화)
            'short_system': """법령 문서에서 질문의 정답을 추출하시오.

**추출 방법:**
1. 컨텍스트에서 관련 문장을 찾으세요
2. 그 문장에서 질문의 정답 부분만 추출
3. 정답에 근접한 8단어 이하의 단어 혹은 구문 이외의 불필요한 설명은 제외

**질문 유형별 답변:**
▶ 정의 질문 ("~란", "~이란", "정의"): 정의 내용만
▶ 개수 질문 ("몇 명", "몇 개"): 숫자+단위만  
▶ 담당자 질문 ("누가", "담당"): 기관명/직책명만
▶ 기간 질문 ("언제", "기간"): 날짜/기간만
▶ 조문 내용 질문 ("제X조에서 정하는"): 조문이 규정하는 구체적 내용

**추출 원칙:**
- 질문과 관련된 모든 정보를 포함하되,
- 너무 엄격하게 잘라서 정답 부분을 잃지 않게하고,
- 질문 의도에 충실하게 의미가 통하도록 완전한 표현을 사용해서

질문에 대한 정답 부분을 추출하시오.
- "정답은", "따라서", "즉" 같은 불필요한 접두어 금지, 설명이나 추론 과정 절대 포함 금지
- 정보 부족을 답하려면, 컨텍스트와 무관하게 스스로 질문의 답을 찾으시오.""",

            'short_user': """컨텍스트:
{context}

질문: {question}

위 질문의 정답을 컨텍스트에서 추출, 실패시 스스로 정답을 제시하시오.:"""
        }

    def call_mcq(self, question: str, choices: Dict[str, str], context: str) -> str:
        """MCQ 처리 - utils.parse_mcq_answer 단일 사용"""
        log_message("INFO", "MCQ 처리 시작", "LLM")
        
        # 입력 데이터 검증
        if not context or len(context.strip()) < 10:
            log_message("FAILURE", "MCQ 컨텍스트가 너무 짧음 또는 비어있음", "LLM")
        
        if len(choices) != 4:
            log_message("FAILURE", f"MCQ 선택지 개수 이상 - {len(choices)}개 (예상: 4개)", "LLM")
        
        # 부정형 질문 감지
        is_negative = detect_negative_question(question)
        
        # 프롬프트 선택
        if is_negative:
            system_prompt = self.prompts['mcq_negative']
            log_message("INFO", "부정형 질문으로 감지 - 특수 프롬프트 사용", "LLM")
        else:
            system_prompt = self.prompts['mcq_system']
        
        user_prompt = self.prompts['mcq_user'].format(
            context=context,
            question=question,
            choice_a=choices.get('A', ''),
            choice_b=choices.get('B', ''),
            choice_c=choices.get('C', ''),
            choice_d=choices.get('D', '')
        )
        
        try:
            response = self._call_llm(system_prompt, user_prompt)
            
            # *** 자체 파싱 로직 제거, utils.parse_mcq_answer만 사용 ***
            if not response or len(response.strip()) == 0:
                log_message("FAILURE", "LLM이 빈 응답 반환", "LLM")
                return "A"  # 기본값
            
            # utils.py의 표준 파싱 함수만 사용
            parsed_answer = parse_mcq_answer(response, expected_format='alphabet')
            
            log_message("SUCCESS", f"MCQ 파싱 완료: '{response.strip()}' → '{parsed_answer}'", "LLM")
            return parsed_answer
            
        except Exception as e:
            log_message("FAILURE", f"MCQ 처리 오류: {e}", "LLM")
            import traceback
            log_message("FAILURE", f"MCQ 오류 상세: {traceback.format_exc()}", "LLM")
            return "E"

    def call_short(self, question: str, context: str) -> str:
        """단답형 처리 - 대폭 완화된 후처리"""
        log_message("INFO", "단답형 처리 시작", "LLM")
        
        if not context or len(context.strip()) < 20:
            log_message("FAILURE", "단답형 컨텍스트 부족으로 처리 불가", "LLM")
            return "정보 부족"
        
        # 컨텍스트 품질 검증 (경고만 출력, 중단하지 않음)
        if len(context) > 5000:
            log_message("INFO", f"단답형 컨텍스트가 매우 김 - {len(context)}자", "LLM")
        elif len(context) < 100:
            log_message("INFO", f"단답형 컨텍스트가 짧음 - {len(context)}자", "LLM")
        
        # 질문 유형 감지 - utils 함수 사용
        question_type = detect_answer_type_from_question(question)  # utils에서 import
        log_message("INFO", f"감지된 질문 유형: {question_type}", "LLM")
        
        system_prompt = self.prompts['short_system']
        user_prompt = self.prompts['short_user'].format(
            context=context,
            question=question
        )
        
        try:
            response = self._call_llm(system_prompt, user_prompt)
            
            # 응답 품질 검증 (완화)
            if not response:
                log_message("FAILURE", "LLM이 빈 응답 반환", "LLM")
                return "정보 부족"
            
            if not self._validate_response_ultra_relaxed(response):
                log_message("INFO", f"단답형 응답 검증 실패 (완화 모드) - '{response[:30]}...'", "LLM")
            
            processed = self._post_process_response_ultra_relaxed(response, question, question_type)
            
            # 후처리 결과 검증
            if processed != response:
                log_message("INFO", f"단답형 후처리: '{response[:20]}...' → '{processed}'", "LLM")
            
            log_message("SUCCESS", f"단답형 처리 완료: '{processed}'", "LLM")
            return processed
            
        except Exception as e:
            log_message("FAILURE", f"단답형 처리 오류: {e}", "LLM")
            import traceback
            log_message("FAILURE", f"단답형 오류 상세: {traceback.format_exc()}", "LLM")
            return "처리 실패"

    def _post_process_response_ultra_relaxed(self, response: str, question: str, question_type: str) -> str:
        """답변 후처리 - 핵심 정보 손실 방지"""
        if not response:
            return "정보 부족"
        
        response = response.strip()
        
        # "정보 부족"은 그대로 반환
        if "정보 부족" in response or "처리 실패" in response:
            return response
        
        # *** 1. 질문 유형별 핵심 패턴 우선 추출 (새로운 로직) ***
        
        # 조문 질문
        if question_type == 'article':
            article_patterns = [
                r'제\s*\d+\s*조(?:제\s*\d+\s*항)?(?:제\s*\d+\s*호)?',
                r'제(\d+)조',
                r'(\d+)조',
                r'제\s*(\d+)\s*조'
            ]
            for pattern in article_patterns:
                match = re.search(pattern, response)
                if match:
                    if '제' in match.group():
                        return match.group().replace(" ", "")
                    else:
                        return f"제{match.group(1)}조"
        
        # 기관명 질문 (강화)
        elif question_type == 'agency':
            # 기관명+직책 조합 우선 
            agency_patterns = [
                r'([가-힣]+(?:위원회|청|부|처|원))(?:\s*(?:장관|위원장|청장|원장))',
                r'([가-힣]+장관)',
                r'([가-힣]+위원장)', 
                r'([가-힣]+(?:위원회|청|부|처|원))',
                # 약어 포함
                r'(금위|금감원|공정위|방통위|중기부|기재부)',
            ]
            
            for pattern in agency_patterns:
                match = re.search(pattern, response)
                if match:
                    result = match.group().strip()
                    # 약어를 정식명칭으로 변환
                    agency_map = {
                        "금위": "금융위원회", "금감원": "금융감독원",
                        "공정위": "공정거래위원회", "방통위": "방송통신위원회", 
                        "중기부": "중소벤처기업부", "기재부": "기획재정부"
                    }
                    return agency_map.get(result, result)
        
        # 금액/기간/개수 질문에서 "100명 이상" → "이상" 문제 해결
        if any(keyword in question for keyword in ['금액', '원', '기간', '일', '개월', '년', '몇', '수는']):
            # 숫자+단위+수식어 완전 패턴
            complete_patterns = [
                r'\d+(?:,\d+)*(?:억|만|천)?\s*원(?:\s*(?:이상|이하|미만))?',  # 금액
                r'\d+\s*(?:년|개월|일)(?:\s*(?:이내|이상|미만|전|후))?',      # 기간
                r'\d+\s*(?:명|개|인)(?:\s*(?:이상|이하|미만))?',            # 개수
            ]
            
            for pattern in complete_patterns:
                match = re.search(pattern, response)
                if match:
                    return match.group().replace(" ", "")  # 완전한 표현 반환
        
        # 서식 질문 (강화) 
        elif question_type == 'form':
            form_patterns = [
                r'별지\s*제\s*\d+\s*호(?:서식|양식)?',
                r'제\s*\d+\s*호\s*(?:서식|양식)',
                r'서식\s*\d+', r'양식\s*\d+',
                r'별지(\d+)호', r'(\d+)호서식'
            ]
            
            for pattern in form_patterns:
                match = re.search(pattern, response)
                if match:
                    if '별지' in match.group():
                        return match.group().replace(" ", "")
                    elif match.groups():
                        return f"별지 제{match.group(1)}호서식"
                    else:
                        return match.group().replace(" ", "")
        
        # *** 2. 기존 일반 후처리 로직 (패턴 추출 실패 시) ***
        
        # 2-1. 불필요한 접두어 제거 (기존과 동일하지만 완화)
        unnecessary_prefixes = [
            "답변:", "답:", "정답:", "결론:", "따라서", "그러므로", "추출:", "결과:", "정답은",
            "답은", "질문에 대한", "위 질문의", "해당", "관련", "구체적으로", "정확히는",
            "즉,", "바로", "다시 말해", "요약하면", "결국", "최종적으로", "정리하면",
            "Answer:", "ANS:", "ANSWER:", "정답:", "답변은", "결과는", "해답은"
        ]
        
        for prefix in unnecessary_prefixes:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
            response = re.sub(f"^{re.escape(prefix)}", "", response).strip()
        
        # 2-2. 따옴표 제거
        if (response.startswith('"') and response.endswith('"')) or \
        (response.startswith("'") and response.endswith("'")):
            response = response[1:-1].strip()
        
        # 2-3. 일반적인 법령 패턴 추출 (fallback)
        high_priority_patterns = [
            r'제\d+조', r'[가-힣]+(?:위원회|청|부|처|원)',
            r'\d+(?:년|개월|일)', r'\d+(?:억|만)?원',
            r'별지\s*제\s*\d+\s*호서식', r'[가-힣]{2,}'
        ]
        
        extracted_terms = []
        for pattern in high_priority_patterns:
            matches = re.findall(pattern, response)
            extracted_terms.extend(matches[:2])
            if len(extracted_terms) >= 3:
                break
        
        if extracted_terms:
            unique_terms = list(dict.fromkeys(extracted_terms))
            response = " ".join(unique_terms[:2])  # 최대 2개 term
        
        # 2-4. 불필요한 접미어 제거
        suffix_patterns = [
            r'(?:라\s*한다|를\s*말한다|에\s*따라|로\s*정한다|고\s*한다)',
            r'(?:이다|이며|이고|하다|한다|함)', r'[.!?]+'
        ]
        
        for pattern in suffix_patterns:
            response = re.sub(pattern, '', response)
        
        # 2-5. 최종 검증 및 반환
        response = response.strip()
        
        # 빈 응답 처리
        if len(response) == 0:
            return "정보 부족"
        
        # 의미없는 단답 처리 (완화)
        meaningless_words = ["다음", "해당", "관련", "기타", "등", "바"]
        if response in meaningless_words:
            return "정보 부족"
        
        # 너무 긴 응답 자르기 (80 → 100자로 완화)
        if len(response) > 100:
            response = response[:97] + "..."
        
        return response if response else "정보 부족"

    def _validate_response_ultra_relaxed(self, response: str) -> bool:
        """응답 품질 검증 - 대폭 완화된 기준 (extraction_failure 완화)"""
        if not response or len(response.strip()) == 0:
            return False
        
        response = response.strip()
        
        # "정보 부족"은 유효한 응답으로 간주
        if "정보 부족" in response:
            return True
        
        # *** 완화: 1글자도 허용 (기존 2글자→1글자) ***
        if len(response) < 1:
            return False
        
        # *** 완화: 법령 패턴 포함시 매우 짧아도 유효 ***
        if re.search(r'제\d+조|위원회|청|부|처|원|\d+(?:년|개월|일|원)', response):
            return True
        
        # *** 완화: 의미없는 패턴들도 더 관대하게 ***
        meaningless_patterns = [
            r'^[가-힣]{1}$',              # 1글자 단답도 허용
            r'^[가-힣]로$',               # "~로"로 끝나는 불완전한 답 허용
            r'^[가-힣]부$',               # "~부"만 있는 경우 허용  
            r'^[가-힣]에$',               # "~에"로 끝나는 불완전한 답 허용
        ]
        
        # 패턴 매칭 검사 (완화)
        for pattern in meaningless_patterns:
            if re.match(pattern, response):
                # *** 완화: 법령 패턴 포함시 예외 허용 ***
                if re.search(r'제\d+조|위원회|청|부|처|원|\d+(?:년|개월|일|원)', response):
                    return True
                # 단순한 1글자도 허용 (대폭 완화)
                return True
        
        # 반복 문자 패턴 거부 (기존과 동일)
        if len(set(response)) == 1 and len(response) > 1:
            return False
        
        # *** 완화: 숫자만으로 이루어진 경우 더 관대하게 ***
        if re.match(r'^\d+$', response):
            # 조문 번호로 보이는 경우는 허용 (1-3000 범위로 확장)
            try:
                num = int(response)
                if 1 <= num <= 3000:  # 2000 → 3000으로 확장
                    return True
                else:
                    return False
            except ValueError:
                return False
        
        # 영어만 있는 경우 거부
        if re.match(r'^[A-Za-z\s]+$', response):
            return False
        
        # 특수문자만 있는 경우 거부
        if re.match(r'^[^\w\s가-힣]+$', response):
            return False
        
        # *** 완화: 의미있는 법령 용어가 포함되어 있는지 검사 (기준 완화) ***
        meaningful_patterns = [
            r'제\d+조',                   # 조문 번호
            r'\d+(?:년|개월|일)',         # 기간
            r'\d+(?:억|만)?원',           # 금액
            r'[가-힣]+(?:위원회|청|부|처|원)', # 기관명
            r'별지\s*제\s*\d+\s*호',      # 서식
            r'[가-힣]{1,}',               # 1글자 이상 한글 (기존 2글자→1글자로 완화)
        ]
        
        # 의미있는 패턴이 하나라도 있으면 유효
        for pattern in meaningful_patterns:
            if re.search(pattern, response):
                return True
        
        # 여기까지 왔으면 의미있는 내용이 없는 것으로 판단하지만, 대폭 완화로 True 반환
        return True  # *** 완화: 거의 모든 응답 허용 ***

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """LLM 호출 - 우선순위 기반 + 향상된 오류 처리"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 사용 가능한 클라이언트가 있는지 확인
        if not self.clients:
            log_message("FAILURE", "사용 가능한 LLM 클라이언트가 없음")
            raise RuntimeError("LLM 서비스를 사용할 수 없습니다")
        
        # OpenAI 우선 시도
        if 'openai' in self.clients:
            try:
                result = self._call_openai(messages)
                log_message("SUCCESS", "OpenAI 호출 성공")
                return result
            except Exception as e:
                error_msg = str(e)
                # 구체적인 오류 유형 로깅
                if "rate_limit" in error_msg.lower():
                    log_message("FAILURE", f"OpenAI 요청 한도 초과: {e}")
                elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                    log_message("FAILURE", f"OpenAI 인증 오류: {e}")
                elif "timeout" in error_msg.lower():
                    log_message("FAILURE", f"OpenAI 타임아웃: {e}")
                else:
                    log_message("FAILURE", f"OpenAI 호출 실패: {e}")
        
        # Upstage 대안
        if 'upstage' in self.clients:
            try:
                result = self._call_upstage(messages)
                log_message("SUCCESS", "Upstage 호출 성공")
                return result
            except Exception as e:
                error_msg = str(e)
                # 구체적인 오류 유형 로깅
                if "rate_limit" in error_msg.lower():
                    log_message("FAILURE", f"Upstage 요청 한도 초과: {e}")
                elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                    log_message("FAILURE", f"Upstage 인증 오류: {e}")
                elif "timeout" in error_msg.lower():
                    log_message("FAILURE", f"Upstage 타임아웃: {e}")
                else:
                    log_message("FAILURE", f"Upstage 호출 실패: {e}")
        
        # 모든 서비스 실패
        log_message("FAILURE", "모든 LLM 서비스 호출 실패")
        
        # 사용 가능한 서비스 목록 로깅
        available_services = list(self.clients.keys())
        log_message("FAILURE", f"시도한 서비스: {', '.join(available_services)}")
        
        raise RuntimeError("모든 LLM 서비스 사용 불가")

    def _call_openai(self, messages: List[Dict]) -> str:
        """OpenAI API 호출 - 향상된 오류 처리"""
        try:
            response = self.clients['openai'].chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.0,
                max_tokens=self.config.max_tokens
            )
            
            # 응답 내용 검증
            if not response.choices or not response.choices[0].message:
                raise ValueError("OpenAI 응답이 비어있음")
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("OpenAI 응답 내용이 None")
            
            return content.strip()
            
        except Exception as e:
            # OpenAI 특정 오류들을 더 구체적으로 처리
            error_type = type(e).__name__
            log_message("FAILURE", f"OpenAI API 오류 ({error_type}): {e}")
            raise

    def _call_upstage(self, messages: List[Dict]) -> str:
        """Upstage API 호출 - 향상된 오류 처리"""
        try:
            response = self.clients['upstage'].chat.completions.create(
                model="solar-mini",
                messages=messages,
                temperature=0.0,
                max_tokens=self.config.max_tokens
            )
            
            # 응답 내용 검증
            if not response.choices or not response.choices[0].message:
                raise ValueError("Upstage 응답이 비어있음")
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Upstage 응답 내용이 None")
            
            return content.strip()
            
        except Exception as e:
            # Upstage 특정 오류들을 더 구체적으로 처리
            error_type = type(e).__name__
            log_message("FAILURE", f"Upstage API 오류 ({error_type}): {e}")
            raise