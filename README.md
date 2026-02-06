# 随机图片服务

一个基于FastAPI的随机图片获取和智能压缩服务，支持多种图片格式处理和高效的流量优化。

## 功能特性

- 🎲 **随机图片获取** - 从指定目录中随机选择图片
- 🗜️ **智能压缩** - 根据图片大小自动调整压缩质量，显著减少流量消耗
- 🔄 **多种格式支持** - 支持JPEG、PNG、WEBP、BMP、TIFF等多种格式
- ⚡ **缓存优化** - 内置LRU缓存机制，提高重复请求响应速度
- 🛠️ **灵活配置** - 支持环境变量配置，易于部署和定制
- 📊 **监控统计** - 提供详细的性能统计和健康检查接口

## 快速开始

### 环境要求

- Python >= 3.11
- uv 包管理器

### 安装依赖

```bash
# 使用 uv 安装依赖
uv sync

# 或者使用传统方式
pip install -e .
```

### 配置环境

创建 `.env` 文件或设置环境变量：

```bash
# 服务器配置
HOST=127.0.0.1
PORT=8000
DEBUG=False

# 图片目录配置
IMAGE_DIR=/path/to/your/images

# 压缩配置
COMPRESSION_QUALITY=85
OUTPUT_FORMAT=WEBP
PROGRESSIVE=True

# 缓存配置
ENABLE_CACHE=True
CACHE_MAX_SIZE=100
```

### 运行服务

```bash
# 开发模式
uv run python -m src.random_image.main

# 生产模式
uvicorn src.random_image.main:app --host 0.0.0.0 --port 8000
```

服务启动后访问：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health
- 主要接口：http://localhost:8000/api/v1/

## API 接口

### 获取随机图片

```http
GET /api/v1/
```

**查询参数：**
- `width` (int, 可选): 目标宽度（像素）
- `height` (int, 可选): 目标高度（像素）
- `quality` (int, 可选): 压缩质量（60-95）
- `format` (string, 可选): 输出格式（JPEG, PNG, WEBP）
- `progressive` (bool, 默认true): 是否启用渐进式JPEG
- `preserve_aspect_ratio` (bool, 默认true): 是否保持宽高比

**示例：**
```bash
# 获取默认大小的随机图片
curl http://localhost:8000/api/v1/

# 获取指定宽度的图片
curl "http://localhost:8000/api/v1/?width=1024"

# 指定压缩质量和格式
curl "http://localhost:8000/api/v1/?quality=75&format=WEBP"
```

### 健康检查

```http
GET /api/v1/health
```

返回服务运行状态和基本统计信息。

### 刷新图片列表

```http
POST /api/v1/refresh
```

手动重新扫描图片目录，更新可用图片列表。

### 获取统计信息

```http
GET /api/v1/stats
```

返回缓存命中率、处理统计等性能指标。

### 获取系统信息

```http
GET /api/v1/info
```

返回支持的格式、配置范围等系统信息。

## 配置说明

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `HOST` | 127.0.0.1 | 服务器监听地址 |
| `PORT` | 8000 | 服务器端口 |
| `DEBUG` | False | 调试模式 |
| `IMAGE_DIR` | /Users/zz/Pictures | 图片目录路径 |
| `COMPRESSION_QUALITY` | 85 | 默认压缩质量 |
| `OUTPUT_FORMAT` | WEBP | 默认输出格式 |
| `PROGRESSIVE` | True | 启用渐进式JPEG |
| `ENABLE_CACHE` | True | 启用缓存 |
| `CACHE_MAX_SIZE` | 100 | 缓存最大条目数 |
| `MAX_IMAGE_SIZE` | 2000 | 最大图片尺寸（像素） |

## 性能优化

### 智能压缩算法

服务采用智能压缩策略：
- 大图片（>5MB）：降低15个质量点
- 中等图片（>1MB）：降低5个质量点
- 小图片（≤1MB）：提升5个质量点

### 缓存机制

内置LRU缓存系统：
- 自动缓存处理过的图片
- 根据参数组合生成唯一缓存键
- 可配置缓存大小和启用状态

## 部署指南

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install uv
RUN uv sync

EXPOSE 8000
CMD ["uvicorn", "src.random_image.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### systemd 服务

创建 `/etc/systemd/system/random-image.service`：

```ini
[Unit]
Description=Random Image Service
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=/path/to/random_image
ExecStart=/usr/local/bin/uv run python -m src.random_image.main
Restart=always

[Install]
WantedBy=multi-user.target
```

## 开发指南

### 项目结构

```
src/random_image/
├── __init__.py
├── main.py          # 应用入口
├── config.py        # 配置管理
├── models.py        # 数据模型
├── exceptions.py    # 异常定义
├── api/             # API层
│   ├── __init__.py
│   ├── routes.py    # 路由定义
│   └── dependencies.py  # 依赖注入
├── services/        # 业务逻辑层
│   ├── __init__.py
│   └── image_service.py
├── utils/           # 工具层
│   ├── __init__.py
│   └── image_processor.py
└── tests/           # 测试文件
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_api.py

# 生成覆盖率报告
uv run pytest --cov=src/random_image
```

### 代码质量

```bash
# 代码格式化
uv run black src/

# 代码检查
uv run ruff check src/
```

## 故障排除

### 常见问题

1. **找不到图片文件**
   - 检查 `IMAGE_DIR` 配置是否正确
   - 确认目录权限是否允许读取
   - 验证图片格式是否受支持

2. **内存占用过高**
   - 调整 `CACHE_MAX_SIZE` 参数
   - 降低 `MAX_IMAGE_SIZE` 限制
   - 考虑禁用缓存功能

3. **响应速度慢**
   - 检查磁盘I/O性能
   - 增加缓存命中率
   - 优化图片目录结构

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

*Powered by FastAPI & Pillow*