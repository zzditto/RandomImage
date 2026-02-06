"""自定义异常定义"""
from typing import Optional


class RandomImageError(Exception):
    """随机图片服务基础异常类"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ConfigurationError(RandomImageError):
    """配置相关异常"""
    pass


class ImageNotFoundError(RandomImageError):
    """图片未找到异常"""
    def __init__(self, message: str = "未找到可用的图片文件"):
        super().__init__(message, "IMAGE_NOT_FOUND")


class ImageProcessingError(RandomImageError):
    """图片处理异常"""
    def __init__(self, message: str = "图片处理失败"):
        super().__init__(message, "IMAGE_PROCESSING_ERROR")


class InvalidParameterError(RandomImageError):
    """无效参数异常"""
    def __init__(self, message: str = "请求参数无效"):
        super().__init__(message, "INVALID_PARAMETER")


class DirectoryAccessError(RandomImageError):
    """目录访问异常"""
    def __init__(self, message: str = "无法访问图片目录"):
        super().__init__(message, "DIRECTORY_ACCESS_ERROR")


class UnsupportedFormatError(RandomImageError):
    """不支持的格式异常"""
    def __init__(self, message: str = "不支持的图片格式"):
        super().__init__(message, "UNSUPPORTED_FORMAT")


class CacheError(RandomImageError):
    """缓存相关异常"""
    def __init__(self, message: str = "缓存操作失败"):
        super().__init__(message, "CACHE_ERROR")


# 异常处理器映射
EXCEPTION_HANDLERS = {
    ConfigurationError: 500,
    ImageNotFoundError: 404,
    ImageProcessingError: 500,
    InvalidParameterError: 400,
    DirectoryAccessError: 500,
    UnsupportedFormatError: 400,
    CacheError: 500,
}