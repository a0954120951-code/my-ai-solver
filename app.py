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
特別注意陷阱：

看到「雙分疊繞」：a = 2 * P

看到「單分疊繞」：a = P

看到「波繞」：a = 2 * m

看到「超前/滯後」：電壓調整率公式中，超前用減號(-)，滯後用加號(+)。

輸出格式：

題目分析：列出條件。

解題思路：解釋選用的公式。

運算程式碼：提供 Python 代碼區塊。

(Streamlit 會自動執行你的代碼並顯示結果) """

--- 主程式 ---
uploaded_file = st.file_uploader("📸 拍照或上傳題目", type=["jpg", "png", "jpeg"])

if uploaded_file and api_key: st.image(uploaded_file, caption="預覽題目", use_container_width=True)

if st.button("🚀 開始詳解 (啟動 Python 運算)", type="primary"):
    with st.spinner("AI 正在分析邏輯並撰寫運算程式..."):
        try:
            client = Groq(api_key=api_key)
            base64_image = encode_image(uploaded_file)
            
            # 1. 呼叫 AI
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
                model="meta-llama/llama-4-scout-17b-16e-instruct", 
                temperature=0.0,
            )
            
            full_response = chat_completion.choices[0].message.content
            
            # 2. 顯示 AI 的文字分析
            st.markdown("### 📝 題目分析與思路")
            st.markdown(full_response)
            
            # 3. 提取並執行 Python 程式碼
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
elif uploaded_file and not api_key: st.error("請先設定 API Key")
