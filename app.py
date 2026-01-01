import streamlit as st
from groq import Groq
import base64
import os
import re
import sys
from io import StringIO
import contextlib

# --- 1. 頁面設定 ---
st.set_page_config(page_title="電工機械解題王 (V5.0)", layout="centered")

st.title("⚡ 電工機械解題王 (V5.0)")
st.caption("🚀 最終修正版：Llama 4 模型 + Python 運算驗證")

# --- 2. 自動讀取 API Key ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.warning("⚠️ 尚未偵測到 API Key")
    api_key = st.sidebar.text_input("請輸入 Groq API Key", type="password")

# --- 3. 核心函數定義 ---
def encode_image(uploaded_file):
    """將圖片轉為 Base64"""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def execute_ai_code(code_str):
    """執行 AI 的 Python 程式碼並捕捉輸出"""
    output_buffer = StringIO()
    try:
        with contextlib.redirect_stdout(output_buffer):
            exec_globals = {}
            exec(code_str, exec_globals)
        return output_buffer.getvalue()
    except Exception as e:
        return f"運算錯誤: {str(e)}"

# --- 4. 設定 AI 指令 (System Prompt) ---
# 注意：為了避免複製錯誤，我簡化了這裡的範例格式，功能完全不變
system_prompt = """
你是一位精通 Python 的電工機械教師。任務：
1. 分析圖片題目，提取已知條件。
2. 判斷題型。
3. **撰寫 Python 程式碼** 計算答案 (不要心算)。

**Python 程式碼要求**：
- 定義變數 (注意單位換算，如 cm 轉 m，rpm 轉 rad/s)。
- 列出公式進行計算。
- **最後一步務必使用 print() 函數印出最終答案與單位**。
- 程式碼必須包含在 markdown 代碼區塊中。

**陷阱提示**：
- 雙分疊繞 a=2P；單分疊繞 a=P；波繞 a=2m。
- 電壓調整率：超前用減(-)，滯後用加(+)。
- 變壓器阻抗換算：轉到高壓側要乘匝數比平方，轉到低壓側要除。

**輸出格式**：
1. 題目分析
2. 解題思路
3. Python 程式碼區塊
"""

# --- 5. 主程式邏輯 ---
uploaded_file = st.file_uploader("📸 拍照或上傳題目", type=["jpg", "png", "jpeg"])

if uploaded_file and api_key:
    st.image(uploaded_file, caption="預覽題目", use_container_width=True)
    
    if st.button("🚀 開始詳解 (啟動 Python 運算)", type="primary"):
        with st.spinner("AI 正在分析並撰寫運算程式..."):
            try:
                client = Groq(api_key=api_key)
                base64_image = encode_image(uploaded_file)
                
                # 發送請求
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": system_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                    # 使用最新的 Llama 4 Scout 模型
                    model="meta-llama/llama-4-scout-17b-16e-instruct", 
                    temperature=0.0,
                )
                
                full_response = chat_completion.choices[0].message.content
                
                # 顯示文字分析
                st.markdown("### 📝 題目分析與思路")
                st.markdown(full_response)
                
                # 提取並執行 Python 程式碼
                code_match = re.search(r'```python(.*?)```', full_response, re.DOTALL)
                
                if code_match:
                    code_to_run = code_match.group(1).strip()
                    
                    st.divider() 
                    st.markdown("### 💻 電腦精確運算結果")
                    st.info("以下是 AI 撰寫的運算程式，由系統自動執行：")
                    
                    st.code(code_to_run, language='python')
                    
                    calculated_result = execute_ai_code(code_to_run)
                    
                    if "運算錯誤" in calculated_result:
                        st.error(calculated_result)
                    else:
                        st.success(f"🧮 最終計算答案：\n\n{calculated_result}")
                else:
                    st.warning("⚠️ AI 未生成可執行的程式碼，請參考上方的文字分析。")
                
            except Exception as e:
                st.error(f"發生系統錯誤：{str(e)}")

elif uploaded_file and not api_key:
    st.error("請先設定 API Key")
