from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_upstage import UpstageEmbeddings
import os
from langchain_pinecone import PineconeVectorStore
from langchain import hub
from langchain_openai import ChatOpenAI
import numpy as np
from langchain.chains import RetrievalQA
from sklearn.metrics.pairwise import cosine_similarity

def setup_components():
    load_dotenv()

    # 1. RAG 체인 설정
    embedding = UpstageEmbeddings(model="solar-embedding-1-large")

    index_name = 'codedoc' 

    database = PineconeVectorStore(embedding=embedding, index_name=index_name)

    retriever = database.as_retriever(search_kwargs={"k": 5})

    prompt = hub.pull('rlm/rag-prompt')
    rag_llm = ChatOpenAI(model="gpt-5-nano") 
    qa_chain = RetrievalQA.from_chain_type(
        rag_llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
    )

    # 2. 질문 분류용 LLM 설정
    classifier_llm = ChatOpenAI(model="gpt-5-nano", temperature=0) 
    
    return qa_chain, classifier_llm

QA_CHAIN, CLASSIFIER_LLM = setup_components()
EMBEDDING_MODEL = UpstageEmbeddings(model="solar-embedding-1-large")

def get_rag_response(query: str) -> str:
    classification_prompt = f"Is the following question related to finance, investment, or economics? Answer with only 'Yes' or 'No'.\n\nQuestion: {query}"
    classification_result = CLASSIFIER_LLM.invoke(classification_prompt).content.strip().lower() # type: ignore

    if 'no' in classification_result:
        return '금융, 투자, 경제와 관련된 질문만 답변할 수 있습니다.'
    return "OK" 

def stream_rag_response(query: str):
    for chunk in QA_CHAIN.stream({"query": query}):
        if 'result' in chunk:
            yield chunk['result']

# 사용자 분석

def get_risk_profile_by_similarity(user_conversation: str) -> str:
    """
    코사인 유사도를 사용해 사용자의 위험 성향을 분석하는 함수
    """
    # 1. 위험 성향을 대표하는 기준 문장들 정의
    risk_averse_texts = [
        "원금 손실은 절대 안 돼요. 안전한 게 제일 중요해요.",
        "예금이나 적금처럼 확실한 상품이 좋아요.",
        "수익이 적더라도 안정적인 투자를 선호합니다.",
        '안전','안정','손실이 적은','위험이 적은','적금'
    ]
    risk_tolerant_texts = [
        "수익률이 높다면 위험을 감수할 수 있어요.",
        "공격적인 투자를 통해 높은 수익을 기대해요.",
        "단기적인 손실은 장기적인 수익을 위해 감당할 수 있습니다.",
        '수익성이 높은','돈을 많이 벌다','위험이 높은','주식','위험이 있는',
        '변동성이 높은','비트코인','단기적인'
    ]

    # 2. 기준 문장들과 사용자 대화 내용을 벡터로 변환
    # 각 그룹의 문장들을 평균내어 대표 벡터를 만듭니다.
    avg_averse_vector = np.mean(EMBEDDING_MODEL.embed_documents(risk_averse_texts), axis=0)
    avg_tolerant_vector = np.mean(EMBEDDING_MODEL.embed_documents(risk_tolerant_texts), axis=0)
    user_vector = EMBEDDING_MODEL.embed_query(user_conversation)

    # 3. 코사인 유사도 계산
    # scikit-learn의 cosine_similarity는 2D 배열을 기대하므로 벡터 형태를 맞춰줍니다.
    similarity_averse = cosine_similarity([user_vector], [avg_averse_vector])[0][0] # type: ignore
    similarity_tolerant = cosine_similarity([user_vector], [avg_tolerant_vector])[0][0] # type: ignore
 
    # 4. 성향 판단
    return f"위험 회피형 (유사도 점수: {similarity_averse:.2f}) \n 위험 감수형 (유사도 점수: {similarity_tolerant:.2f})"
