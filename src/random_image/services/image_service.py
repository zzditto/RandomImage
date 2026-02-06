"""图片服务业务逻辑模块"""
import logging
import random
import time
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional

from ..config import settings
from ..models import (
    ImageInfo, ProcessedImage, ImageRequestParams, 
    HealthStatus
)
from ..exceptions import (
    ImageNotFoundError, DirectoryAccessError, 
    ImageProcessingError
)
from ..utils.image_processor import image_processor

logger = logging.getLogger(__name__)


class ImageCache:
    """简单的LRU缓存实现"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[ProcessedImage]:
        """从缓存获取数据"""
        if key in self.cache:
            self.hits += 1
            # 移动到最前面（最近使用）
            self.cache.move_to_end(key)
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, key: str, value: ProcessedImage) -> None:
        """放入缓存"""
        if key in self.cache:
            # 更新现有项
            self.cache.move_to_end(key)
        else:
            # 添加新项
            if len(self.cache) >= self.max_size:
                # 删除最老的项
                self.cache.popitem(last=False)
        self.cache[key] = value
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0


class ImageService:
    """图片服务类"""
    
    def __init__(self):
        self.cache = ImageCache(max_size=settings.CACHE_MAX_SIZE)
        self.image_list: List[Path] = []
        self.last_update_time = 0
        self.start_time = time.time()
        self._load_images()
    
    def _scan_directories(self) -> List[Path]:
        """扫描图片目录获取所有图片文件"""
        image_files = []
        
        valid_dirs = settings.valid_image_dirs
        if not valid_dirs:
            raise DirectoryAccessError("没有找到有效的图片目录")
        
        supported_extensions = image_processor.get_supported_extensions()
        
        for directory in valid_dirs:
            try:
                for file_path in directory.rglob("*"):
                    if (file_path.is_file() and 
                        file_path.suffix.lower() in supported_extensions and
                        image_processor.validate_image_format(file_path)):
                        image_files.append(file_path)
            except PermissionError as e:
                logger.warning(f"无法访问目录 {directory}: {e}")
                continue
            except Exception as e:
                logger.error(f"扫描目录 {directory} 时出错: {e}")
                continue
        
        if not image_files:
            raise ImageNotFoundError("在指定目录中未找到任何图片文件")
        
        logger.info(f"找到 {len(image_files)} 个图片文件")
        return image_files
    
    def _load_images(self) -> None:
        """加载图片列表"""
        try:
            self.image_list = self._scan_directories()
            self.last_update_time = time.time()
            logger.info(f"成功加载 {len(self.image_list)} 张图片")
        except Exception as e:
            logger.error(f"加载图片失败: {e}")
            raise
    
    def refresh_images(self) -> int:
        """刷新图片列表"""
        old_count = len(self.image_list)
        self._load_images()
        new_count = len(self.image_list)
        logger.info(f"图片列表已刷新: {old_count} -> {new_count}")
        return new_count
    
    def get_random_image(self) -> Path:
        """获取随机图片路径"""
        if not self.image_list:
            raise ImageNotFoundError("图片列表为空")
        
        return random.choice(self.image_list)
    
    def get_image_info(self, image_path: Path) -> ImageInfo:
        """获取图片详细信息"""
        return image_processor.get_image_info(image_path)
    
    def process_image(self, 
                     image_path: Path, 
                     params: ImageRequestParams) -> ProcessedImage:
        """处理图片（带缓存）"""
        # 生成缓存键
        cache_key = image_processor.generate_cache_key(image_path, params)
        
        # 尝试从缓存获取
        if settings.ENABLE_CACHE:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
        
        # 缓存未命中，进行处理
        try:
            # 获取原始图片大小
            original_size = image_path.stat().st_size
            
            # 处理图片
            from PIL import Image
            with Image.open(image_path) as img:
                result = image_processor.compress_image(img, params, original_size)
                result = image_processor.compress_image(img, params, original_size)
            
            # 存入缓存
            if settings.ENABLE_CACHE:
                self.cache.put(cache_key, result)
                logger.debug(f"结果已缓存: {cache_key}")
            
            return result
            
        except Exception as e:
            logger.error(f"处理图片 {image_path} 失败: {e}")
            raise ImageProcessingError(f"图片处理失败: {str(e)}")
    
    def get_statistics(self) -> dict:
        """获取服务统计信息"""
        return {
            "total_images": len(self.image_list),
            "cache_hit_rate": round(self.cache.hit_rate * 100, 2),
            "cache_hits": self.cache.hits,
            "cache_misses": self.cache.misses,
            "last_update": self.last_update_time,
            "uptime_seconds": time.time() - self.start_time
        }
    
    def get_health_status(self) -> HealthStatus:
        """获取健康检查状态"""
        cache_status = "healthy" if self.cache.hit_rate > 0.5 else "degraded"
        
        return HealthStatus(
            status="healthy" if self.image_list else "unhealthy",
            version="1.0.0",
            uptime=time.time() - self.start_time,
            image_count=len(self.image_list),
            cache_status=cache_status,
            last_updated=self.last_update_time
        )


# 全局图片服务实例
image_service = ImageService()