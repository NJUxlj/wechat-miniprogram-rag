from langchain_community.vectorstores.milvus import Milvus  
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings  
from langchain_community.document_loaders.directory import DirectoryLoader, TextLoader  
from langchain.text_splitter import RecursiveCharacterTextSplitter  

def get_retriever():  
    embeddings = HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese")  
    
    vector_db = Milvus(  
        embedding_function=embeddings,  
        connection_args={"host": "localhost", "port": "19530"},  
        collection_name="tcm_knowledge"  
    )  
    
    return vector_db.as_retriever(search_kwargs={"k": 3})  

# 知识库初始化脚本  
def initialize_knowledge_base():  
    loader = DirectoryLoader("/data/tcm_docs", glob="**/*.txt")  
    documents = loader.load()  
    
    text_splitter = RecursiveCharacterTextSplitter(  
        chunk_size=500,  
        chunk_overlap=50  
    )  
    
    splits = text_splitter.split_documents(documents)  
    vector_db = Milvus.from_documents(  
        documents=splits,  
        embedding=get_retriever().embedding_function  
    )  