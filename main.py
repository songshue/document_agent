#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文档问答助手 - 基于HelloAgents的智能文档问答系统

这是一个完整的PDF学习助手应用，支持：
- 加载PDF文档并构建知识库
- 智能问答（基于RAG）
- 学习历程记录（基于Memory）
- 学习回顾和报告生成

应用采用模块化架构，分为以下核心模块：
- src/assistant/learning_assistant.py: 核心学习助手类
- src/ui/app.py: FastAPI后端和静态文件服务
- src/utils/parallel_processor.py: 并行处理工具
"""

import uvicorn
from dotenv import load_dotenv
from src.api.app import app

# 加载环境变量
load_dotenv()


def main():
    """主函数 - 启动FastAPI Web服务"""
    print("\n" + "="*60)
    print("智能文档问答助手")
    print("="*60)
    print("\n")

    # 启动FastAPI应用
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7866,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()