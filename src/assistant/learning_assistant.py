#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文档问答助手 - 核心类

负责PDF文档加载、知识库构建、智能问答和学习记忆管理
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from hello_agents.tools import MemoryTool, RAGTool

# 导入图片处理相关模块
from src.api.llm import OpenAIVisionClient
from markitdown import MarkItDown


class PDFLearningAssistant:
    """智能文档问答助手"""

    def __init__(self, user_id: str = "default_user"):
        """初始化学习助手

        Args:
            user_id: 用户ID，用于隔离不同用户的数据
        """
        self.user_id = user_id
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 初始化工具
        self.memory_tool = MemoryTool(user_id=user_id)
        self.rag_tool = RAGTool(rag_namespace=f"pdf_{user_id}")

        # 初始化图片处理工具
        self.ocr_client = OpenAIVisionClient()
        self.markitdown = MarkItDown(llm_client=self.ocr_client, llm_model=self.ocr_client.model)

        # 学习统计
        self.stats = {
            "session_start": datetime.now(),
            "documents_loaded": 0,
            "images_loaded": 0,
            "questions_asked": 0,
            "concepts_learned": 0
        }

        # 当前加载的文档
        self.current_documents = []
        # 临时文件名到原始文件名的映射
        self.temp_to_original = {}

    def load_document(self, file_path: str, original_filename: Optional[str] = None) -> Dict[str, Any]:
        """加载文档（PDF或图片）到知识库

        Args:
            file_path: 文件路径（支持PDF和图片）
            original_filename: 原始文件名（可选）

        Returns:
            Dict: 包含success和message的结果
        """
        if not os.path.exists(file_path):
            return {"success": False, "message": f"文件不存在: {file_path}"}

        # 获取文件扩展名和文件名
        temp_doc_name = os.path.basename(file_path)
        doc_name = original_filename if original_filename else temp_doc_name
        ext = os.path.splitext(doc_name)[1].lower() if doc_name else os.path.splitext(file_path)[1].lower()

        # 处理图片文件
        if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            return self.process_image(file_path, doc_name)
        # 处理PDF文件
        elif ext == ".pdf":
            start_time = time.time()

            try:
                # 使用RAG工具处理PDF
                result = self.rag_tool.execute(
                    "add_document",
                    file_path=file_path,
                    chunk_size=1000,
                    chunk_overlap=200
                )

                process_time = time.time() - start_time

                # 存储临时文件名到原始文件名的映射
                self.temp_to_original[temp_doc_name] = doc_name
                self.current_documents.append(doc_name)
                self.stats["documents_loaded"] += 1

                # 记录到学习记忆
                self.memory_tool.execute(
                    "add",
                    content=f"加载了文档《{doc_name}》",
                    memory_type="episodic",
                    importance=0.9,
                    event_type="document_loaded",
                    session_id=self.session_id
                )

                return {
                    "success": True,
                    "message": f"PDF文档加载成功！(耗时: {process_time:.1f}秒)",
                    "document": doc_name
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"PDF文档加载失败: {str(e)}"
                }
        else:
            return {
                "success": False,
                "message": f"不支持的文件类型: {ext}，仅支持PDF和图片文件"
            }

    def ask(self, question: str, use_advanced_search: bool = True) -> str:
        """向文档提问

        Args:
            question: 用户问题
            use_advanced_search: 是否使用高级检索（MQE + HyDE）

        Returns:
            str: 答案
        """
        if not self.current_documents:
            return "⚠️ 请先加载文档！使用 load_document() 方法加载PDF文档。"

        # 记录问题到工作记忆
        self.memory_tool.execute(
            "add",
            content=f"提问: {question}",
            memory_type="working",
            importance=0.6,
            session_id=self.session_id
        )

        # 使用RAG检索答案
        answer = self.rag_tool.execute(
            "ask",
            question=question,
            limit=5,
            enable_advanced_search=use_advanced_search,
            enable_mqe=use_advanced_search,
            enable_hyde=use_advanced_search
        )
        
        # 将答案中的临时文件名替换为原始文件名
        for temp_name, original_name in self.temp_to_original.items():
            answer = answer.replace(temp_name, original_name)

        # 记录到情景记忆
        self.memory_tool.execute(
            "add",
            content=f"关于'{question}'的学习",
            memory_type="episodic",
            importance=0.7,
            event_type="qa_interaction",
            session_id=self.session_id
        )

        self.stats["questions_asked"] += 1
        return answer

    def add_note(self, content: str, concept: Optional[str] = None):
        """添加学习笔记

        Args:
            content: 笔记内容
            concept: 相关概念（可选）
        """
        self.memory_tool.execute(
            "add",
            content=content,
            memory_type="semantic",
            importance=0.8,
            concept=concept or "general",
            session_id=self.session_id
        )

        self.stats["concepts_learned"] += 1

    def recall(self, query: str, limit: int = 5) -> str:
        """回顾学习历程

        Args:
            query: 查询关键词
            limit: 返回结果数量

        Returns:
            str: 相关记忆
        """
        result = self.memory_tool.execute(
            "search",
            query=query,
            limit=limit
        )
        return result

    def get_stats(self) -> Dict[str, Any]:
        """获取学习统计

        Returns:
            Dict: 统计信息
        """
        duration = (datetime.now() - self.stats["session_start"]).total_seconds()

        return {
            "会话时长": f"{duration:.0f}秒",
            "加载文档": self.stats["documents_loaded"],
            "加载图片": self.stats["images_loaded"],
            "提问次数": self.stats["questions_asked"],
            "学习笔记": self.stats["concepts_learned"],
            "当前文档": ", ".join(self.current_documents) if self.current_documents else "未加载"
        }

    def process_image(self, file_path: str, doc_name: str) -> Dict[str, Any]:
        """处理图片文件，使用OCR提取文字并添加到知识库

        Args:
            file_path: 图片文件路径
            doc_name: 文档名称

        Returns:
            Dict: 包含success和message的结果
        """
        import time
        start_time = time.time()

        try:
            # 使用MarkItDown处理图片，仅返回原文
            custom_prompt = "请准确提取这张图片中的所有文字内容，不要解释，不要总结，只输出原文"
            result = self.markitdown.convert(file_path, llm_prompt=custom_prompt)
            
            # 获取提取的文字内容
            text_content = result.text_content
            if not text_content.strip():
                return {
                    "success": False,
                    "message": "图片文字提取失败，未获取到有效内容"
                }
            
            # 将提取的文字添加到知识库
            self.rag_tool.execute(
                "add_text",
                text=text_content,
                document_id=doc_name
            )
            
            process_time = time.time() - start_time
            
            # 更新统计信息
            self.temp_to_original[os.path.basename(file_path)] = doc_name
            self.current_documents.append(doc_name)
            self.stats["images_loaded"] += 1
            
            # 记录到学习记忆
            self.memory_tool.execute(
                "add",
                content=f"加载了图片《{doc_name}》",
                memory_type="episodic",
                importance=0.9,
                event_type="image_loaded",
                session_id=self.session_id
            )
            
            return {
                "success": True,
                "message": f"图片处理成功！(耗时: {process_time:.1f}秒)，提取文字长度: {len(text_content)}字符",
                "document": doc_name
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"图片处理失败: {str(e)}"
            }

    def generate_report(self, save_to_file: bool = True) -> Dict[str, Any]:
        """生成学习报告

        Args:
            save_to_file: 是否保存到文件

        Returns:
            Dict: 学习报告
        """
        # 获取记忆摘要
        memory_summary = self.memory_tool.execute("summary", limit=10)

        # 获取RAG统计
        rag_stats = self.rag_tool.execute("stats")

        # 生成报告
        duration = (datetime.now() - self.stats["session_start"]).total_seconds()
        report = {
            "session_info": {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "start_time": self.stats["session_start"].isoformat(),
                "duration_seconds": duration
            },
            "learning_metrics": {
                "documents_loaded": self.stats["documents_loaded"],
                "questions_asked": self.stats["questions_asked"],
                "concepts_learned": self.stats["concepts_learned"]
            },
            "memory_summary": memory_summary,
            "rag_status": rag_stats
        }

        # 保存到文件
        if save_to_file:
            report_file = f"learning_report_{self.session_id}.json"
            try:
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2, default=str)
                report["report_file"] = report_file
            except Exception as e:
                report["save_error"] = str(e)

        return report
