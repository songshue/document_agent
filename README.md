# 智能文档问答助手

基于HelloAgents的智能文档问答系统，支持多文件上传和并行处理，提供智能问答和学习历程记录功能。

## 功能特性

### 📚 核心功能
- **多文件上传**：支持单次上传多个PDF文档
- **并行处理**：利用并行计算提高文档处理效率
- **智能问答**：基于RAG技术实现文档内容的智能问答
- **学习记忆**：记录学习历程，支持回顾和报告生成
- **学习报告**：自动生成学习统计和报告

### 🏗️ 架构设计
- **模块化设计**：清晰的代码结构，便于维护和扩展
- **高性能**：基于FastAPI的Web后端，支持异步请求
- **可扩展性**：支持自定义工具和插件
- **用户隔离**：不同用户数据相互隔离

### 🎨 用户体验
- **现代化UI**：自定义HTML/CSS/JS界面
- **响应式设计**：适配不同设备尺寸
- **实时反馈**：操作结果实时显示
- **友好的交互**：直观的操作流程

## 安装指南

### 1. 环境要求
- Python 3.8+ 
- pip 20.0+

### 2. 安装步骤

#### 克隆项目
```bash
git clone <项目地址>
cd document_agent
```

#### 安装依赖
使用清华镜像加速安装：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

#### 配置环境变量
编辑 `.env` 文件，配置必要的环境变量：
```bash
# 复制示例配置
# cp .env.example .env

# 编辑 .env 文件
vim .env
```

主要配置项说明：
- `OPENAI_API_KEY`：OpenAI API密钥
- `LLM_BASE_URL`：大语言模型API地址
- `LLM_MODEL_ID`：使用的模型ID
- `QDRANT_URL`：Qdrant向量数据库地址
- `QDRANT_API_KEY`：Qdrant API密钥
- `NEO4J_URI`：Neo4j图数据库地址
- `NEO4J_USERNAME`：Neo4j用户名
- `NEO4J_PASSWORD`：Neo4j密码
- `EMBED_API_KEY`：嵌入模型API密钥

### 3. 启动应用

#### 方式一：直接运行
```bash
python main.py
```

#### 方式二：使用uvicorn直接启动
```bash
uvicorn src.ui.app:app --host 0.0.0.0 --port 7864
```

应用将在 `http://localhost:7864` 启动。

## 使用说明

### 1. 访问应用
在浏览器中输入 `http://localhost:7864`，进入应用首页。

### 2. 初始化助手
首次使用需要初始化助手，系统会自动为您创建用户身份。

### 3. 上传PDF文档
- 点击「选择文件」按钮，选择一个或多个PDF文档
- 点击「上传并处理」按钮，系统将并行处理您的文档
- 等待处理完成，查看处理结果

### 4. 智能问答
- 在输入框中输入您的问题
- 点击「发送」按钮，或按回车键
- 等待系统生成回答
- 查看回答结果和相关文档引用

### 5. 添加学习笔记
- 在笔记输入框中输入笔记内容
- 点击「保存笔记」按钮
- 笔记将被保存到您的学习记忆中

### 6. 查看学习统计
- 点击「统计信息」按钮
- 查看学习时长、文档数量、提问次数等统计数据

### 7. 生成学习报告
- 点击「生成报告」按钮
- 系统将生成包含学习历程和统计数据的报告
- 报告将自动保存到本地

## 项目结构

```
document_agent/
├── src/                      # 源代码目录
│   ├── assistant/            # 助手核心模块
│   │   └── learning_assistant.py  # 智能文档问答助手类
│   ├── ui/                   # 前端界面模块
│   │   ├── static/           # 静态资源
│   │   │   ├── index.html    # 主页面
│   │   │   ├── script.js     # JavaScript代码
│   │   │   └── styles.css    # CSS样式
│   │   └── app.py            # FastAPI应用
│   └── utils/                # 工具模块
│       └── parallel_processor.py  # 并行处理工具
├── memory_data/              # 记忆数据目录
│   └── memory.db             # 记忆数据库
├── .env                      # 环境变量配置
├── main.py                   # 应用入口
├── requirements.txt          # 依赖列表
└── README.md                 # 项目说明文档
```

## 核心模块说明

### 1. learning_assistant.py
- **PDFLearningAssistant类**：智能文档问答助手的核心类
- **功能**：PDF加载、知识库构建、智能问答、学习记忆管理
- **主要方法**：
  - `load_document()`：加载PDF文档
  - `ask()`：智能问答
  - `add_note()`：添加学习笔记
  - `recall()`：回顾学习历程
  - `get_stats()`：获取学习统计
  - `generate_report()`：生成学习报告

### 2. app.py
- **FastAPI应用**：提供Web API和静态文件服务
- **主要API端点**：
  - `/api/init_assistant`：初始化助手
  - `/api/load_pdf`：加载单个PDF文件
  - `/api/load_pdf_parallel`：并行加载PDF文件
  - `/api/chat`：聊天功能
  - `/api/add_note`：添加笔记
  - `/api/get_stats`：获取统计信息
  - `/api/generate_report`：生成报告

### 3. parallel_processor.py
- **并行处理工具**：用于并行处理多个PDF文档
- **主要功能**：提高文档处理效率，减少等待时间

## 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| Web框架 | FastAPI | 0.104.0+ | 构建Web API |
| ASGI服务器 | Uvicorn | 0.24.0+ | 运行FastAPI应用 |
| 环境管理 | python-dotenv | 1.0.0+ | 加载环境变量 |
| 核心功能库 | hello_agents | 0.1.0+ | 提供RAG和Memory工具 |
| 数据验证 | Pydantic | 2.0.0+ | 数据验证和序列化 |
| 表单处理 | python-multipart | 0.0.6+ | 处理文件上传 |

## 配置说明

### 大语言模型配置
```
OPENAI_API_KEY="your_openai_api_key"
LLM_BASE_URL="https://api.example.com/v1"
LLM_MODEL_ID="gpt-4.1-mini"
LLM_TIMEOUT=60
```

### 向量数据库配置
```
QDRANT_URL="https://your-qdrant-instance.cloud.qdrant.io:6333"
QDRANT_API_KEY="your_qdrant_api_key"
QDRANT_COLLECTION=rag_knowledge_base
QDRANT_VECTOR_SIZE=384
QDRANT_DISTANCE=cosine
QDRANT_TIMEOUT=30
```

### 图数据库配置
```
NEO4J_URI="neo4j+s://your-neo4j-instance.databases.neo4j.io"
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD="your_neo4j_password"
NEO4J_DATABASE=neo4j
NEO4J_MAX_CONNECTION_LIFETIME=3600
NEO4J_MAX_CONNECTION_POOL_SIZE=50
NEO4J_CONNECTION_TIMEOUT=60
```

### 嵌入模型配置
```
EMBED_MODEL_TYPE=dashscope
EMBED_MODEL_NAME="text-embedding-v3"
EMBED_API_KEY="your_embed_api_key"
EMBED_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

## 常见问题

### 1. 应用无法启动
- 检查Python版本是否符合要求
- 检查依赖是否正确安装
- 检查端口是否被占用
- 检查环境变量配置是否正确

### 2. 文档无法加载
- 检查文件格式是否为PDF
- 检查文件大小是否超过限制
- 检查网络连接是否正常
- 检查向量数据库配置是否正确

### 3. 问答结果不准确
- 检查文档是否正确加载
- 尝试使用更精确的问题描述
- 检查LLM模型配置是否正确
- 检查嵌入模型配置是否正确

### 4. 应用运行缓慢
- 检查服务器资源使用情况
- 减少同时处理的文档数量
- 优化环境配置
- 考虑使用更强大的硬件

## 开发指南

### 1. 代码结构
- `src/assistant/`：核心功能模块
- `src/ui/`：Web界面和API
- `src/utils/`：工具函数
- `memory_data/`：数据存储

### 2. 扩展功能
- 可以在 `src/assistant/` 目录下添加新的工具类
- 可以在 `src/ui/app.py` 中添加新的API端点
- 可以在 `src/ui/static/` 目录下修改前端界面

### 3. 测试
```bash
# 运行单元测试
python -m pytest

# 运行API测试
python -m pytest tests/api/
```

### 4. 代码规范
```bash
# 检查代码规范
flake8

# 自动格式化代码
black .
```


