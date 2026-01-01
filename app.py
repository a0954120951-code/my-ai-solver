import streamlit as st
from groq import Groq
import base64
import os

# --- 頁面設定 ---
st.set_page_config(page_title="電工機械解題王(V4.0)", layout="centered")

st.title("⚡ 電工機械解題王 (V4.0 核彈模式)")
st.caption("啟用最高等級嚴格邏輯檢查，速度較慢但更準確。")

# --- 自動讀取鑰匙 ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.warning("⚠️ 尚未偵測到 API Key")
    api_key = st.sidebar.text_input("或在此手動輸入 Groq API Key", type="password")

# --- 處理圖片的函數 ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- V4.0 核彈級指令 (The Nuclear Prompt) ---
# 核心策略：強制結構化輸出，禁止心算，強制單位換算，變數明確化
system_prompt = """
Role: You are a pedantic, super-strict Professor of Electrical Machinery engineering. Your job is to solve exam problems with 100% mathematical precision.

**CRITICAL RULE: DO NOT DO MENTAL MATH.**
You are bad at mental math. You must write out every calculation step clearly so a human with a calculator can verify it.

**EXECUTION PROTOCOL (Follow strictly):**

**PHASE 1: IMAGE OCR & DATA EXTRACTION (The most important phase)**
1. Read the image text carefully. Pay extreme attention to scientific notation (e.g., 10^-3 vs 10^-5).
2. **Identify Key "Traps" (Keywords):**
   - "雙分疊繞" (Double Lap): Set a = 2 * P.
   - "單分疊繞" (Simplex Lap): Set a = P.
   - "波繞" (Wave): Set a = 2 (usually).
   - "轉速 N (rpm)" vs "角速度 ω (rad/s)": If given ω, N = 60*ω / (2π).
   - "直徑 D" vs "半徑 r".
   - "導磁係數 μ": Is it relative (μr) or absolute (μ)? μ = μr * μ0. (μ0 = 4π * 10^-7).

3. **List Structured Variables (SI Units Mandatory):**
   - Extract every number and convert it to standard SI base units IMMEDIATELY.
   - Example format:
     - P (極數) = 4
     - N_rpm (轉速) = 1200 rpm
     - ω (角速度) = 1200 * 2 * 3.14159 / 60 = 125.66 rad/s  <-- YOU MUST WRITE THIS OUT
     - D (直徑) = 50 cm = 0.5 m
     - I (電流) = 10 A

**PHASE 2: FORMULA SELECTION**
1. State the standard textbook formula clearly using LaTeX format ($$...$$).
2. Define what each variable in the formula represents.

**PHASE 3: THE CALCULATION (The danger zone)**
1. Plug the specific numbers into the formula. Do not simplify yet.
   $$ E = \frac{4 \times 500 \times 0.02 \times 1200}{60 \times 4} $$
2. **Simplify step-by-step.** Do not jump to the answer. Deal with exponents separately if needed.
   Step 3.1 (Numerator): 4 * 500 * 0.02 * 1200 = ...
   Step 3.2 (Denominator): 60 * 4 = ...
   Step 3.3 (Final Division): ...
3. State the final result with units.

**PHASE 4: FINAL OUTPUT FORMAT (Traditional Chinese)**
Please present the final output to the student in clear Traditional Chinese, following this structure:
### 🎯 題目分析與陷阱識別
(這裡列出你看到的關鍵字，如雙分疊繞，並說明其意義)
### 🔢 已知條件 (化為基本單位)
(列出變數清單)
### 📐 選用公式
(列出 LaTeX 公式)
### 🧮 詳細計算過程
(一步一步的算式，禁止跳步)
### ✅ 最終答案
(答案選項)

Answer in Traditional Chinese only. Use LaTeX for math.
"""

# --- 主程式 ---
uploaded_file = st.file_uploader("📸 拍照或上傳題目", type=["jpg", "png", "jpeg"])

if uploaded_file and api_key:
    # 為了讓 AI 看得更清楚，這裡不縮圖，直接用原圖寬度傳送 (雖然介面會變醜一點)
    # st.image(uploaded_file, caption="預覽題目", use_container_width=True) 
    st.write("圖片已接收，準備進行精密分析...")
    
    if st.button("🚀 啟動核彈級詳解", type="primary"):
        with st.spinner("⚠️ 正在進行精密運算，請耐心等候 (約需 15-30 秒)..."):
            try:
                client = Groq(api_key=api_key)
                base64_image = encode_image(uploaded_file)
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", # 這裡改用 system role，權重更高
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "請依照上面的嚴格協議分析這張圖片的題目。"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        # 試圖傳送更高解析度 (如果 API 支援)
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                        "detail": "high" 
                                    },
                                },
                            ],
                        }
                    ],
                    # 使用目前 Groq 上最強的推理+視覺模型
                    model="llama-3.2-90b-vision-preview", 
                    # 關鍵：Temperature 設為 0，強制 AI 不要有任何創造力，只能死板邏輯推理
                    temperature=0.0, 
                    # 限制最大輸出 token，防止它無限迴圈，但給夠用
                    max_tokens=2048,
                    # 核取樣設定，進一步限制隨機性
                    top_p=0.1,
                )
                
                result = chat_completion.choices[0].message.content
                st.markdown("---")
                st.markdown(result)
                st.success("精密分析完成！")
                st.error("⚠️ 重要提醒：即使是核彈模式，仍建議同學按計算機驗算關鍵步驟的數字！")
                
            except Exception as e:
                st.error(f"發生錯誤，可能是題目太模糊或運算超時：{str(e)}")

elif uploaded_file and not api_key:
    st.error("請先設定 API Key")
