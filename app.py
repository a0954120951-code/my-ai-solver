import streamlit as st
import os
from groq import Groq
import base64

# --- 頁面設定 ---
st.set_page_config(page_title="電工機械解題王", layout="mobile")

st.title("⚡ 電工機械解題王")
st.write("上傳電路圖或題目，AI 幫你分析！")

# --- 自動讀取鑰匙 ---
# 這裡會去抓取您在 Streamlit 後台設定的密碼
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    # 如果沒設定，給個友善提示
    st.warning("⚠️ 尚未偵測到 API Key")
    st.info("請到 Streamlit 後台設定 Secrets，或是先用左側邊欄手動輸入測試。")
    # 備用：允許手動輸入 (以免您卡在 Secrets 設定)
    api_key = st.sidebar.text_input("或在此手動輸入 Groq API Key", type="password")

# --- 處理圖片的函數 ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- 主程式 ---
uploaded_file = st.file_uploader("📸 拍照或上傳題目", type=["jpg", "png", "jpeg"])

if uploaded_file and api_key:
    # 顯示縮圖
    st.image(uploaded_file, caption="預覽題目", use_container_width=True)
    
    if st.button("🚀 開始解題", type="primary"):
        with st.spinner("AI 老師正在思考中..."):
            try:
                client = Groq(api_key=api_key)
                base64_image = encode_image(uploaded_file)
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "你是一位台灣高職電工機械老師。請分析這張圖片中的題目。1. 識別題型與已知條件。 2. 列出詳細解題步驟與公式 (用 LaTeX)。 3. 如果是電路圖，請指導如何分析。請用繁體中文回答。"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                    model="llama-3.2-11b-vision-preview",
                )
                
                result = chat_completion.choices[0].message.content
                st.markdown("### 📝 解題分析")
                st.markdown(result)
                st.success("分析完成！")
                
            except Exception as e:
                st.error(f"發生錯誤：{str(e)}")

elif uploaded_file and not api_key:
    st.error("請先設定 API Key 才能開始解題喔！")
