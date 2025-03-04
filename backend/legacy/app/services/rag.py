
from typing import List, Dict
from langchain.vectorstores import Milvus
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from pymongo import MongoClient
from ..core.config import settings

class RAGService:
    def __init__(self):
        # 初始化MongoDB客户端
        self.mongo_client = MongoClient(settings.MONGODB_URL)
        self.db = self.mongo_client[settings.MONGODB_DB]
        
        # 初始化向量数据库
        self.embeddings = HuggingFaceEmbeddings(
            model_name="shibing624/text2vec-base-chinese"
        )
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            connection_args={
                "host": settings.MILVUS_HOST,
                "port": settings.MILVUS_PORT
            },
            collection_name="knowledge_base"
        )
        
    async def add_knowledge(self, content: str, metadata: Dict) -> str:
        """
        添加新的知识到知识库
        
        Args:
            content: 知识内容
            metadata: 元数据
        
        Returns:
            str: 文档ID
        """
        # 分割文本
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_text(content)
        
        # 存储到向量数据库
        self.vector_store.add_texts(texts, metadatas=[metadata] * len(texts))
        
        # 存储原始文档到MongoDB
        doc_id = self.db.documents.insert_one({
            "content": content,
            "metadata": metadata
        }).inserted_id
        
        return str(doc_id)
    
    async def search_similar(self, query: str, k: int = 3) -> List[Dict]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            List[Dict]: 相似文档列表
        """
        docs = self.vector_store.similarity_search(query, k=k)
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in docs
        ]

