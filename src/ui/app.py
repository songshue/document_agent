#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文档问答助手 - FastAPI后端

负责提供API端点和静态文件服务
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict, Any
import os
import tempfile
from src.assistant.learning_assistant import PDFLearningAssistant
from src.utils.parallel_processor import process_files_in_parallel

# 创建FastAPI应用
app = FastAPI(
    title="智能文档问答助手",
    description="基于HelloAgents的智能文档问答系统，支持多文件上传和并行处理",
    version="1.0.0"
)

# 全局助手实例
assistant_state = {"assistant": None}

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="src/ui/static"), name="static")

@app.post("/api/init_assistant")
def init_assistant(user_id: str = Form("web_user")) -> Dict[str, Any]:
    """初始化助手"""
    global assistant_state
    assistant_state["assistant"] = PDFLearningAssistant(user_id=user_id)
    return {"success": True, "message": f"✅ 助手已初始化 (用户: {user_id})"}

@app.post("/api/load_pdf")
def load_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """加载单个PDF文件"""
    global assistant_state
    if assistant_state["assistant"] is None:
        return {"success": False, "message": "❌ 请先初始化助手"}

    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file.file.read())
        temp_path = temp_file.name

    try:
        # 处理文件，传递原始文件名
        result = assistant_state["assistant"].load_document(temp_path, original_filename=file.filename)
        return result
    finally:
        # 删除临时文件
        os.unlink(temp_path)

@app.post("/api/load_pdf_parallel")
def load_pdf_parallel(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    """并行加载PDF文件"""
    global assistant_state
    if assistant_state["assistant"] is None:
        return {"success": False, "message": "❌ 请先初始化助手"}

    if not files:
        return {"success": False, "message": "❌ 请上传PDF文件"}

    temp_paths = []
    temp_to_original = {}
    try:
        # 保存所有临时文件并记录原始文件名
        for file in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file.file.read())
                temp_path = temp_file.name
                temp_paths.append(temp_path)
                temp_to_original[temp_path] = file.filename

        # 创建闭包函数来传递原始文件名
        def process_file_with_original(temp_path):
            original_filename = temp_to_original[temp_path]
            return assistant_state["assistant"].load_document(
                temp_path, 
                original_filename=original_filename
            )

        # 并行处理文件
        results = process_files_in_parallel(
            file_paths=temp_paths,
            process_func=process_file_with_original
        )

        return {"success": True, "results": results}
    finally:
        # 删除所有临时文件
        for temp_path in temp_paths:
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"删除临时文件 {temp_path} 失败: {e}")

@app.post("/api/chat")
def chat(message: str = Form(...), history: str = Form("[]")) -> Dict[str, Any]:
    """聊天功能"""
    import json
    global assistant_state
    if assistant_state["assistant"] is None:
        return {"success": False, "message": "❌ 请先初始化助手"}

    if not message.strip():
        return {"success": False, "message": "❌ 消息内容不能为空"}

    # 解析历史记录
    try:
        chat_history = json.loads(history)
    except json.JSONDecodeError:
        chat_history = []

    # 判断是技术问题还是回顾问题
    if any(keyword in message for keyword in ["之前", "学过", "回顾", "历史", "记得"]):
        # 回顾学习历程
        response = assistant_state["assistant"].recall(message)
        response = f"🧠 **学习回顾**\n\n{response}"
    else:
        # 技术问答
        response = assistant_state["assistant"].ask(message)
        response = f"💡 **回答**\n\n{response}"

    # 更新历史记录
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": response})
    return {"success": True, "response": response, "history": chat_history}

@app.post("/api/add_note")
def add_note(note_content: str = Form(...), concept: str = Form(None)) -> Dict[str, Any]:
    """添加笔记"""
    global assistant_state
    if assistant_state["assistant"] is None:
        return {"success": False, "message": "❌ 请先初始化助手"}

    if not note_content.strip():
        return {"success": False, "message": "❌ 笔记内容不能为空"}

    assistant_state["assistant"].add_note(note_content, concept)
    return {"success": True, "message": f"✅ 笔记已保存: {note_content[:50]}..."}

@app.get("/api/get_stats")
def get_stats() -> Dict[str, Any]:
    """获取统计信息"""
    global assistant_state
    if assistant_state["assistant"] is None:
        return {"success": False, "message": "❌ 请先初始化助手"}

    stats = assistant_state["assistant"].get_stats()
    return {"success": True, "stats": stats}

@app.post("/api/generate_report")
def generate_report() -> Dict[str, Any]:
    """生成报告"""
    global assistant_state
    if assistant_state["assistant"] is None:
        return {"success": False, "message": "❌ 请先初始化助手"}

    report = assistant_state["assistant"].generate_report(save_to_file=True)

    result = {
        "success": True,
        "message": "✅ 学习报告已生成",
        "report": {
            "session_info": report["session_info"],
            "learning_metrics": report["learning_metrics"]
        }
    }

    if "report_file" in report:
        result["report_file"] = report["report_file"]

    return result

@app.get("/")
def read_root():
    """根路径返回静态HTML文件"""
    return FileResponse("src/ui/static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.ui.app:app",
        host="0.0.0.0",
        port=7864,
        reload=True
    )
