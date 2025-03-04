# WeChat miniprogram RAG

## Project Description
本项目旨在实现一个基于大模型RAG技术的中医问答微信小程序

## project tools
- 后端框架：FastAPI（轻量级、高性能、易于使用）+ Django
- 数据库：MongoDB（适合存储非结构化的知识库数据）
- 向量数据库：Milvus（用于RAG系统的向量检索）
- RAG实现：LangChain（提供完整的RAG工具链）
- 大模型API：月之暗面/智谱/通义，优先使用 qwen-plus
- 前端：微信小程序开发者工具


## Project Structure
```Plain Text
wechat-rag-tcm/  
├── backend/                 # 后端服务  
│   ├── fastapi_app/         # API服务  
│   │   ├── main.py  
│   │   ├── routers/  
│   │   │   └── chat.py  
│   │   └── config.py  
│   ├── django_project/      # 管理后台  
│   │   ├── manage.py  
│   │   └── knowledge/  
│   │       ├── models.py  
│   │       └── admin.py  
│   ├── rag_service/         # RAG核心  
│   │   ├── chains/  
│   │   │   └── tcm_chain.py  
│   │   └── retriever.py  
│   └── requirements.txt  
├── frontend/                # 小程序前端  
│   ├── app.json  
│   ├── pages/  
│   │   └── chat/  
│   │       ├── index.js  
│   │       └── index.wxml  
└── infrastructure/          # 基础设施  
    ├── milvus/  
    └── mongo/  


```
