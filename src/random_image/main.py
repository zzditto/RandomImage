"""应用主入口文件"""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse

from .config import settings
from .api.routes import router
from .models import APIResponse
from .exceptions import EXCEPTION_HANDLERS

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("正在启动随机图片服务...")
    
    # 启动时的初始化工作
    try:
        # 验证配置
        settings.validate_config()
        logger.info("配置验证通过")
        
        # 初始化服务
        from .services.image_service import image_service
        logger.info(f"发现 {len(image_service.image_list)} 张图片")
        logger.info(f"缓存已启用: {settings.ENABLE_CACHE}")
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise
    
    yield
    
    # 关闭时的清理工作
    logger.info("正在关闭随机图片服务...")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title="随机图片服务",
        description="提供随机图片获取和处理的API服务",
        version="1.0.0",
        lifespan=lifespan,
        debug=settings.DEBUG
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(router, prefix="/api/v1")
    
    # 全局异常处理器
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content=APIResponse(
                success=False,
                message=exc.detail,
                error_code=f"HTTP_{exc.status_code}"
            ).__dict__
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content=APIResponse(
                success=False,
                message="请求参数验证失败",
                error_code="VALIDATION_ERROR",
                data={"details": exc.errors()}
            ).__dict__
        )
    
    # 自定义异常处理器
    for exception_class, status_code in EXCEPTION_HANDLERS.items():
        @app.exception_handler(exception_class)
        async def custom_exception_handler(request, exc):
            return JSONResponse(
                status_code=status_code,
                content=APIResponse(
                    success=False,
                    message=exc.message,
                    error_code=exc.error_code
                ).__dict__
            )
    
    # 根路径重定向
    @app.get("/")
    async def root():
        return {
            "message": "欢迎使用随机图片服务",
            "version": "1.0.0",
            "docs": "/docs",
            "api_prefix": "/api/v1"
        }
    
    # 健康检查简化版
    @app.get("/health")
    async def simple_health_check():
        return {"status": "healthy", "service": "random-image"}
    
    logger.info("应用创建完成")
    return app


# 创建应用实例
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"启动服务器: {settings.HOST}:{settings.PORT}")
    logger.info(f"调试模式: {settings.DEBUG}")
    
    uvicorn.run(
        "src.random_image.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )