"""图片处理工具模块"""
import hashlib
import logging
from io import BytesIO
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageOps

from ..config import settings
from ..models import (
    ImageInfo, ProcessedImage, ImageRequestParams, 
    ImageFormat, CompressionLevel
)
from ..exceptions import (
    ImageProcessingError, UnsupportedFormatError, 
    InvalidParameterError
)

logger = logging.getLogger(__name__)


class ImageProcessor:
    """图片处理器类"""
    
    def __init__(self):
        self.supported_formats = {
            '.jpg': ImageFormat.JPEG,
            '.jpeg': ImageFormat.JPEG,
            '.png': ImageFormat.PNG,
            '.webp': ImageFormat.WEBP,
            '.bmp': ImageFormat.BMP,
            '.tiff': ImageFormat.TIFF
        }
    
    def get_image_info(self, image_path: Path) -> ImageInfo:
        """获取图片基本信息"""
        try:
            stat = image_path.stat()
            with Image.open(image_path) as img:
                return ImageInfo(
                    path=image_path,
                    name=image_path.name,
                    size=stat.st_size,
                    format=img.format,
                    width=img.width,
                    height=img.height,
                    created_time=stat.st_ctime,
                    modified_time=stat.st_mtime
                )
        except Exception as e:
            logger.error(f"获取图片信息失败 {image_path}: {e}")
            raise ImageProcessingError(f"无法读取图片信息: {str(e)}")
    
    def calculate_optimal_quality(self, image_size: int, target_size: Optional[int] = None) -> int:
        """根据图片大小计算最优压缩质量"""
        if target_size is None:
            target_size = settings.DEFAULT_COMPRESSION_QUALITY
        
        # 智能压缩算法：大图用较低质量，小图用较高质量
        if image_size > 5 * 1024 * 1024:  # 大于5MB
            return max(settings.MIN_COMPRESSION_QUALITY, target_size - 15)
        elif image_size > 1 * 1024 * 1024:  # 大于1MB
            return max(settings.MIN_COMPRESSION_QUALITY, target_size - 5)
        else:
            return min(settings.MAX_COMPRESSION_QUALITY, target_size + 5)
    
    def resize_image(self, img: Image.Image, params: ImageRequestParams) -> Image.Image:
        """调整图片尺寸"""
        if params.width is None and params.height is None:
            # 如果没有指定尺寸，使用默认宽度
            params.width = settings.DEFAULT_WIDTH
        
        original_width, original_height = img.size
        
        if params.preserve_aspect_ratio:
            # 保持宽高比
            if params.width and not params.height:
                # 只指定了宽度
                ratio = params.width / original_width
                new_height = int(original_height * ratio)
                new_size = (params.width, new_height)
            elif params.height and not params.width:
                # 只指定了高度
                ratio = params.height / original_height
                new_width = int(original_width * ratio)
                new_size = (new_width, params.height)
            elif params.width and params.height:
                # 同时指定了宽高，按比例缩放
                ratio_w = params.width / original_width
                ratio_h = params.height / original_height
                ratio = min(ratio_w, ratio_h)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                new_size = (new_width, new_height)
            else:
                new_size = (original_width, original_height)
        else:
            # 不保持宽高比
            new_width = params.width or original_width
            new_height = params.height or original_height
            new_size = (new_width, new_height)
        
        # 限制最大尺寸
        if new_size[0] > settings.MAX_IMAGE_SIZE or new_size[1] > settings.MAX_IMAGE_SIZE:
            ratio = settings.MAX_IMAGE_SIZE / max(new_size)
            new_width = int(new_size[0] * ratio)
            new_height = int(new_size[1] * ratio)
            new_size = (new_width, new_height)
        
        if new_size != img.size:
            return img.resize(new_size, Image.Resampling.LANCZOS)
        return img
    
    def convert_format(self, img: Image.Image, target_format: ImageFormat) -> Image.Image:
        """转换图片格式"""
        # 处理RGBA模式的图片
        if img.mode in ('RGBA', 'LA') and target_format in [ImageFormat.JPEG, ImageFormat.WEBP]:
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[-1])
            else:
                background.paste(img)
            img = background
        elif img.mode == 'P' and target_format in [ImageFormat.JPEG, ImageFormat.WEBP]:
            # 处理调色板模式
            img = img.convert('RGB')
        
        return img
    
    def compress_image(self, 
                      img: Image.Image, 
                      params: ImageRequestParams,
                      original_size: int) -> ProcessedImage:
        """压缩图片"""
        try:
            # 调整尺寸
            resized_img = self.resize_image(img, params)
            
            # 转换格式
            target_format = params.format or ImageFormat[settings.OUTPUT_FORMAT]
            converted_img = self.convert_format(resized_img, target_format)
            
            # 计算压缩质量
            quality = params.quality or self.calculate_optimal_quality(original_size)
            quality = max(settings.MIN_COMPRESSION_QUALITY, 
                         min(settings.MAX_COMPRESSION_QUALITY, quality))
            
            # 保存到内存缓冲区
            buffer = BytesIO()
            
            save_kwargs = {
                'format': target_format.value,
                'optimize': True,
                'quality': quality
            }
            
            if params.progressive and target_format == ImageFormat.JPEG:
                save_kwargs['progressive'] = True
            
            converted_img.save(buffer, **save_kwargs)
            buffer.seek(0)
            
            compressed_content = buffer.getvalue()
            compressed_size = len(compressed_content)
            compression_ratio = compressed_size / original_size if original_size > 0 else 0
            
            return ProcessedImage(
                content=compressed_content,
                format=target_format,
                original_size=original_size,
                compressed_size=compressed_size,
                width=converted_img.width,
                height=converted_img.height,
                compression_ratio=compression_ratio
            )
            
        except Exception as e:
            logger.error(f"图片压缩失败: {e}")
            raise ImageProcessingError(f"图片压缩过程中发生错误: {str(e)}")
    
    def generate_cache_key(self, image_path: Path, params: ImageRequestParams) -> str:
        """生成缓存键"""
        param_str = f"{params.width}_{params.height}_{params.quality}_{params.format}_{params.progressive}"
        content = f"{image_path}_{param_str}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def validate_image_format(self, image_path: Path) -> bool:
        """验证图片格式是否支持"""
        suffix = image_path.suffix.lower()
        return suffix in self.supported_formats
    
    def get_supported_extensions(self) -> list:
        """获取支持的文件扩展名"""
        return list(self.supported_formats.keys())


# 全局图片处理器实例
image_processor = ImageProcessor()