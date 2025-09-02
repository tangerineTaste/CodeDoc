# 통합 RAG 시스템 완전 매뉴얼

## 1. 시스템 개요

본 프로젝트는 금융/법령 문서(.docx)를 기반으로 한 **RAG(Retrieval-Augmented Generation)** 시스템입니다. BM25 키워드 검색과 Pinecone 벡터 검색을 결합한 하이브리드 검색으로 법령 질의응답과 성능 평가를 수행합니다.

### 시스템 아키텍처
```
DOCX 문서 → [인덱스 구축] → [하이브리드 검색] → [LLM 응답] → [평가] → [UI 관리]
```

## 2. 파일 구조 및 역할

### 2.1 데이터 처리 및 인덱싱 모듈
| 파일명 | 역할 | 주요 기능 |
|--------|------|-----------|
| `pipeline_bm25_from_docx.py` | BM25 인덱스 구축 | DOCX → 청킹 → BM25 인덱스 생성 |
| `reindex_upstage_docx.py` | Vector 인덱스 구축 | DOCX → Upstage 임베딩 → Pinecone 업서트 |
| `embedder_upstage.py` | 임베딩 API 래퍼 | Upstage API 호출, rate limiting |

### 2.2 검색 및 LLM 모듈
| 파일명 | 역할 | 주요 기능 |
|--------|------|-----------|
| `hybrid_retriever.py` | 하이브리드 검색기 | BM25 + Vector 검색 결합 |
| `llm_bridge.py` | LLM 호출 관리 | OpenAI/Upstage API, 프롬프트 관리 |

### 2.3 평가 모듈
| 파일명 | 역할 | 주요 기능 |
|--------|------|-----------|
| `evaluator.py` | 통합 평가기 | MCQ/Short Answer 평가, 오답 분석 |
| `evaluate.py` | 평가 실행 엔트리포인트 | CLI/웹 평가 실행 |
| `utils.py` | 공통 유틸리티 | MCQ 파싱, 정규화, EM/F1 계산 |

### 2.4 애플리케이션 및 관리 모듈
| 파일명 | 역할 | 주요 기능 |
|--------|------|-----------|
| `app.py` | Streamlit UI 애플리케이션 | 질의응답, 평가, 관리 도구 |
| `config.py` | 환경 설정 관리 | API 키, 인덱스, 시스템 검증 |

## 3. 단계별 상세 설명

### 3.1 인덱스 구축 단계

#### A. BM25 인덱스 구축 (pipeline_bm25_from_docx.py)

**목표**: DOCX 문서를 키워드 기반 검색이 가능한 BM25 인덱스로 변환

**주요 프로세스**:
```python
# 1. DOCX 파일 수집
iter_docx_files(root_dirs)  # 재귀적 .docx 탐색

# 2. 텍스트 추출 및 정규화
read_docx_text(path)        # DOCX → 텍스트
normalize_text(text)        # 제어문자, 공백 정리

# 3. 문장 분리 및 청킹
split_sentences(text)       # 문장 단위 분리
chunk_by_sentences(text, max_chars=800, overlap=80)  # 청킹

# 4. Corpus 생성
make_corpus_from_docx(files, chunk_size, overlap)

# 5. BM25 인덱스 생성
build_bm25(corpus, tokenizer)  # rank-bm25 기반
```

**출력**:
- `bm25.pkl`: BM25 인덱스 객체
- `law_chunks.parquet`: 청크 데이터

#### B. Vector 인덱스 구축 (reindex_upstage_docx.py)

**목표**: DOCX 문서를 의미 기반 검색이 가능한 벡터 인덱스로 변환

**핵심 클래스**:
```python
# 설정 관리
class ProcessingConfig:
    chunk_max_size: int = 1000      # 청크 최대 길이
    batch_size: int = 50            # 업서트 배치 크기
    upstage_models: List[str]       # 임베딩 모델 후보

# 법령 텍스트 정규화
class LegalTextPatterns:
    def normalize_text(text)        # 조문, 기관명 정규화
    def extract_article_number(text) # 조문 번호 추출

# 문서 청킹
class LegalDocumentChunker:
    def chunk_document(paragraphs)  # 적응적 청킹
    def _create_chunks_with_overlap(paragraphs, config) # 중첩 청킹

# 메타데이터 생성
class OptimizedMetadataGenerator:
    def create_vector_metadata(doc_id, title, law_info, chunk)
```

**출력**: Pinecone 벡터 DB에 업서트된 임베딩 + 메타데이터

### 3.2 검색 단계

#### A. 임베딩 생성 (embedder_upstage.py)

```python
class UpstageEmbedder:
    def embed_query(text: str) -> List[float]           # 단일 쿼리 임베딩
    def embed_documents(texts: List[str]) -> List[List[float]]  # 배치 임베딩
    def _rate_limit()                                   # API 호출 제한
```

#### B. 하이브리드 검색 (hybrid_retriever.py)

**목표**: BM25(키워드) + Vector(의미) 검색 결합으로 최적 검색 성능 확보

```python
class HybridRetriever:
    def search(query, question_type="general", top_k=None):
        # 1. BM25 검색
        bm25_results = self._bm25_search(query, top_k)
        
        # 2. Vector 검색
        vector_results = self._vector_search(query, top_k)
        
        # 3. 결과 병합
        merged_results = self._merge_results_enhanced(
            bm25_results, vector_results, 
            bm25_weight=0.3, vector_weight=0.7
        )
        
        # 4. 소스 다양성 확보
        return self._diversify_by_source_and_score(merged_results)
```

**특징**:
- 법령 특화 토크나이저 (`_enhanced_legal_tokenize`)
- BM25 실패 시 Vector fallback
- 질문 유형별 가중치 조정

### 3.3 LLM 응답 생성 단계 (llm_bridge.py)

**목표**: 검색된 컨텍스트 기반으로 정확한 답변 생성

```python
class HybridLLM:
    def call_mcq(question, choices, context):
        # 1. 부정형 질문 감지
        is_negative = detect_negative_question(question)
        
        # 2. 적절한 프롬프트 선택
        prompt = mcq_negative if is_negative else mcq_system
        
        # 3. LLM 호출
        response = self._call_llm(prompt, user_input)
        
        # 4. 응답 파싱
        return parse_mcq_answer(response)
    
    def call_short(question, context):
        # 1. 답변 유형 감지
        answer_type = detect_answer_type_from_question(question)
        
        # 2. LLM 호출
        response = self._call_llm(short_system, user_input)
        
        # 3. 후처리
        return self._post_process_response_ultra_relaxed(response, question)
```

**프롬프트 템플릿**:
- `mcq_system`: 일반 MCQ 질문
- `mcq_negative`: 부정형 MCQ 질문 ("~아닌 것은?")
- `short_system`: 단답형 질문

**후처리 기능**:
- 조문번호, 기관명, 금액, 기간 패턴 우선 추출
- 불필요한 설명 제거
- 응답 길이 제한 (100자)

### 3.4 평가 단계

#### A. 공통 유틸리티 (utils.py)

```python
# MCQ 응답 파싱
def parse_mcq_answer(raw_answer, expected_format='number'):
    # "정답: 2번", "①", "세번째" → "2" 변환

# 답변 정규화
def enhanced_answer_normalize(text):
    # "금위" → "금융위원회", "삼년" → "3년" 등 동의어 처리

# 평가 지표 계산
def calculate_enhanced_exact_match(pred, gold):
    # 완전일치, 포함관계, 토큰매칭율, 편집거리 종합 판단

def calculate_enhanced_f1_score(pred, gold):
    # 법령 답변의 부분적 정확성 반영

# Excel 입출력
def load_excel_data(file_path, mcq_limit=None, short_limit=None)
def save_evaluation_results(results, output_file=None)
```

#### B. 통합 평가기 (evaluator.py)

```python
class UnifiedEvaluator:
    def evaluate_file(file_path, mcq_limit=None, short_limit=None):
        # 1. MCQ 배치 평가
        mcq_accuracy, mcq_results = self.evaluate_mcq_batch(mcq_questions)
        
        # 2. Short Answer 배치 평가
        short_em, short_f1, short_results = self.evaluate_short_batch(short_questions)
        
        # 3. 성능 요약 생성
        performance_summary = self._generate_performance_summary()
        
        # 4. 결과 저장
        self.save_results(results, output_file)
```

**오답 분석**:
- MCQ: `choice_mapping`, `context_quality`, `search_failure`, `negative_detection`, `llm_reasoning`
- Short: `extraction_failure`, `normalization_failure`, `low_bm25_score`, `context_mismatch`

#### C. 실행 엔트리포인트 (evaluate.py)

```python
def run_evaluation(file_path, mcq_limit=None, short_limit=None, progress_callback=None):
    # CLI/웹 환경에서 평가 실행
    
def validate_environment():
    # API 키, BM25 인덱스, Pinecone 연결 상태 검증

def main():
    # CLI 인터페이스: python evaluate.py test.xlsx --mcq 10 --short 5
```

### 3.5 애플리케이션 및 관리 단계

#### A. 환경 설정 관리 (config.py)

```python
class Config:
    # API 키 관리
    openai_api_key: str
    upstage_api_key: str
    pinecone_api_key: str
    
    # 인덱스 경로
    bm25_index_path: str
    
    # LLM 설정
    max_tokens: int = 2000
    llm_timeout: int = 30
    
    def validate(self, silent=False):
        # API 키, 인덱스 파일, Pinecone 연결 검증
    
    def is_production_ready(self):
        # 운영 환경 준비 상태 확인

# 환경 검증 함수
def validate_runtime_environment():
    # 디스크 공간, 메모리, 네트워크 상태 점검
```

#### B. Streamlit UI 애플리케이션 (app.py)

**주요 탭 구성**:

1. **질의응답 탭**
```python
def create_chat_interface():
    # 질문 입력 → 검색 → LLM 답변 → 대화 기록 표시
    
def retrieve(question, top_k=5):
    # HybridRetriever로 관련 문서 검색
    
def generate_answer_short(question, contexts):
    # 단답형 답변 생성
```

2. **평가 시스템 탭**
```python
def create_evaluation_controls():
    # 평가 시작/중지 버튼, 파일 업로드
    
def display_real_time_monitoring():
    # 진행률 바, 문제별 상태 로그
    
def run_evaluation_task(excel_file, mcq_limit, short_limit):
    # UnifiedEvaluator 백그라운드 실행
```

3. **관리 도구 탭**
```python
def create_management_interface():
    # BM25 재생성, 벡터 재생성, Pinecone 백업 버튼
    
def run_management_task_with_status(task_name):
    # 관리 스크립트 실행 및 상태 업데이트
```

## 4. 데이터 흐름 예시

### 4.1 MCQ 질문 처리 과정

```
입력: "조합의 사업에 드는 비용을 조합원에게 부과할 수 있는 근거는?"
선택지: A) 제10조 총회, B) 제11조 비용부담, C) 제20조 해산, D) 제30조 임원

1. 검색 단계:
   - BM25: "제11조 조합의 사업에 드는 비용은 조합원에게 부과할 수 있다" (score: 6.1)
   - Vector: 동일 조항 (score: 47.0)
   - 병합: final_score 42.5

2. LLM 응답:
   - 입력: 질문 + 선택지 + 컨텍스트
   - 출력: "정답은 B입니다. 제11조에서 근거를 찾을 수 있습니다."
   - 파싱: "B"

3. 평가:
   - 정답: "2", 예측: "B" → "2" 변환
   - 결과: 정답 (EM=1.0)
```

### 4.2 Short Answer 질문 처리 과정

```
입력: "조합의 사업에 드는 비용은 누가 부담하는가?"

1. 검색 단계:
   - 동일한 제11조 조항 검색
   
2. LLM 응답:
   - 입력: 질문 + 컨텍스트
   - 출력: "정답은 '조합원'입니다."
   - 후처리: "조합원"

3. 평가:
   - 정답: "조합원", 예측: "조합원"
   - 결과: EM=1.0, F1=1.0
```

## 5. 설치 및 실행 가이드

### 5.1 환경 설정

```bash
# 필수 패키지 설치
pip install streamlit pandas openpyxl
pip install rank-bm25 pinecone-client
pip install openai upstage
pip install kiwipiepy  # 한국어 형태소 분석기

# 환경 변수 설정
export OPENAI_API_KEY="your-openai-key"
export UPSTAGE_API_KEY="your-upstage-key"
export PINECONE_API_KEY="your-pinecone-key"
```

### 5.2 인덱스 구축

```bash
# 1. BM25 인덱스 생성
python pipeline_bm25_from_docx.py

# 2. Vector 인덱스 생성
python reindex_upstage_docx.py
```

### 5.3 시스템 실행

```bash
# Streamlit UI 실행
streamlit run app.py

# CLI 평가 실행
python evaluate.py test.xlsx --mcq 10 --short 5
```

## 6. 성능 최적화 및 운영 가이드

### 6.1 검색 성능 튜닝

```python
# hybrid_retriever.py 설정
SEARCH_WEIGHTS = {
    "MCQ": {"bm25": 0.3, "vector": 0.7},
    "short": {"bm25": 0.4, "vector": 0.6}
}

# 청킹 파라미터 조정
CHUNK_SIZE = 800        # 청크 최대 길이
CHUNK_OVERLAP = 80      # 중첩 크기
```

### 6.2 평가 지표 개선

```python
# utils.py - EM 계산 임계값
EM_THRESHOLDS = {
    "coverage_threshold": 0.35,     # 포함 관계 임계값
    "token_match_threshold": 0.55,  # 토큰 매칭 임계값
    "edit_similarity_threshold": 0.72  # 편집거리 임계값
}
```

### 6.3 운영 모니터링

```python
# config.py - 시스템 상태 점검
def validate_runtime_environment():
    # 디스크 여유 공간: 1GB 이상
    # 메모리 사용률: 80% 이하
    # Pinecone 연결: 정상
```

## 7. 문제 해결 가이드

### 7.1 일반적인 오류

| 오류 | 원인 | 해결방법 |
|------|------|----------|
| BM25 인덱스 로드 실패 | bm25.pkl 파일 없음 | `python pipeline_bm25_from_docx.py` 실행 |
| Pinecone 연결 오류 | API 키 또는 인덱스명 오류 | config.py에서 설정 확인 |
| LLM 응답 오류 | API 키 만료 또는 rate limit | API 키 갱신, 요청 간격 조정 |

### 7.2 성능 최적화

- **검색 속도 개선**: BM25 인덱스 정기 재생성
- **정확도 향상**: 법령 동의어 사전 확장 (`utils.py`)
- **메모리 최적화**: 배치 크기 조정 (`reindex_upstage_docx.py`)

## 8. 확장 가능성

### 8.1 새로운 문서 타입 지원
- PDF, HWP 파일 처리 모듈 추가
- 다국어 법령 지원

### 8.2 검색 알고리즘 확장
- Dense Passage Retrieval (DPR) 추가
- 그래프 기반 검색 (Neo4j) 통합

### 8.3 평가 지표 확장
- BLEU, ROUGE 스코어 추가
- 도메인 특화 평가 지표 개발

## 부록: API 참조

### A. 주요 클래스 및 메소드

```python
# HybridRetriever 주요 메소드
class HybridRetriever:
    def search(query: str, question_type: str = "general", top_k: int = None) -> List[SearchResult]
    def _bm25_search(query: str, top_k: int) -> List[SearchResult]
    def _vector_search(query: str, top_k: int) -> List[SearchResult]

# HybridLLM 주요 메소드  
class HybridLLM:
    def call_mcq(question: str, choices: Dict[str, str], context: str) -> str
    def call_short(question: str, context: str) -> str

# UnifiedEvaluator 주요 메소드
class UnifiedEvaluator:
    def evaluate_file(file_path: str, mcq_limit: int = None, short_limit: int = None) -> Dict
    def evaluate_mcq_batch(questions: List[Dict]) -> Tuple[float, List[Dict]]
    def evaluate_short_batch(questions: List[Dict]) -> Tuple[float, float, List[Dict]]
```

### B. 설정 파라미터

```python
# 기본 설정값
DEFAULT_CONFIG = {
    "chunk_size": 800,
    "chunk_overlap": 80,
    "max_tokens": 2000,
    "llm_timeout": 30,
    "top_k_default": 12,
    "bm25_weight": 0.3,
    "vector_weight": 0.7
}
```

---

*이 매뉴얼은 금융 법령 RAG 시스템의 완전한 구현 및 운영 가이드를 제공합니다. 시스템의 각 구성요소와 데이터 흐름을 이해하고, 효과적으로 활용하시기 바랍니다.*