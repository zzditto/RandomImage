# 贡献指南

感谢您考虑为随机图片服务项目做贡献！

## 📋 如何贡献

### 报告Bug
- 使用GitHub Issues报告bug
- 请提供详细的复现步骤
- 包含环境信息（Python版本、操作系统等）

### 提交功能请求
- 清晰描述您希望添加的功能
- 解释该功能解决的问题
- 提供使用场景示例

### 代码贡献

#### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/yourusername/random-image-service.git
cd random-image-service

# 安装依赖
uv sync

# 安装开发依赖
uv pip install -e ".[dev]"
```

#### 代码规范
- 遵循PEP 8编码规范
- 使用类型提示
- 编写docstring文档
- 保持代码简洁易读

#### 测试
```bash
# 运行测试
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov=src/random_image
```

#### 提交Pull Request
1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📁 项目结构

```
src/random_image/
├── __init__.py
├── main.py          # 应用入口
├── config.py        # 配置管理
├── models.py        # 数据模型
├── exceptions.py    # 异常定义
├── api/             # API层
├── services/        # 业务逻辑层
├── utils/           # 工具层
└── tests/           # 测试文件
```

## 🎯 开发重点

我们特别欢迎以下方面的贡献：
- 性能优化
- 新的图片处理算法
- 更多的配置选项
- 文档改进
- 测试用例补充

## 📝 代码审查标准

- 代码必须通过所有测试
- 需要适当的文档和注释
- 遵循现有的代码风格
- 不引入安全漏洞

## 🤝 行为准则

请保持友善和专业的态度，尊重所有贡献者。

## 📞 联系方式

如有疑问，请通过以下方式联系：
- GitHub Issues
- 项目维护者邮箱

感谢您的贡献！