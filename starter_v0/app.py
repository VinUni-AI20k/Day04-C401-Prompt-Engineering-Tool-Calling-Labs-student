import streamlit as st
import json
from pathlib import Path

# Import các hàm từ bài lab có sẵn
from chat import run_model_tool_loop, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Research Agent", page_icon="✨", layout="centered")

# Inject Custom CSS để có giao diện giống ChatGPT / DeepSeek
st.markdown("""
<style>
    /* Ẩn các thành phần mặc định của Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Đổi font chữ sang dạng Inter hoặc hệ thống */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Căn giữa tiêu đề và tạo điểm nhấn */
    .title-container {
        text-align: center;
        padding-bottom: 2rem;
        margin-top: -3rem;
    }
    .title-container h1 {
        font-weight: 600;
        font-size: 2.5rem;
        color: #1E1E1E;
    }
    .title-container p {
        color: #666;
        font-size: 1.1rem;
    }
    
    /* Chỉnh sửa ô nhập chat cho bo góc giống DeepSeek/ChatGPT */
    .stChatInputContainer textarea {
        border-radius: 20px !important;
        border: 1px solid #E5E5E5 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        padding: 14px 20px !important;
    }
    
    /* Tinh chỉnh hộp tin nhắn (Expander) của tools */
    [data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        background-color: #f8fafc;
        box-shadow: none;
    }
    [data-testid="stExpander"] summary {
        font-size: 0.9rem;
        color: #475569;
        font-weight: 500;
    }
    
    /* Styling cho các nút gợi ý */
    [data-testid="stButton"] button {
        background-color: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 12px;
        color: #333;
        padding: 10px 15px;
        text-align: left;
        font-weight: 500;
        transition: all 0.2s ease;
        justify-content: flex-start;
    }
    [data-testid="stButton"] button:hover {
        border-color: #999;
        background-color: #f9f9f9;
        color: #000;
    }
    [data-testid="stButton"] button p {
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('''
<div class="title-container">
    <h1>✨ Research Agent</h1>
    <p>AI Assistant tích hợp công cụ (Tool-calling) siêu mạnh mẽ</p>
</div>
''', unsafe_allow_html=True)

# Load môi trường và provider (chỉ load 1 lần nhờ st.cache_resource)
@st.cache_resource
def setup_environment():
    load_lab_env(ROOT)
    provider = make_provider("openrouter")
    return provider

# Cố gắng khởi tạo môi trường, bắt lỗi nếu chưa có API Key
try:
    provider = setup_environment()
except Exception as e:
    st.error(f"Lỗi khởi tạo Provider: {e}. Vui lòng kiểm tra file .env của bạn.")
    st.stop()

# Đọc cấu hình prompt và tools (chỉ đọc 1 lần nhờ st.cache_data)
@st.cache_data
def load_agent_config():
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    openai_tools = to_openai_tools(tool_declarations)
    return system_prompt, openai_tools

try:
    system_prompt, openai_tools = load_agent_config()
except Exception as e:
    st.error(f"Lỗi đọc cấu hình: {e}")
    st.stop()

# Khởi tạo state để lưu lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = [] # Dùng để hiển thị lên UI
if "history" not in st.session_state:
    st.session_state.history = []  # Dùng để làm ngữ cảnh (context) cho AI

# Hàm hiển thị các tin nhắn cũ mỗi khi Streamlit render lại
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tool_events" in msg and msg["tool_events"]:
            for event in msg["tool_events"]:
                with st.expander(f"🛠️ Đã dùng tool: `{event.get('tool')}`"):
                    st.json(event)

# Lấy input từ thanh chat
prompt = st.chat_input("Hỏi tôi bất cứ điều gì (ví dụ: Tóm tắt tin AI hôm nay)...")

# Biến lưu trữ input cuối cùng (từ chat hoặc từ nút gợi ý)
final_input = prompt

# Gợi ý ban đầu (chỉ hiển thị khi chưa có tin nhắn nào)
if not st.session_state.messages:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📰 Tin tức AI hôm nay có gì nổi bật?", use_container_width=True):
            final_input = "Tin tức AI hôm nay có gì nổi bật?"
        if st.button("🐦 Mọi người đang bàn gì về GPT-5 trên Twitter?", use_container_width=True):
            final_input = "Mọi người đang bàn gì về GPT-5 trên Twitter?"
    with col2:
        if st.button("💰 Giá Bitcoin hiện tại là bao nhiêu?", use_container_width=True):
            final_input = "Giá Bitcoin hiện tại là bao nhiêu?"
        if st.button("📝 Tóm tắt bài này: https://openai.com/blog", use_container_width=True):
            final_input = "Tóm tắt bài này: https://openai.com/blog"

if final_input:
    # 1. Hiển thị tin nhắn người dùng ngay lập tức
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    # 2. Xây dựng danh sách tin nhắn gửi cho AI (kèm system prompt và lịch sử cũ)
    context_messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, window=5),
        {"role": "user", "content": final_input},
    ]

    # 3. Chạy vòng lặp tool calling
    with st.chat_message("assistant"):
        with st.spinner("Agent đang suy nghĩ và dùng tools..."):
            try:
                # Gọi hàm run_model_tool_loop y hệt như chat.py
                result = run_model_tool_loop(
                    provider=provider,
                    messages=context_messages,
                    tools=openai_tools,
                    model=None,
                    max_tool_rounds=4,
                )
                
                assistant_text = result.get("assistant_text", "")
                tool_events = result.get("tool_events", [])
                
                # Hiển thị câu trả lời
                st.markdown(assistant_text)
                
                # Hiển thị log của tools đã dùng trong lượt này
                if tool_events:
                    for event in tool_events:
                        with st.expander(f"🛠️ Đã dùng tool: `{event.get('tool')}`"):
                            st.json(event)
                            
                # 4. Lưu vào session state
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": assistant_text,
                    "tool_events": tool_events
                })
                
                # Cập nhật lịch sử ngắn (history window) cho lượt chat tiếp theo
                st.session_state.history.append({"role": "user", "content": final_input})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
                
                # Rerun để ẩn các nút gợi ý và cập nhật UI mượt mà
                st.rerun()
                
            except Exception as e:
                st.error(f"Đã có lỗi xảy ra trong quá trình chạy Agent: {str(e)}")
