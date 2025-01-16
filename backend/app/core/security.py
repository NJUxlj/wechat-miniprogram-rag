
from fastapi import Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from ..core.config import settings
import secrets
import hashlib
import time
from typing import Optional

# API密钥认证
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# 用于生成临时令牌的密钥
TOKEN_SECRET = secrets.token_urlsafe(32)

def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> bool:
    """
    验证API密钥
    
    Args:
        api_key: 请求头中的API密钥
        
    Returns:
        bool: 验证是否通过
        
    Raises:
        HTTPException: 当验证失败时抛出
    """
    if not api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="未提供API密钥"
        )
    
    # 在实际应用中，这里应该从数据库或配置中获取有效的API密钥列表
    valid_api_keys = [settings.DOUBAO_AK]  # 示例：使用豆包API密钥作为有效密钥
    
    if api_key not in valid_api_keys:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="无效的API密钥"
        )
    
    return True

def generate_access_token(expires_in: int = 3600) -> dict:
    """
    生成临时访问令牌
    
    Args:
        expires_in: 过期时间（秒），默认1小时
        
    Returns:
        dict: 包含令牌和过期时间的字典
    """
    timestamp = int(time.time())
    expires_at = timestamp + expires_in
    
    # 生成令牌
    token_data = f"{timestamp}{TOKEN_SECRET}{expires_at}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    
    return {
        "access_token": token,
        "expires_at": expires_at
    }

def verify_access_token(token: str, timestamp: int) -> bool:
    """
    验证访问令牌
    
    Args:
        token: 访问令牌
        timestamp: 当前时间戳
        
    Returns:
        bool: 验证是否通过
    """
    # 检查令牌是否过期
    if timestamp > int(time.time()):
        return False
    
    # 验证令牌
    expected_token = hashlib.sha256(
        f"{timestamp}{TOKEN_SECRET}{timestamp}".encode()
    ).hexdigest()
    
    return token == expected_token

def get_current_user(api_key: str = Security(verify_api_key)):
    """
    获取当前用户（依赖项）
    
    Args:
        api_key: 经过验证的API密钥
        
    Returns:
        str: API密钥（代表当前用户）
    """
    return api_key

