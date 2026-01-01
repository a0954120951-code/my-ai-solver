import streamlit as st
from groq import Groq
import base64
import os

# --- 頁面設定 ---
st.set_page_config(page_title="電工機械解題王", layout="centered")

st.title("⚡ 電工機械解題王 (V3.1 修正版)")
st.caption("AI 輔助運算，請同學務必自行驗算數據")

# --- 自動讀取鑰匙 ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.warning("⚠️ 尚未偵測到 API Key")
    st.info("請到 Streamlit 後台設定 Secrets")
    api_key = st.sidebar.text_input("或在此手動輸入 Groq API Key", type="password")

# --- 處理圖片的函數 ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- 嚴格版 AI 指令 (核心修正) ---
system_prompt = """
你是一位嚴謹的台灣高職「電工機械」教師。你的任務是精確解決學生上傳的考題。
目前你的計算準確率不足，必須嚴格遵守以下思考流程 (Chain of Thought)：

### 步驟 1：識別與提取 (OCR)
1. 仔細閱讀圖片中的所有文字，特別是數字的指數部分 (例如 10^-3 與 10^-5)。
2. **列出所有已知條件 (Given)**：
   - 看到「雙分疊繞」：記住 a = 2P。
   - 看到「雙分波繞」：記住 a = 2 × 2 = 4 (若m=2)。
   - 看到「轉速 rad/s」：必須檢查是否需要換算成 rpm (N = 60ω / 2π)。
   - 看到導磁係數：注意是相對導磁係數還是絕對導磁係數。

### 步驟 2：選擇公式與邏輯
1. 寫出將使用的標準公式 (例如 E = P Z Φ N / 60 a)。
2. 若是選擇題的觀念題（如換向、電樞反應），請先回想課本定義，對於每個選項進行「True/False」驗證，不要只憑直覺。

### 步驟 3：逐步計算 (避免跳步)
1. **不要直接給出最終答案**。
2. 請像寫算式給小學生看一樣，把數字帶入公式。
3. 遇到指數運算 (10的次方) 請特別小心，分開計算係數與指數。
4. **檢查單位**：確保所有單位統一 (例如 cm 轉 m)。

### 步驟 4：最終檢查
1. 檢查算出的數字是否符合常理 (例如發電機電壓通常是 100V~220V，算出 0.4V 肯定錯了)。
2. 回答格式：
   - **題型分析**
   - **已知條件**
   - **詳細步驟** (含 LaTeX 公式)
   - **最終答案** (清楚標示選項，如：(C))

請用繁體中文回答。數學公式用 Streamlit 支援的格式：$$ E = ... $$。
"""

# --- 主程式 ---
uploaded_file = st.file_uploader("📸 拍照或上傳題目", type=["jpg", "png", "jpeg"])

if uploaded_file and api_key:
    st.image(uploaded_file, caption="預覽題目", use_container_width=True)
    
    if st.button("🚀 開始詳解", type="primary"):
        with st.spinner("AI 老師正在讀題並驗算中..."):
            try:
                client = Groq(api_key=api_key)
                base64_image = encode_image(uploaded_file)
                
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
                    # --- 修正重點：使用您之前測試成功的 Llama 4 Scout 模型 ---
                    model="meta-llama/llama-4-scout-17b-16e-instruct", 
                    temperature=0.1, # 極低隨機性，強迫它邏輯運算
                )
                
                result = chat_completion.choices[0].message.content
                st.markdown("### 📝 解題分析")
                st.markdown(result)
                
                # 加入免責聲明
                st.warning("⚠️ AI 可能發生計算錯誤，請同學務必自行按計算機驗算一次！")
                
            except Exception as e:
                st.error(f"發生錯誤：{str(e)}")

elif uploaded_file and not api_key:
    st.error("請先設定 API Key")
