// 聊天历史记录
let chat_history = [];

// 标签页切换功能
function openTab(evt, tabName) {
    // 获取所有标签页内容和按钮
    const tabContents = document.getElementsByClassName("tab-content");
    const tabBtns = document.getElementsByClassName("tab-btn");

    // 隐藏所有标签页内容
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].classList.remove("active");
    }

    // 移除所有按钮的活跃状态
    for (let i = 0; i < tabBtns.length; i++) {
        tabBtns[i].classList.remove("active");
    }

    // 显示当前标签页内容并激活按钮
    document.getElementById(tabName).classList.add("active");
    evt.currentTarget.classList.add("active");
}

// 获取当前时间格式化字符串
function getCurrentTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');
    return `[${hours}:${minutes}:${seconds}]`;
}

// 显示消息到输出区域
function showMessage(elementId, message, isError = false) {
    const element = document.getElementById(elementId);
    // 渲染markdown格式的内容
    const renderedMessage = renderMarkdown(message);
    element.innerHTML = `${getCurrentTime()} ${renderedMessage}`;
    element.style.color = isError ? "red" : "black";
}

// 初始化助手
async function initAssistant() {
    const user_id = document.getElementById("user_id").value;
    showMessage("init_output", "初始化中...");

    try {
        const response = await fetch("/api/init_assistant", {
            method: "POST",
            body: new URLSearchParams({
                "user_id": user_id
            })
        });
        const result = await response.json();
        showMessage("init_output", result.message);
    } catch (error) {
        showMessage("init_output", `❌ 初始化失败: ${error.message}`, true);
    }
}

// 文档加载（根据文件数量自动选择加载方式）
async function loadDocuments() {
    const fileInput = document.getElementById("pdf_upload");
    if (!fileInput.files || fileInput.files.length === 0) {
        showMessage("load_output", "❌ 请选择PDF文件", true);
        return;
    }

    const files = fileInput.files;
    const fileCount = files.length;
    let timer = null;
    let elapsedTime = 0;
    
    try {
        if (fileCount === 1) {
            // 单文件加载
            const formData = new FormData();
            formData.append("file", files[0]);
            
            // 启动计时器
            elapsedTime = 0;
            timer = setInterval(() => {
                elapsedTime += 1;
                showMessage("load_output", `加载中... (已耗时: ${elapsedTime}.0秒)`);
            }, 1000);

            const startTime = Date.now();
            const response = await fetch("/api/load_pdf", {
                method: "POST",
                body: formData
            });
            const endTime = Date.now();
            
            // 清除计时器
            clearInterval(timer);
            const totalTime = ((endTime - startTime) / 1000).toFixed(1);

            const result = await response.json();
            if (result.success) {
                showMessage("load_output", `✅ ${result.message} (耗时: ${totalTime}秒)\n📄 文档: ${result.document}`);
            } else {
                showMessage("load_output", result.message, true);
            }
        } else {
            // 多文件并行加载 - 为每个文件创建计时器和状态
            const fileStatus = [];
            const fileTimers = [];
            
            // 初始化每个文件的状态
            for (let i = 0; i < fileCount; i++) {
                fileStatus.push({ fileName: files[i].name, time: 0, status: "加载中" });
            }
            
            // 启动所有文件的计时器
            for (let i = 0; i < fileCount; i++) {
                const index = i;
                fileTimers[i] = setInterval(() => {
                    fileStatus[index].time += 1;
                    updateMultiFileStatus(fileStatus);
                }, 1000);
            }
            
            const startTime = Date.now();
            
            // 准备多文件上传
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append("files", files[i]);
            }

            const response = await fetch("/api/load_pdf_parallel", {
                method: "POST",
                body: formData
            });
            
            // 清除所有计时器
            fileTimers.forEach(timer => clearInterval(timer));
            const endTime = Date.now();
            
            const result = await response.json();
            if (result.success) {
                // 更新最终结果
                const formattedResults = result.results.map((res, index) => {
                    const fileIndex = index;
                    const totalTime = ((endTime - startTime) / 1000).toFixed(1);
                    if (res.success) {
                        return `✅ ${res.message} (耗时: ${totalTime}秒)\n📄 文档: ${res.document}`;
                    } else {
                        return res.message;
                    }
                });
                showMessage("load_output", formattedResults.join("\n\n"));
            } else {
                showMessage("load_output", result.message, true);
            }
        }
    } catch (error) {
        showMessage("load_output", `❌ 加载失败: ${error.message}`, true);
    }
}

// HTML转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Markdown简单渲染函数
function renderMarkdown(text) {
    // 先对文本进行HTML转义，防止安全问题
    let html = escapeHtml(text);
    
    // 处理粗体 **text** -> <strong>text</strong>
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 处理斜体 *text* -> <em>text</em>
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // 处理列表项 - text -> <li>text</li>
    html = html.replace(/^- (.*$)/gm, '<li>$1</li>');
    // 包裹列表项为ul
    html = html.replace(/(<li>.*?<\/li>)+/gs, '<ul>$&</ul>');
    
    // 处理有序列表项 1. text -> <li>text</li>
    html = html.replace(/^\d+\. (.*$)/gm, '<li>$1</li>');
    // 包裹有序列表项为ol
    html = html.replace(/(<li>.*?<\/li>)+/gs, '<ol>$&</ol>');
    
    // 处理换行
    html = html.replace(/\n/g, '<br>');
    
    // 处理标题 # 到 ######
    html = html.replace(/^(#{1,6}) (.*$)/gm, (match, hashes, content) => {
        const level = hashes.length;
        return `<h${level}>${content}</h${level}>`;
    });
    
    // 处理引用 > text -> <blockquote>text</blockquote>
    html = html.replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>');
    
    // 处理代码块 ```code``` -> <pre><code>code</code></pre>
    html = html.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');
    
    // 处理行内代码 `code` -> <code>code</code>
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');
    
    return html;
}

// 添加聊天消息到界面
function addChatMessage(role, content) {
    const chatHistory = document.getElementById("chat_history");
    const messageDiv = document.createElement("div");
    messageDiv.className = `chat-message ${role}`;
    
    // 添加时间戳到聊天消息
    const timestamp = getCurrentTime();
    
    // 渲染markdown格式的内容
    const renderedContent = renderMarkdown(content);
    messageDiv.innerHTML = `<div class="message-timestamp">${timestamp}</div>${renderedContent}`;
    
    chatHistory.appendChild(messageDiv);
    // 滚动到底部
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// 更新多文件加载状态
function updateMultiFileStatus(fileStatus) {
    let statusHtml = `加载中... (共${fileStatus.length}个文件)\n\n`;
    fileStatus.forEach((file, index) => {
        // 对文件名和状态进行HTML转义
        const escapedFileName = escapeHtml(file.fileName);
        const escapedStatus = escapeHtml(file.status);
        statusHtml += `📄 文档 ${index + 1}: ${escapedFileName}\n`;
        statusHtml += `   ${escapedStatus} (已耗时: ${file.time}.0秒)\n\n`;
    });
    showMessage("load_output", statusHtml);
}

// 发送消息
async function sendMessage() {
    const msgInput = document.getElementById("msg_input");
    const message = msgInput.value.trim();
    if (!message) return;

    // 清空输入框
    msgInput.value = "";

    // 添加用户消息到界面
    addChatMessage("user", message);
    chat_history.push({ "role": "user", "content": message });

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            body: new URLSearchParams({
                "message": message,
                "history": JSON.stringify(chat_history)
            })
        });

        const result = await response.json();
        console.log("result:", result);
        if (result.success) {
            // 添加助手消息到界面
            addChatMessage("assistant", result.response);
            chat_history = result.history;
        } else {
            addChatMessage("assistant", result.message);
        }
    } catch (error) {
        addChatMessage("assistant", `❌ 发送失败: ${error.message}`);
    }
}

// 设置示例问题
function setExample(text) {
    const msgInput = document.getElementById("msg_input");
    msgInput.value = text;
}

// 添加笔记
async function addNote() {
    const noteContent = document.getElementById("note_content").value.trim();
    const concept = document.getElementById("concept_input").value.trim();

    if (!noteContent) {
        showMessage("note_output", "❌ 笔记内容不能为空", true);
        return;
    }

    showMessage("note_output", "保存中...");

    try {
        const response = await fetch("/api/add_note", {
            method: "POST",
            body: new URLSearchParams({
                "note_content": noteContent,
                "concept": concept
            })
        });

        const result = await response.json();
        showMessage("note_output", result.message);
        if (result.success) {
            // 清空输入框
            document.getElementById("note_content").value = "";
            document.getElementById("concept_input").value = "";
        }
    } catch (error) {
        showMessage("note_output", `❌ 保存失败: ${error.message}`, true);
    }
}

// 获取统计信息
async function getStats() {
    const statsOutput = document.getElementById("stats_output");
    statsOutput.innerHTML = "加载中...";

    try {
        const response = await fetch("/api/get_stats", {
            method: "GET"
        });

        const result = await response.json();
        if (result.success) {
            let statsHTML = "📊 **学习统计**\n\n";
            for (const [key, value] of Object.entries(result.stats)) {
                statsHTML += `- **${key}**: ${value}\n`;
            }
            statsOutput.innerHTML = renderMarkdown(statsHTML);
        } else {
            statsOutput.innerHTML = result.message;
        }
    } catch (error) {
        statsOutput.innerHTML = `❌ 获取失败: ${error.message}`;
    }
}

// 生成报告
async function generateReport() {
    showMessage("report_output", "生成中...");

    try {
        const response = await fetch("/api/generate_report", {
            method: "POST"
        });

        const result = await response.json();
        if (result.success) {
            let reportHTML = result.message + "\n\n";
            reportHTML += "**会话信息**\n";
            reportHTML += `- 会话时长: ${result.report.session_info.duration_seconds.toFixed(0)}秒\n`;
            reportHTML += `- 加载文档: ${result.report.learning_metrics.documents_loaded}\n`;
            reportHTML += `- 提问次数: ${result.report.learning_metrics.questions_asked}\n`;
            reportHTML += `- 学习笔记: ${result.report.learning_metrics.concepts_learned}\n`;

            if (result.report_file) {
                reportHTML += `\n💾 报告已保存至: ${result.report_file}`;
            }

            // 对报告内容进行markdown渲染
            const renderedReport = renderMarkdown(reportHTML);
            showMessage("report_output", renderedReport);
        } else {
            showMessage("report_output", result.message, true);
        }
    } catch (error) {
        showMessage("report_output", `❌ 生成失败: ${error.message}`, true);
    }
}

// 键盘事件监听
document.addEventListener("DOMContentLoaded", function() {
    // 聊天输入框回车发送
    const msgInput = document.getElementById("msg_input");
    if (msgInput) {
        msgInput.addEventListener("keypress", function(e) {
            if (e.key === "Enter") {
                sendMessage();
            }
        });
    }
});
