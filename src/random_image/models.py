"""数据模型定义"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
from datetime import datetime


class ImageFormat(str, Enum):
    """支持的图片格式枚举"""

    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    BMP = "BMP"
    TIFF = "TIFF"


class CompressionLevel(str, Enum):
    """压缩级别枚举"""

    LOW = "low"  # 低压缩，高质量
    MEDIUM = "medium"  # 中等压缩
    HIGH = "high"  # 高压缩，低质量


@dataclass
class ImageInfo:
    """图片信息数据类"""

    path: Path
    name: str
    size: int  # 文件大小（字节）
    format: str
    width: int
    height: int
    created_time: datetime
    modified_time: datetime

    @property
    def aspect_ratio(self) -> float:
        """计算宽高比"""
        return self.width / self.height if self.height > 0 else 0

    @property
    def resolution(self) -> str:
        """返回分辨率字符串"""
        return f"{self.width}x{self.height}"


@dataclass
class ProcessedImage:
    """处理后的图片数据类"""

    content: bytes
    format: ImageFormat
    original_size: int
    compressed_size: int
    width: int
    height: int
    compression_ratio: float

    @property
    def size_saved(self) -> int:
        """节省的空间大小"""
        return self.original_size - self.compressed_size


@dataclass
class ImageRequestParams:
    """图片请求参数"""

    width: Optional[int] = None
    height: Optional[int] = None
    quality: Optional[int] = None
    format: Optional[ImageFormat] = None
    progressive: bool = True
    preserve_aspect_ratio: bool = True


@dataclass
class APIResponse:
    """API响应数据类"""

    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class HealthStatus:
    """健康检查状态"""

    status: str
    version: str
    uptime: float
    image_count: int
    cache_status: str
    last_updated: float
