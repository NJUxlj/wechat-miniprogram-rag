
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..services.doubao import DouBaoService
from ..services.rag import RAGService

router = APIRouter()
doubao_service = DouBaoService()
rag_service = RAGService()

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    references: List[Dict]

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 1. 通过RAG检索相关文档
        relevant_docs = await rag_service.search_similar(request.query)
        
        # 2. 构建提示词
        context = "\n".join([doc["content"] for doc in relevant_docs])
        messages = [
            {"role": "system", "content": f"你是一个智能助手。请基于以下参考信息回答用户问题：\n{context}"},
            *request.history,
            {"role": "user", "content": request.query}
        ]
        
        # 3. 调用豆包API
        response = await doubao_service.chat(messages)
        
        return ChatResponse(
            response=response["choices"][0]["message"]["content"],
            references=relevant_docs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

