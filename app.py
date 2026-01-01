import streamlit as st
from groq import Groq
import base64
import os

# --- 頁面設定 ---
st.set_page_config(page_title="電工機械解題王", layout="centered")

st.title("⚡ 電工機械解題王")
st.write("上傳電路圖或題目，AI 幫你分析！")

# --- 自動讀取鑰匙 ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.warning("⚠️ 尚未偵測到 API Key")
    st.info("請到 Streamlit 後台設定 Secrets，或是先用左側邊欄手動輸入測試。")
    api_key = st.sidebar.text_input("或在此手動輸入 Groq API Key", type="password")

# --- 處理圖片的函數 ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- 設定 AI 專屬的「電工機械老師」指令 (System Prompt) ---
# 這裡我們加入了非常詳細的解題規則，防止 AI 犯低級錯誤
system_prompt = """
你是一位台灣頂尖的高職「電工機械」教師。請精確分析圖片中的題目。

重要解題規則（必須嚴格遵守）：
1. **電壓調整率 (VR%)**：
   - 看到「**滯後** (Lagging)」或電感性負載：公式中間使用 **「加號 (+)」**。
   - 看到「**超前** (Leading)」或電容性負載：公式中間必須使用 **「減號 (-)」**。
   - 若計算結果為 0 或負值，請直接寫出，不要懷疑。

2. **數學格式**：
   - 所有數學公式請務必使用 Streamlit 支援的 LaTeX 格式。
   - 獨立公式用 $$ 包裹 (例如 $$VR \% = \frac{I(R\cos\theta \pm X\sin\theta)}{V} \times 100\%$$)。
   - 行內變數用 $ 包裹 (例如 $I_2$, $V_t$)。

3. **解題邏輯**：
   - 先列出題目給定條件 (Given)。
   - 判斷題型 (變壓器、感應機、直流機等)。
   - 列出使用的公式。
   - 代入數字前，先檢查單位是否統一。
   - **一步一步計算 (Step-by-step)**，避免跳躍導致算術錯誤。

請用繁體中文回答，語氣專業且詳細。
"""

# --- 主程式 ---
uploaded_file = st.file_uploader("📸 拍照或上傳題目", type=["jpg", "png", "jpeg"])

if uploaded_file and api_key:
    st.image(uploaded_file, caption="預覽題目", use_container_width=True)
    
    if st.button("🚀 開始解題", type="primary"):
        with st.spinner("AI 老師正在思考中... (正在檢查超前/滯後條件)"):
            try:
                client = Groq(api_key=api_key)
                base64_image = encode_image(uploaded_file)
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": system_prompt}, # 這裡讀取上面設定好的加強版指令
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
                    temperature=0.1, # 降低隨機性，讓計算更精確
                )
                
                result = chat_completion.choices[0].message.content
                st.markdown("### 📝 解題分析")
                st.markdown(result)
                st.success("分析完成！")
                
            except Exception as e:
                st.error(f"發生錯誤：{str(e)}")

elif uploaded_file and not api_key:
    st.error("請先設定 API Key 才能開始解題喔！")
