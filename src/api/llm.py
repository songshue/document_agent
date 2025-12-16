
from email import message
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
import base64
from markitdown import MarkItDown
import os
import json

# def image_to_base64_data_url(image_path: str) -> str:
#     """
#     将本地图片文件转换为 Base64 Data URL
#     支持 PNG, JPG, JPEG, GIF 等常见格式
#     """
#     if not os.path.isfile(image_path):
#         raise FileNotFoundError(f"Image file not found: {image_path}")
    
#     # 获取文件扩展名以确定 MIME 类型
#     ext = os.path.splitext(image_path)[1].lower()
#     mime_type = {
#         ".png": "image/png",
#         ".jpg": "image/jpeg",
#         ".jpeg": "image/jpeg",
#         ".gif": "image/gif",
#         ".webp": "image/webp"
#     }.get(ext, "image/png")  # 默认为 png
    
#     with open(image_path, "rb") as image_file:
#         encoded_str = base64.b64encode(image_file.read()).decode("utf-8")
    
#     return f"data:{mime_type};base64,{encoded_str}"
class OpenAIVisionClient:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"),
                              base_url=os.getenv("LLM_BASE_URL"))
        self.model = os.getenv("LLM_MODEL_OCR")
    
    def complete(self, messages):
        print("\n[DEBUG] Messages received by MarkItDown:")
        print(json.dumps(messages, indent=2, ensure_ascii=False))
        print("[DEBUG] Model:", self.model)
        
        # 确保消息格式正确
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    # 为了兼容MarkItDown的直接调用，实现chat.completions.create接口
    class Chat:
        def __init__(self, vision_client):
            self.vision_client = vision_client
        
        class Completions:
            def __init__(self, chat_instance):
                self.chat_instance = chat_instance
            
            def create(self, model, messages, **kwargs):
                
                # 使用vision_client的client直接调用OpenAI API
                response = self.chat_instance.vision_client.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return response
        
        @property
        def completions(self):
            return self.Completions(self)
    
    @property
    def chat(self):
        return self.Chat(self)

if __name__ == "__main__":
    
    # 创建客户端
    client = OpenAIVisionClient()
    
    # 测试MarkItDown
    print("\n[DEBUG] 测试MarkItDown:")
    try:
        # 创建MarkItDown实例，确保传递llm_model
        md = MarkItDown(llm_client=client, llm_model=client.model)
        
        
        # 转换图片，传递自定义提示词
        custom_prompt = "请准确提取这张图片中的所有文字内容，不要解释，不要总结，只输出原文，格式为md格式。"
        result = md.convert(r"C:\Users\32670\Desktop\wechat_2025-12-15_094109_180.png", llm_prompt=custom_prompt)
        

        
        if hasattr(result, 'metadata'):
            print(f"[DEBUG] Metadata: {result.metadata}")
        if result.text_content.strip():
            print(f"[DEBUG] 提取到有效文字内容: {result.text_content.strip()}")
        else:
            print(f"[DEBUG] 未提取到有效文字内容")
            
    except Exception as e:
        print(f"[DEBUG] MarkItDown转换失败: {e}")
        import traceback
        traceback.print_exc()
