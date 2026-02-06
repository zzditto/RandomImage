"""依赖注入模块"""

from fastapi import Depends, HTTPException, status
from typing import Optional

from ..config import settings
from ..models import ImageRequestParams, ImageFormat
from ..exceptions import EXCEPTION_HANDLERS


def get_image_params(
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: Optional[int] = None,
    format: Optional[str] = None,
    progressive: bool = True,
    preserve_aspect_ratio: bool = True,
) -> ImageRequestParams:
    """解析和验证图片请求参数"""
    # 验证参数
    if width is not None and width <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="宽度必须大于0"
        )

    if height is not None and height <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="高度必须大于0"
        )

    if quality is not None:
        if (
            quality < settings.MIN_COMPRESSION_QUALITY
            or quality > settings.MAX_COMPRESSION_QUALITY
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"压缩质量必须在 {settings.MIN_COMPRESSION_QUALITY}-{settings.MAX_COMPRESSION_QUALITY} 之间",
            )

    # 转换格式参数
    image_format = None
    if format:
        try:
            image_format = ImageFormat[format.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的图片格式: {format}",
            )

    return ImageRequestParams(
        width=width,
        height=height,
        quality=quality,
        format=image_format,
        progressive=progressive,
        preserve_aspect_ratio=preserve_aspect_ratio,
    )


def get_exception_handler():
    """获取异常处理器映射"""
    return EXCEPTION_HANDLERS
