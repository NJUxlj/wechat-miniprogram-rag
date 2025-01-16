
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # 用于处理跨源资源共享（CORS）
from app.core.config import settings
from app.api import chat, knowledge

app = FastAPI( # FastAPI 框架的核心类，用于创建应用实例
    title=settings.PROJECT_NAME, # 项目的名称
    openapi_url=f"{settings.API_V1_STR}/openapi.json" # 用于生成 API 文档
)

# 配置CORS
app.add_middleware(
    CORSMiddleware, # 是一个中间件，用于处理跨源资源共享（CORS）。
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,  # 参数设置是否允许发送凭据（如 cookies）
    allow_methods=["*"], #  参数设置允许的 HTTP 方法。
    allow_headers=["*"], # 参数设置允许的 HTTP 头。
)

# 注册路由
'''
include_router 方法用于将路由添加到应用程序中。
chat.router 和 knowledge.router 是从 chat 和 knowledge 子模块导入的路由对象。
prefix 参数设置路由的前缀，通常是 API 版本号。
'''
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(knowledge.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run 方法用于启动应用程序，host="0.0.0.0" 表示监听所有网络接口，port=8000 表示监听端口 8000。
    uvicorn.run(app, host="0.0.0.0", port=8000)







'''
什么是跨源资源共享？

跨源资源共享（CORS）是一种机制，它使用额外的HTTP头来告诉浏览器，让运行在一个 origin (domain) 上的Web应用
被准许访问来自不同源服务器上的指定的资源。
当一个资源从与该资源本身所在的服务器不同的域、协议或端口请求一个资源时，
资源会发起一个跨域HTTP请求。

例如，一个站点（http://domain-a.com）的JavaScript代码试图从另一个站点（http://domain-b.com）获取数据，
这就是一个跨源请求。由于安全原因，浏览器限制从脚本内发起的跨源HTTP请求。例如，XMLHttpRequest和Fetch API遵循同源策略。这意味着使用这些API的Web应用程序只能从加载应用程序的同一个域请求HTTP资源，除非响应报文包含了正确CORS响应头。

CORS机制通过添加一些HTTP头来告诉浏览器，允许来自不同源的请求。这些头包括：

Access-Control-Allow-Origin: 指定哪些源可以访问资源。可以是一个具体的源，
也可以是通配符 * 表示允许任何源访问。

Access-Control-Allow-Methods: 指定允许的HTTP方法。
Access-Control-Allow-Headers: 指定允许的请求头。
Access-Control-Allow-Credentials: 指定是否允许发送Cookie等凭证信息。
在你的代码中，CORSMiddleware 是FastAPI提供的一个中间件，用于处理CORS。
通过配置这个中间件，你可以允许来自不同源的请求访问你的API。
在开发环境中，你可能会使用通配符 * 来允许任何源访问，但在生产环境中，建议设置具体的域名以确保安全性。







'''

