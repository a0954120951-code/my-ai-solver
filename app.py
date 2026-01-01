import streamlit as st
from groq import Groq
import base64
import os
import re
import sys
from io import StringIO
import contextlib

# --- 1. 頁面設定 ---
st.set_page_config(page_title="電工機械解題王 (V6.0)", layout="centered")

st.title("⚡ 電工機械解題王")
st.caption("🤖 AI 助教輔助解題 (V6.0 學生友善版)")

# --- 2. 自動讀取 API Key ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.warning("⚠️ 尚未偵測到 API Key")
    api_key = st.sidebar.text_input("請輸入 Groq API Key", type="password")

# --- 3. 核心函數 ---
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
# 修改重點：要求 AI 用「教學口吻」解釋，並將程式碼藏在最後
system_prompt = """
你是一位親切、擅長教學的台灣高職「電工機械」老師。
你的任務是幫助學生理解題目，並算出正確答案。

**解題流程 (請嚴格遵守)**：

**第一部分：教學講解 (給學生看)**
1. **題目分析**：用簡單白話文列出已知條件 (Given)，例如：「這題告訴我們極數 P=4...」。
2. **公式選用**：列出要用的公式，並解釋為什麼用這個公式。
3. **計算步驟**：用數學式子 (LaTeX) 展示代入數字的過程，不要寫程式碼，要寫數學算式。
   - 例如：$$ E = \\frac{P Z \\phi N}{60 a} $$
4. **觀念提醒**：如果有陷阱 (如雙分疊繞、超前/滯後)，請用文字特別提醒學生注意。

**第二部分：精確運算 (給電腦執行)**
為了確保答案數字絕對正確，請在講解完畢後，撰寫一段 Python 程式碼來驗算。
- 程式碼必須包含在 markdown 代碼區塊中 (```python ... ```)。
- **最後一步務必使用 `print()` 印出最終答案與單位**。

**陷阱提示**：
- 雙分疊繞 a=2P；單分疊繞 a=P；波繞 a=2m。
- 電壓調整率：超前用減(-)，滯後用加(+)。

**輸出格式要求**：
請先用繁體中文和 LaTeX 數學式做完整的教學講解，最後才附上 Python 程式碼區塊。
"""

# --- 5. 主程式邏輯 ---
uploaded_file = st.file_uploader("📸 拍照或上傳題目", type=["jpg", "png", "jpeg"])

if uploaded_file and api_key:
    st.image(uploaded_file, caption="預覽題目", use_container_width=True)
    
    if st.button("🚀 開始解題", type="primary"):
        with st.spinner("AI 助教正在分析題目並計算中..."):
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
                
                # --- 介面優化重點 ---
                
                # 1. 提取 Python 程式碼 (但不直接顯示)
                code_match = re.search(r'```python(.*?)```', full_response, re.DOTALL)
                
                # 2. 移除回應中的程式碼部分，只留下教學文字，讓畫面乾淨
                # 這樣學生就只會看到中文講解和數學公式
                display_text = re.sub(r'```python.*?```', '', full_response, flags=re.DOTALL)
                
                # 3. 顯示親切的教學文字
                st.markdown("### 📝 助教講解")
                st.markdown(display_text)
                
                if code_match:
                    code_to_run = code_match.group(1).strip()
                    
                    # 4. 執行運算並顯示最終精確答案 (醒目顯示)
                    calculated_result = execute_ai_code(code_to_run)
                    
                    if "運算錯誤" not in calculated_result:
                        st.success(f"✅ 電腦驗算最終答案：\n\n**{calculated_result}**")
                    else:
                        st.error(f"驗算失敗：{calculated_result}")
                        
                    # 5. 將程式碼藏在摺疊選單中 (給老師檢查用)
                    with st.expander("🛠️ 查看運算細節 (老師專用)"):
                        st.info("這是 AI 在後台執行的驗算程式碼：")
                        st.code(code_to_run, language='python')
                        
                else:
                    st.warning("⚠️ AI 未生成驗算程式碼，請依上方解題思路為主。")
                
            except Exception as e:
                st.error(f"發生系統錯誤：{str(e)}")

elif uploaded_file and not api_key:
    st.error("請先設定 API Key")
