import streamlit as st
from groq import Groq
import base64
import os
import re
import sys
from io import StringIO
import contextlib

# --- 頁面設定 ---
st.set_page_config(page_title="電工機械解題王 (V4.0 運算增強版)", layout="centered")

st.title("⚡ 電工機械解題王 (V4.0)")
st.caption("🚀 結合 AI 邏輯分析 + Python 精確運算")

# --- 自動讀取鑰匙 ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.warning("⚠️ 尚未偵測到 API Key")
    api_key = st.sidebar.text_input("請輸入 Groq API Key", type="password")

# --- 函數：處理圖片 ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- 函數：執行 AI 產生的 Python 程式碼 ---
def execute_ai_code(code_str):
    # 建立一個捕捉輸出的緩衝區
    output_buffer = StringIO()
    
    try:
        # 重新導向 stdout，這樣 print() 的結果才會被我們抓到
        with contextlib.redirect_stdout(output_buffer):
            # 建立一個安全的執行環境 (字典)
            exec_globals = {}
            exec(code_str, exec_globals)
        return output_buffer.getvalue()
    except Exception as e:
        return f"運算錯誤: {str(e)}"

# --- V4.0 核心指令：要求 AI 寫程式 ---
system_prompt = """
你是一位精通 Python 的電工機械教師。
你的任務是：
1. 分析圖片中的題目，提取所有已知條件 (Given)。
2. 判斷題型 (例如：直流機、變壓器)。
3. **不要自己心算**，請撰寫一段完整的 **Python 程式碼** 來計算答案。

**Python 程式碼要求**：
- 將所有已知數定義為變數 (注意單位換算，如 cm 轉 m，rpm 轉 rad/s)。
- 定義公式並進行計算。
- **最後一步務必使用 `print()` 函數印出最終答案與單位**。
- 程式碼必須包含在 markdown區塊中，例如：
```python
P = 4
N = 800
...
print(f"答案: {E} V")
