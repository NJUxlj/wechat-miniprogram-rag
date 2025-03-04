from langchain_core.runnables import RunnablePassthrough  
from langchain_core.prompts import ChatPromptTemplate  
from langchain_core.output_parsers import StrOutputParser  
from langchain_community.llms.tongyi import Tongyi  
from ..retriever import get_retriever  

def format_docs(docs):  
    return "\n\n".join(doc.page_content for doc in docs)  

def create_rag_chain():  
    llm = Tongyi(model_name="qwen-plus")  
    retriever = get_retriever()  
    
    prompt_template = """  
    你是一个专业的中医助手，请根据以下中医知识库内容回答问题：  
    
    {context}  
    
    问题：{question}  
    
    回答要求：  
    1. 使用简体中文回答  
    2. 引用文献使用【1】格式标注  
    3. 如果问题与中医无关，请礼貌拒绝回答  
    """  
    
    prompt = ChatPromptTemplate.from_template(prompt_template)  
    
    return (  
        {"context": retriever | format_docs, "question": RunnablePassthrough()}  
        | prompt  
        | llm  
        | StrOutputParser()  
    )  

async def get_rag_response(question: str):  
    chain = create_rag_chain()  
    response = await chain.ainvoke(question)  
    return {"answer": response}  