"""
간소화된 Upstage 임베딩 서비스 - 로그 시스템 통합
"""
import os
import requests
import time
from typing import List, Dict, Any
from rag.utils import log_message  # 추가

# 기존 log_message 함수 전체 삭제 (25줄 정도)

class UpstageEmbedder:
    """로그 시스템 통합된 Upstage 임베딩 서비스"""
    
    def __init__(self, api_key: str = None, model: str = "embedding-query"):
        self.api_key = api_key or os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            log_message("FAILURE", "UPSTAGE_API_KEY 환경변수가 설정되지 않음", "EMBEDDER")
            raise ValueError("UPSTAGE_API_KEY 환경변수가 설정되지 않았습니다")
            
        self.model = model
        self.api_url = "https://api.upstage.ai/v1/embeddings"
        
        # 차원 자동 감지용
        self._embedding_dim = None
        self._last_request_time = 0
        self._min_interval = 0.05  # 50ms
        
        log_message("SUCCESS", f"Upstage 임베더 초기화 완료 (모델: {model})", "EMBEDDER")
        
    def _rate_limit(self):
        """간단한 rate limiting"""
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def _call_api(self, texts: List[str]) -> List[List[float]]:
        """API 호출"""
        self._rate_limit()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "input": texts if isinstance(texts, list) else [texts]
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            log_message("FAILURE", f"API 호출 실패: {e}", "EMBEDDER")
            raise
        
        try:
            result = response.json()
        except ValueError as e:
            log_message("FAILURE", f"JSON 파싱 실패: {e}", "EMBEDDER")
            raise
        
        embeddings = []
        
        for item in result["data"]:
            embedding = [float(x) for x in item["embedding"]]
            
            if self._embedding_dim is None:
                self._embedding_dim = len(embedding)
                log_message("SUCCESS", f"임베딩 차원 자동 감지: {self._embedding_dim}", "EMBEDDER")
            
            embeddings.append(embedding)
        
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """단일 쿼리 임베딩"""
        if not text or not text.strip():
            dim = self._embedding_dim or 1536
            log_message("INFO", "빈 텍스트로 인한 제로 벡터 반환", "EMBEDDER")
            return [0.0] * dim
        
        try:
            embeddings = self._call_api([text.strip()])
            return embeddings[0] if embeddings else [0.0] * (self._embedding_dim or 1536)
        except Exception as e:
            log_message("FAILURE", f"단일 쿼리 임베딩 실패: {e}", "EMBEDDER")
            dim = self._embedding_dim or 1536
            return [0.0] * dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """여러 문서 배치 임베딩"""
        if not texts:
            log_message("INFO", "빈 텍스트 리스트", "EMBEDDER")
            return []
        
        log_message("INFO", f"배치 임베딩 시작: {len(texts)}개 문서", "EMBEDDER")
        
        clean_texts = []
        text_indices = []
        
        for i, text in enumerate(texts):
            if text and text.strip():
                clean_texts.append(text.strip())
                text_indices.append(i)
        
        if not clean_texts:
            dim = self._embedding_dim or 1536
            log_message("INFO", f"모든 텍스트가 빈 값, {len(texts)}개 제로 벡터 반환", "EMBEDDER")
            return [[0.0] * dim] * len(texts)
        
        try:
            embeddings = self._call_api(clean_texts)
            log_message("SUCCESS", f"배치 임베딩 완료: {len(clean_texts)}개 처리됨", "EMBEDDER")
        except Exception as e:
            log_message("FAILURE", f"배치 임베딩 실패: {e}", "EMBEDDER")
            dim = self._embedding_dim or 1536
            return [[0.0] * dim] * len(texts)
        
        result = []
        embedding_idx = 0
        dim = self._embedding_dim or (len(embeddings[0]) if embeddings else 1536)
        
        for i in range(len(texts)):
            if i in text_indices:
                result.append(embeddings[embedding_idx])
                embedding_idx += 1
            else:
                result.append([0.0] * dim)
        
        return result

# 전역 인스턴스
_embedder = None

def get_embedder() -> UpstageEmbedder:
    global _embedder
    if _embedder is None:
        try:
            _embedder = UpstageEmbedder()
            log_message("SUCCESS", "전역 임베더 인스턴스 생성 완료", "EMBEDDER")
        except Exception as e:
            log_message("FAILURE", f"임베더 초기화 실패: {e}", "EMBEDDER")
            raise
    return _embedder