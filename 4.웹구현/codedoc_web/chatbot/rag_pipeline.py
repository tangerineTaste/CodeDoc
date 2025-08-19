from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_upstage import UpstageEmbeddings
import os
from langchain_pinecone import PineconeVectorStore
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

def setup_rag_chain():
    load_dotenv()

    embedding = UpstageEmbeddings(model="solar-embedding-1-large")
    
    index_name = 'codedoc' 

    database = PineconeVectorStore(
        embedding=embedding, 
        index_name=index_name
    )

    retriever = database.as_retriever(search_kwargs={"k": 5})
    prompt = hub.pull('rlm/rag-prompt')
    llm = ChatOpenAI(model="gpt-5-nano") 

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
    )
    print("RAG chain initialized.")
    return qa_chain

QA_CHAIN = setup_rag_chain()

def get_rag_response(query: str) -> str:
    if QA_CHAIN is None:
        raise Exception("RAG Chain is not initialized.")

    # 금융 관련 질문인지 LLM에게 확인
    llm = ChatOpenAI(model="gpt-5-nano")
    classification_prompt = f"Is the following question related to finance? Answer with 'Yes' or 'No'.\n\nQuestion: {query}"
    classification_result = llm.invoke(classification_prompt).content.strip().lower() # type: ignore

    if 'no' in classification_result:
        return '금융과 관련된 질문만 해주세요.'

    # 미리 만들어진 체인을 바로 사용
    message = QA_CHAIN.invoke({"query": query})['result']
    return message