"""API路由定义"""
import logging
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from ..services.image_service import image_service
from ..models import APIResponse, ImageRequestParams
from ..exceptions import RandomImageError, EXCEPTION_HANDLERS
from .dependencies import get_image_params

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=Response, summary="获取随机图片")
async def get_random_image(
    params: ImageRequestParams = Depends(get_image_params)
):
    """
    获取一张随机图片
    
    参数:
    - width: 图片宽度（像素）
    - height: 图片高度（像素）
    - quality: 压缩质量（60-95）
    - format: 输出格式（JPEG, PNG, WEBP）
    - progressive: 是否启用渐进式JPEG
    - preserve_aspect_ratio: 是否保持宽高比
    """
    try:
        # 获取随机图片
        image_path = image_service.get_random_image()
        
        # 处理图片
        processed_image = image_service.process_image(image_path, params)
        
        # 返回图片响应
        media_type = f"image/{processed_image.format.value.lower()}"
        return Response(
            content=processed_image.content,
            media_type=media_type,
            headers={
                "Content-Length": str(processed_image.compressed_size),
                "X-Original-Size": str(processed_image.original_size),
                "X-Compressed-Size": str(processed_image.compressed_size),
                "X-Compression-Ratio": f"{processed_image.compression_ratio:.2f}",
                "X-Size-Saved": str(processed_image.size_saved)
            }
        )
        
    except RandomImageError as e:
        status_code = EXCEPTION_HANDLERS.get(type(e), 500)
        return JSONResponse(
            status_code=status_code,
            content=APIResponse(
                success=False,
                message=e.message,
                error_code=e.error_code
            ).__dict__
        )
    except Exception as e:
        logger.error(f"未预期的错误: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponse(
                success=False,
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ).__dict__
        )


@router.get("/stats", response_model=APIResponse, summary="获取服务统计信息")
async def get_statistics():
    """获取服务运行统计信息"""
    try:
        stats = image_service.get_statistics()
        return APIResponse(
            success=True,
            data=stats,
            message="统计信息获取成功"
        )
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return APIResponse(
            success=False,
            message="获取统计信息失败",
            error_code="STATS_ERROR"
        )


@router.post("/refresh", response_model=APIResponse, summary="刷新图片列表")
async def refresh_images():
    """手动刷新图片列表"""
    try:
        count = image_service.refresh_images()
        return APIResponse(
            success=True,
            data={"image_count": count},
            message=f"成功刷新 {count} 张图片"
        )
    except Exception as e:
        logger.error(f"刷新图片列表失败: {e}")
        return APIResponse(
            success=False,
            message="刷新图片列表失败",
            error_code="REFRESH_ERROR"
        )


@router.get("/health", response_model=APIResponse, summary="健康检查")
async def health_check():
    """健康检查端点"""
    try:
        health_status = image_service.get_health_status()
        return APIResponse(
            success=True,
            data=health_status.__dict__,
            message="服务运行正常"
        )
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return APIResponse(
            success=False,
            message="服务状态异常",
            error_code="HEALTH_CHECK_ERROR"
        )


@router.get("/info", response_model=APIResponse, summary="获取系统信息")
async def get_system_info():
    """获取系统配置信息"""
    try:
        info = {
            "version": "1.0.0",
            "supported_formats": [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"],
            "compression_range": f"{60}-{95}",
            "default_output_format": "WEBP",
            "cache_enabled": True,
            "max_image_size": 2000
        }
        return APIResponse(
            success=True,
            data=info,
            message="系统信息获取成功"
        )
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        return APIResponse(
            success=False,
            message="获取系统信息失败",
            error_code="INFO_ERROR"
        )