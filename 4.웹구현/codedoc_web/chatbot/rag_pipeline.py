from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_upstage import UpstageEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
import os
from langchain_core.prompts import PromptTemplate

def setup_components():
    load_dotenv()

    # 1. RAG 체인 설정
    embedding = UpstageEmbeddings(model="solar-embedding-1-large")

    index_name = 'codedoc' 

    database = PineconeVectorStore(embedding=embedding, index_name=index_name)

    rag_llm = ChatOpenAI(model="gpt-5-nano") 
    retriever = database.as_retriever(search_kwargs={"k": 5})
    custom_prompt_template = """당신은 주어진 정보를 바탕으로 사용자의 질문에 답변하는 전문적인 금융 상담원입니다.
    반드시 한국어 높임말(존댓말)을 사용하여, 간결하고 명확하게 100자 이내로 답변해야 합니다.
    답변 시작 시 '요청하신 대로' 또는 '존댓말로 답변해 드리겠습니다'와 같은 불필요한 서론을 붙이지 마세요.

    [정보]
    {context}

    [질문]
    {question}

    [답변]:
    """

    # 2. PromptTemplate 객체 생성
    custom_rag_prompt = PromptTemplate(
        template=custom_prompt_template,
        input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        rag_llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": custom_rag_prompt},
        return_source_documents=True
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
    LLM을 사용하여 사용자의 대화 내용에서 사용자 성향 분석,
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
