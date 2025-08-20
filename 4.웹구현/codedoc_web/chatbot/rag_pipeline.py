from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_upstage import UpstageEmbeddings
import os
from langchain_pinecone import PineconeVectorStore
from langchain import hub
from langchain_openai import ChatOpenAI
import numpy as np
from langchain.chains import RetrievalQA
import os
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

def setup_components():
    load_dotenv()

    # 1. RAG 체인 설정
    embedding = UpstageEmbeddings(model="solar-embedding-1-large")

    index_name = 'codedoc' 

    database = PineconeVectorStore(embedding=embedding, index_name=index_name)

    rag_llm = ChatOpenAI(model="gpt-5-nano") 
    retriever = database.as_retriever(search_kwargs={"k": 5})
    prompt = hub.pull('rlm/rag-prompt')

    qa_chain = RetrievalQA.from_chain_type(
        rag_llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
    )

    # 2. 질문 분류용 LLM 설정
    classifier_llm = ChatOpenAI(model="gpt-5-nano", temperature=0) 
    
    return qa_chain, classifier_llm, embedding

QA_CHAIN, CLASSIFIER_LLM,EMBEDDING_MODEL = setup_components()

def get_rag_response(query: str):
    classification_prompt = f"Is the following question related to finance, investment, or economics? Answer with only 'Yes' or 'No'. \n\nQuestion: {query}"

    classification_result = CLASSIFIER_LLM.invoke(classification_prompt).content.strip().lower() # type: ignore

    if 'no' in classification_result:
        return '죄송합니다. 금융, 투자, 경제와 관련된 질문에만 답변해 드릴 수 있습니다.'
    return "OK" 

def stream_rag_response(query: str):
    for chunk in QA_CHAIN.stream({"query": query}):
        if 'result' in chunk:
            yield chunk['result']

def analyze_profile_with_llm(user_conversation: str):
    """
    LLM을 사용하여 사용자의 대화 내용에서 '종합 금융 프로필'을 추출하고,
    그 결과를 JSON(파이썬 딕셔너리) 형태로 반환하는 함수.
    """
    analysis_prompt = f"""
    You are an expert financial profiler. Analyze the following user conversation with a financial assistant.

    **Rules:**
    1.  Analyze the user's personality by analyzing the words the user uses..
    2.  Analyze whether your users prefer stability or risk-taking and proactive behavior.
    3.  If the analysis result is stable, output 1, otherwise output -1.
    4.  The output is only a real number, either 1 or -1.

    **Conversation:** 
    {user_conversation}
    """
    
    # 이전에 정의한 분석용 LLM (CLASSIFIER_LLM 또는 새로 만든 ANALYZER_LLM)을 사용
    response = CLASSIFIER_LLM.invoke(analysis_prompt)
    
    return response.content
