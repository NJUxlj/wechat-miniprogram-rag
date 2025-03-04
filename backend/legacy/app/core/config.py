from pydantic_settings import BaseSettings
from functools import lru_cache # 从 functools 模块中导入 lru_cache 装饰器，用于缓存函数的返回值。

class Settings(BaseSettings):
    # 豆包API配置
    DOUBAO_AK: str # API Key
    # DOUBAO_SK: str
    
    # MongoDB配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "chatbot"
    
    # Milvus配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    
    # FastAPI配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ChatBot API"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    '''
    使用 @lru_cache() 装饰器修饰 get_settings 函数，
    确保每次调用 get_settings() 时都返回同一个 Settings 实例，
    避免重复创建配置对象。
    '''
    return Settings()

settings = get_settings()

