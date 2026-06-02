import streamlit as st
from pathlib import Path

# --- CÁC IMPORTS TỪ BACKEND CỦA BÀI LAB ---
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop, trim_history

# --- KHỞI TẠO MÔI TRƯỜNG & ĐƯỜNG DẪN ---
ROOT = Path(__file__).parent
load_lab_env(ROOT)
ARTIFACTS_DIR = ROOT / "artifacts"

# Cấu hình UI
st.set_page_config(page_title="Research AI Agent", page_icon="🤖", layout="wide")

# --- SIDEBAR: Giao diện và Cấu hình ---
with st.sidebar:
    st.title("🤖 Trợ lý thông minh")
    st.markdown("---")
    
    st.subheader("✨ Tính năng (Tools) hiện có")
    st.markdown("""
    * ❓ **clarify**: Hỏi lại khi thiếu thông tin
    * 📄 **fetch**: Đọc nội dung website
    * 📝 **format**: Định dạng báo cáo
    * 🔍 **lookup**: Tra cứu Internet
    * 📚 **papers**: Tìm bài báo arXiv
    * 📖 **paper_text**: Đọc bài báo arXiv
    * 🏢 **policy**: Tra cứu quy định
    * ✈️ **send**: Gửi nội dung
    * 🐦 **social_search**: Tìm MXH theo từ khóa
    * 👤 **timeline**: Lấy bài đăng cá nhân
    """)
    st.markdown("---")
    
    st.subheader("⚙️ Cấu hình Hệ thống")
    # 1. Đã bỏ 'openai' khỏi danh sách
    selected_provider = st.selectbox("Provider:", ["openrouter", "gemini"], index=0)
    selected_version = st.selectbox("Version:", ["v0", "v1", "v2", "v3"], index=0)
    
    # 2. Thêm thanh kéo Temperature
    selected_temperature = st.slider(
        "Temperature:", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.6, 
        step=0.01,       # Làm tròn bước nhảy tới hàng phần trăm
        format="%g",     # %g tự động lược bỏ số 0 thừa ở 2 đầu
        help="0: Trả lời chính xác, logic.\n1: Trả lời sáng tạo, bay bổng."
    )
    
    # st.caption("Lưu ý: Agent sẽ luôn chạy dựa trên nội dung cấu hình hiện hành trong artifacts/.")

# --- MAIN GIAO DIỆN CHAT ---
st.title("Trợ lý nghiên cứu, tra cứu & tổng hợp thông tin (Nhóm 4 - Zone 3)")
st.caption("Hãy nhập yêu cầu của bạn (Ví dụ: Tra cứu thông tin xăng dầu hôm nay, tìm bài đăng mới nhất...)")

# Khởi tạo bộ nhớ hội thoại
if "messages" not in st.session_state:
    st.session_state.messages = [] 
if "history" not in st.session_state:
    st.session_state.history = []  

# Hiển thị lịch sử tin nhắn
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- XỬ LÝ LÔ-GIC KHI CHAT ---
if prompt := st.chat_input("Nhập yêu cầu của bạn vào đây..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Chuẩn bị Backend
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(selected_provider)
    
    llm_messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, 5),
        {"role": "user", "content": prompt}
    ]
    
    # Chạy Agent thật
    with st.chat_message("assistant"):
        with st.spinner(f"Đang tìm kiếm và xử lý thông tin..."):
            try:
                # GỌI BACKEND
                result = run_model_tool_loop(
                    provider=provider,
                    messages=llm_messages,
                    tools=openai_tools,
                    model=None,
                    max_tool_rounds=4
                )
                
                final_answer = result.get("assistant_text") or "*(Không có phản hồi dạng văn bản.)*"
                st.markdown(final_answer)
                
                st.session_state.history.append({"role": "user", "content": prompt})
                st.session_state.history.append({"role": "assistant", "content": final_answer})
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
                
            except Exception as e:
                error_msg = f"Đã xảy ra lỗi kết nối: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})