"""配置管理模块"""

import os
from pathlib import Path
from typing import List, Optional


class Settings:
    """应用配置类"""

    # 服务器配置
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # 图片目录配置
    IMAGE_DIRS: List[Path] = [
        Path(os.getenv("IMAGE_DIR", "/Users/zz/Pictures"))  # 默认图片目录
    ]

    # 支持的图片格式
    SUPPORTED_FORMATS: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]

    # 图片压缩配置
    DEFAULT_COMPRESSION_QUALITY: int = int(os.getenv("COMPRESSION_QUALITY", "85"))
    MIN_COMPRESSION_QUALITY: int = 60
    MAX_COMPRESSION_QUALITY: int = 95

    # 输出格式配置
    OUTPUT_FORMAT: str = os.getenv("OUTPUT_FORMAT", "WEBP")  # WEBP, JPEG, PNG
    ENABLE_PROGRESSIVE: bool = os.getenv("PROGRESSIVE", "True").lower() == "true"

    # 缓存配置
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "True").lower() == "true"
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "100"))  # 最大缓存图片数量

    # 性能配置
    MAX_IMAGE_SIZE: int = int(
        os.getenv("MAX_IMAGE_SIZE", "2000")
    )  # 最大图片尺寸（像素）
    DEFAULT_WIDTH: int = int(os.getenv("DEFAULT_WIDTH", "800"))  # 默认输出宽度

    @property
    def valid_image_dirs(self) -> List[Path]:
        """获取有效的图片目录列表"""
        valid_dirs = []
        for directory in self.IMAGE_DIRS:
            if directory.exists() and directory.is_dir():
                valid_dirs.append(directory)
        return valid_dirs

    def validate_config(self) -> None:
        """验证配置的有效性"""
        if not self.valid_image_dirs:
            raise ValueError("没有找到有效的图片目录")

        if not (
            self.MIN_COMPRESSION_QUALITY
            <= self.DEFAULT_COMPRESSION_QUALITY
            <= self.MAX_COMPRESSION_QUALITY
        ):
            raise ValueError(
                f"压缩质量必须在 {self.MIN_COMPRESSION_QUALITY}-{self.MAX_COMPRESSION_QUALITY} 之间"
            )


# 全局配置实例
settings = Settings()

try:
    settings.validate_config()
except ValueError as e:
    print(f"配置错误: {e}")
