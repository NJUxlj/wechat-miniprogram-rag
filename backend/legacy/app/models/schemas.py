# Pydantic模型

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    """用于处理MongoDB的ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(str(v)):
            raise ValueError("Invalid ObjectId")
        return str(v)

class KnowledgeBase(BaseModel):
    """知识库基础模型"""
    id: Optional[PyObjectId] = Field(alias="_id")
    title: str = Field(..., description="知识文档标题")
    content: str = Field(..., description="知识文档内容")
    category: str = Field(..., description="知识类别")
    tags: List[str] = Field(default=[], description="标签列表")
    metadata: Dict = Field(default={}, description="元数据")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }

class KnowledgeCreate(BaseModel):
    """创建知识文档的请求模型"""
    title: str = Field(..., description="知识文档标题")
    content: str = Field(..., description="知识文档内容")
    category: str = Field(..., description="知识类别")
    tags: Optional[List[str]] = Field(default=[], description="标签列表")
    metadata: Optional[Dict] = Field(default={}, description="元数据")

class KnowledgeUpdate(BaseModel):
    """更新知识文档的请求模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class KnowledgeResponse(BaseModel):
    """知识文档的响应模型"""
    success: bool
    message: str
    data: Optional[KnowledgeBase] = None

class KnowledgeListResponse(BaseModel):
    """知识文档列表的响应模型"""
    success: bool
    message: str
    total: int
    data: List[KnowledgeBase]

class SearchQuery(BaseModel):
    """搜索请求模型"""
    query: str = Field(..., description="搜索关键词")
    category: Optional[str] = Field(None, description="按类别筛选")
    tags: Optional[List[str]] = Field(None, description="按标签筛选")
    limit: int = Field(default=10, ge=1, le=50, description="返回结果数量")

