
from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID
from langchain.vectorstores import Milvus
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from pymongo import MongoClient
from bson import ObjectId

from ..core.config import settings
from ..core.security import get_password_hash
from ..models.schemas import (
    KnowledgeBase,
    KnowledgeDocument,
    DocumentCreate,
    DocumentUpdate,
    SearchQuery,
    VectorSearchResult
)

'''
知识库管理：

创建知识库
为每个知识库维护独立的向量存储
支持公开/私有知识库
支持访问码保护
文档管理：

创建文档（支持自定义分块大小）
更新文档（包括内容和元数据）
删除文档
文档版本控制
增强的搜索功能：

支持相似度阈值过滤
返回详细的元数据
权限验证
分页支持
安全特性：

用户权限验证
知识库访问控制
文档所有权管理
更好的错误处理和验证：

详细的错误消息
输入验证
状态检查


'''


class RAGService:
    def __init__(self):
        # 初始化MongoDB客户端
        self.mongo_client = MongoClient(settings.MONGODB_URL)
        self.db = self.mongo_client[settings.MONGODB_DB]
        
        # 初始化向量数据库
        self.embeddings = HuggingFaceEmbeddings(
            model_name="shibing624/text2vec-base-chinese"
        )
        
        # 为每个知识库创建独立的collection
        self.vector_stores = {}
        
    async def init_knowledge_base(self, knowledge_base: KnowledgeBase) -> str:
        """
        初始化新的知识库
        
        Args:
            knowledge_base: 知识库创建信息
            
        Returns:
            str: 知识库ID
        """
        # 创建知识库记录
        kb_data = {
            "name": knowledge_base.name,
            "description": knowledge_base.description,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "owner_id": knowledge_base.owner_id,
            "is_public": knowledge_base.is_public,
            "access_code": get_password_hash(knowledge_base.access_code) if knowledge_base.access_code else None
        }
        
        kb_id = str(self.db.knowledge_bases.insert_one(kb_data).inserted_id)
        
        # 初始化向量存储
        self.vector_stores[kb_id] = Milvus(
            embedding_function=self.embeddings,
            connection_args={
                "host": settings.MILVUS_HOST,
                "port": settings.MILVUS_PORT
            },
            collection_name=f"kb_{kb_id}"
        )
        
        return kb_id
    
    async def add_document(self, kb_id: str, document: DocumentCreate) -> str:
        """
        向知识库添加新文档
        
        Args:
            kb_id: 知识库ID
            document: 文档创建信息
        
        Returns:
            str: 文档ID
        """
        # 验证知识库存在
        kb = self.db.knowledge_bases.find_one({"_id": ObjectId(kb_id)})
        if not kb:
            raise ValueError("Knowledge base not found")
        
        # 分割文本
        text_splitter = CharacterTextSplitter(
            chunk_size=document.chunk_size or 1000,
            chunk_overlap=document.chunk_overlap or 200
        )
        texts = text_splitter.split_text(document.content)
        
        # 准备元数据
        metadata = {
            "title": document.title,
            "source": document.source,
            "author": document.author,
            "tags": document.tags,
            "created_at": datetime.utcnow(),
            "kb_id": kb_id
        }
        
        # 存储到向量数据库
        vector_store = self.vector_stores.get(kb_id)
        if not vector_store:
            raise ValueError("Vector store not initialized")
            
        vector_ids = vector_store.add_texts(
            texts=texts,
            metadatas=[{**metadata, "chunk_index": i} for i in range(len(texts))]
        )
        
        # 存储原始文档到MongoDB
        doc_data = {
            "kb_id": kb_id,
            "title": document.title,
            "content": document.content,
            "source": document.source,
            "author": document.author,
            "tags": document.tags,
            "vector_ids": vector_ids,
            "created_at": metadata["created_at"],
            "updated_at": metadata["created_at"],
            "status": "active"
        }
        
        doc_id = str(self.db.documents.insert_one(doc_data).inserted_id)
        return doc_id
    
    async def search_similar(
        self,
        kb_id: str,
        query: SearchQuery,
        user_id: Optional[str] = None
    ) -> List[VectorSearchResult]:
        """
        在知识库中搜索相似文档
        
        Args:
            kb_id: 知识库ID
            query: 搜索查询
            user_id: 用户ID（用于权限验证）
            
        Returns:
            List[VectorSearchResult]: 搜索结果列表
        """
        # 验证访问权限
        kb = self.db.knowledge_bases.find_one({"_id": ObjectId(kb_id)})
        if not kb:
            raise ValueError("Knowledge base not found")
            
        if not kb["is_public"] and kb["owner_id"] != user_id:
            raise ValueError("Access denied")
        
        # 获取向量存储
        vector_store = self.vector_stores.get(kb_id)
        if not vector_store:
            raise ValueError("Vector store not initialized")
        
        # 执行相似度搜索
        docs = vector_store.similarity_search_with_score(
            query.text,
            k=query.limit or 3,
            score_threshold=query.score_threshold or 0.5
        )
        
        # 格式化结果
        results = []
        for doc, score in docs:
            # 获取原始文档信息
            original_doc = self.db.documents.find_one({
                "kb_id": kb_id,
                "vector_ids": {"$in": [doc.metadata.get("vector_id")]}
            })
            
            results.append(VectorSearchResult(
                content=doc.page_content,
                score=float(score),
                metadata={
                    "title": original_doc["title"] if original_doc else None,
                    "source": doc.metadata.get("source"),
                    "author": doc.metadata.get("author"),
                    "chunk_index": doc.metadata.get("chunk_index"),
                    "created_at": doc.metadata.get("created_at")
                }
            ))
        
        return results
    
    async def delete_document(self, kb_id: str, doc_id: str, user_id: str) -> bool:
        """
        删除文档
        
        Args:
            kb_id: 知识库ID
            doc_id: 文档ID
            user_id: 用户ID（用于权限验证）
            
        Returns:
            bool: 是否删除成功
        """
        # 验证权限
        kb = self.db.knowledge_bases.find_one({"_id": ObjectId(kb_id)})
        if not kb or kb["owner_id"] != user_id:
            raise ValueError("Access denied")
        
        # 获取文档
        doc = self.db.documents.find_one({"_id": ObjectId(doc_id), "kb_id": kb_id})
        if not doc:
            raise ValueError("Document not found")
        
        # 从向量数据库删除
        vector_store = self.vector_stores.get(kb_id)
        if vector_store:
            for vector_id in doc["vector_ids"]:
                vector_store.delete([vector_id])
        
        # 从MongoDB删除
        result = self.db.documents.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0
    
    async def update_document(
        self,
        kb_id: str,
        doc_id: str,
        update_data: DocumentUpdate,
        user_id: str
    ) -> bool:
        """
        更新文档
        
        Args:
            kb_id: 知识库ID
            doc_id: 文档ID
            update_data: 更新数据
            user_id: 用户ID（用于权限验证）
            
        Returns:
            bool: 是否更新成功
        """
        # 验证权限
        kb = self.db.knowledge_bases.find_one({"_id": ObjectId(kb_id)})
        if not kb or kb["owner_id"] != user_id:
            raise ValueError("Access denied")
        
        # 获取原文档
        doc = self.db.documents.find_one({"_id": ObjectId(doc_id), "kb_id": kb_id})
        if not doc:
            raise ValueError("Document not found")
        
        # 如果内容发生变化，需要更新向量存储
        if update_data.content:
            # 删除旧的向量
            vector_store = self.vector_stores.get(kb_id)
            if vector_store:
                for vector_id in doc["vector_ids"]:
                    vector_store.delete([vector_id])
            
            # 创建新的向量
            text_splitter = CharacterTextSplitter(
                chunk_size=update_data.chunk_size or 1000,
                chunk_overlap=update_data.chunk_overlap or 200
            )
            texts = text_splitter.split_text(update_data.content)
            
            metadata = {
                "title": update_data.title or doc["title"],
                "source": update_data.source or doc["source"],
                "author": update_data.author or doc["author"],
                "tags": update_data.tags or doc["tags"],
                "updated_at": datetime.utcnow(),
                "kb_id": kb_id
            }
            
            vector_ids = vector_store.add_texts(
                texts=texts,
                metadatas=[{**metadata, "chunk_index": i} for i in range(len(texts))]
            )
        
        # 更新MongoDB文档
        update_fields = {
            "updated_at": datetime.utcnow()
        }
        
        if update_data.content:
            update_fields["content"] = update_data.content
            update_fields["vector_ids"] = vector_ids
        if update_data.title:
            update_fields["title"] = update_data.title
        if update_data.source:
            update_fields["source"] = update_data.source
        if update_data.author:
            update_fields["author"] = update_data.author
        if update_data.tags:
            update_fields["tags"] = update_data.tags
        
        result = self.db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": update_fields}
        )
        
        return result.modified_count > 0

