
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from ..models.schemas import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeResponse,
    KnowledgeListResponse,
    SearchQuery
)
from ..services.rag import RAGService
from ..core.security import get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
rag_service = RAGService()

@router.post("/create", response_model=KnowledgeResponse)
async def create_knowledge(
    knowledge: KnowledgeCreate,
    current_user: str = Depends(get_current_user)
):
    """
    创建新的知识文档
    """
    try:
        # 添加创建时间和更新时间
        metadata = {
            **knowledge.metadata,
            "created_by": current_user,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # 保存到知识库
        doc_id = await rag_service.add_knowledge(
            content=knowledge.content,
            metadata={
                "title": knowledge.title,
                "category": knowledge.category,
                "tags": knowledge.tags,
                **metadata
            }
        )
        
        # 获取创建的文档
        doc = await rag_service.get_document(doc_id)
        
        return KnowledgeResponse(
            success=True,
            message="知识文档创建成功",
            data=doc
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=KnowledgeListResponse)
async def list_knowledge(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: str = Depends(get_current_user)
):
    """
    获取知识文档列表
    """
    try:
        # 构建查询条件
        query = {}
        if category:
            query["metadata.category"] = category
        if tag:
            query["metadata.tags"] = tag
            
        # 获取文档列表
        docs, total = await rag_service.list_documents(
            query=query,
            skip=(page - 1) * limit,
            limit=limit
        )
        
        return KnowledgeListResponse(
            success=True,
            message="获取知识文档列表成功",
            total=total,
            data=docs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{doc_id}", response_model=KnowledgeResponse)
async def get_knowledge(
    doc_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    获取单个知识文档
    """
    try:
        doc = await rag_service.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="文档不存在")
            
        return KnowledgeResponse(
            success=True,
            message="获取知识文档成功",
            data=doc
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{doc_id}", response_model=KnowledgeResponse)
async def update_knowledge(
    doc_id: str,
    update_data: KnowledgeUpdate,
    current_user: str = Depends(get_current_user)
):
    """
    更新知识文档
    """
    try:
        # 检查文档是否存在
        doc = await rag_service.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="文档不存在")
            
        # 更新文档
        update_dict = update_data.dict(exclude_unset=True)
        update_dict["metadata.updated_at"] = datetime.utcnow()
        update_dict["metadata.updated_by"] = current_user
        
        updated_doc = await rag_service.update_document(doc_id, update_dict)
        
        # 如果内容更新了，需要更新向量存储
        if "content" in update_dict:
            await rag_service.update_vectors(doc_id, update_dict["content"])
        
        return KnowledgeResponse(
            success=True,
            message="知识文档更新成功",
            data=updated_doc
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doc_id}", response_model=KnowledgeResponse)
async def delete_knowledge(
    doc_id: str,
    current_user: str = Depends(get_current_user)
):
    """
    删除知识文档
    """
    try:
        # 检查文档是否存在
        doc = await rag_service.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="文档不存在")
            
        # 删除文档
        await rag_service.delete_document(doc_id)
        
        return KnowledgeResponse(
            success=True,
            message="知识文档删除成功",
            data=None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=KnowledgeListResponse)
async def search_knowledge(
    query: SearchQuery,
    current_user: str = Depends(get_current_user)
):
    """
    搜索知识文档
    """
    try:
        # 构建搜索条件
        filter_dict = {}
        if query.category:
            filter_dict["metadata.category"] = query.category
        if query.tags:
            filter_dict["metadata.tags"] = {"$all": query.tags}
            
        # 执行向量搜索
        results = await rag_service.search_similar(
            query=query.query,
            k=query.limit,
            filter_dict=filter_dict
        )
        
        return KnowledgeListResponse(
            success=True,
            message="搜索成功",
            total=len(results),
            data=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

