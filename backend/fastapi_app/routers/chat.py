from fastapi import APIRouter, Depends  
from rag_service.chains.tcm_chain import get_rag_response  
from pydantic import BaseModel  

router = APIRouter()  

class QueryRequest(BaseModel):  
    question: str  
    history: list = [] 
    
    
@router.post("/chat")  
async def chat_endpoint(request: QueryRequest):  
    response = await get_rag_response(  
        question=request.question,  
        chat_history=request.history  
    )  
    return {  
        "answer": response["answer"],  
        "sources": response["source_documents"]  
    }  