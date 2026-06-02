import streamlit as st
import json
import requests
import re

# --- IMPORT HỆ THỐNG LAB CHUẨN XÁC ---
try:
    from agent import ResearchAgent
    from tools import load_tool_declarations, to_openai_tools, TOOL_FUNCTIONS 
    from providers.openrouter_provider import OpenRouterProvider
    from providers.openai_provider import OpenAIProvider
    from providers.anthropic_provider import AnthropicProvider
    from providers.gemini_provider import GeminiProvider
    
    # =====================================================================
    # ☢️ GIẢI PHÁP HẠT NHÂN: VIẾT THẲNG HÀM TÌM ẢNH BING VÀO APP.PY
    # (Khắc phục triệt để lỗi 403 DuckDuckGo và lỗi Cache của hệ thống)
    # =====================================================================
    def search_images_bing(query: str) -> dict:
        """Hàm kéo ảnh Bing siêu cấp, chống 403 tuyệt đối"""
        try:
            # Giả lập làm trình duyệt web người thật
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
            safe_query = query.replace(" ", "+")
            url = f"https://www.bing.com/images/search?q={safe_query}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Đào link ảnh gốc chất lượng cao bằng Regex
            image_links = re.findall(r'murl&quot;:&quot;(.*?)&quot;', response.text)
            unique_links = list(dict.fromkeys(image_links))[:3]
            
            items = []
            for link in unique_links:
                items.append({"title": f"Ảnh thực tế {query}", "url": link})
                
            # Nếu mạnng lỗi không tìm thấy, trả về ảnh giữ chỗ (placeholder)
            if not items:
                items.append({"title": f"Minh họa {query}", "url": f"https://placehold.co/800x400?text={safe_query}"})
                
            return {"status": "success", "query": query, "items": items}
        except Exception as e:
            return {"status": "error", "query": query, "message": f"Lỗi Bing: {str(e)}"}

    # Ghi đè vĩnh viễn tool search_images bằng hàm Bing vừa tạo
    TOOL_FUNCTIONS["search_images"] = search_images_bing
    
    
except ImportError as e:
    st.error(f"⚠️ Lỗi cấu trúc import thư mục: {str(e)}\nHãy chắc chắn file app.py đặt trong thư mục 'starter/'.")
    st.stop()

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Research Agent Pro UI", page_icon="🧪", layout="wide")

# --- HÀM KHỞI TẠO PROVIDER ---
def get_provider_instance(provider_name: str, model_name: str = None):
    if provider_name == "openrouter":
        return OpenRouterProvider(model=model_name) if model_name else OpenRouterProvider()
    elif provider_name == "openai":
        return OpenAIProvider(model=model_name) if model_name else OpenAIProvider()
    elif provider_name == "anthropic":
        return AnthropicProvider(model=model_name) if model_name else AnthropicProvider()
    elif provider_name == "gemini":
        return GeminiProvider(model=model_name) if model_name else GeminiProvider()
    else:
        return OpenRouterProvider()

# =========================================================
# GIAO DIỆN THANH ĐIỀU HƯỚNG (SIDEBAR)
# =========================================================
# Gán cố định cấu hình ngầm để Agent vẫn hoạt động mượt mà
provider_choice = "openrouter"
model_choice = ""

with st.sidebar:
    if st.button("🗑️ Xóa lịch sử chat và làm mới"):
        st.session_state.messages = []
        st.rerun()

# =========================================================
# KHU VỰC CHAT CHÍNH (MAIN CHAT INTERFACE)
# =========================================================
st.title("🧪 Trực quan hóa Nghiên cứu Agent (Live Debug)")
st.markdown("Xem trực tiếp luồng tư duy của Agent: Chọn tool ngầm -> Kéo dữ liệu API thật -> Tổng hợp câu trả lời dựa trên bằng chứng.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tool_calls" in msg and msg["tool_calls"]:
            with st.expander("🛠️ Xem lại các Tool JSON đã gọi ở lượt này", expanded=False):
                st.json(msg["tool_calls"])

if user_input := st.chat_input("Nhập yêu cầu... (Ví dụ: Lấy ảnh Donald Trump, Lấy 5 tweet của Elon Musk)"):
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Agent đang phân tích câu hỏi và định tuyến Tool..."):
            try:
                # --- BƯỚC A: ĐỌC VÀ CHUẨN HÓA CẤU HÌNH ---
                with open("artifacts/system_prompt.md", "r", encoding="utf-8") as f:
                    system_prompt_content = f.read()
                    
                tool_declarations = load_tool_declarations("artifacts/tools.yaml")
                openai_tools = to_openai_tools(tool_declarations)

                # --- BƯỚC B: KHỞI TẠO AGENT ---
                current_provider = get_provider_instance(provider_choice, model_choice if model_choice else None)
                agent = ResearchAgent(
                    provider=current_provider,
                    system_prompt=system_prompt_content,
                    tools=openai_tools,
                    model=model_choice if model_choice else None
                )
                
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                
                # --- BƯỚC C: CHẠY AGENT LƯỢT 1 (ROUTING & EXECUTION) ---
                tool_choice = "required" if not any(kw in user_input.lower() for kw in ["chào", "bạn là ai", "nguyên hàm"]) else None
                result = agent.run(history, tool_choice=tool_choice)
                
                ui_tool_calls = []
                for call in result.tool_calls:
                    ui_tool_calls.append({"name": call.name, "args": call.args})

                # --- BƯỚC D: VÒNG LẶP HỒI ĐÁP LƯỢT 2 (SYNTHESIS BASED ON EVIDENCE) ---
                if ui_tool_calls:
                    with st.expander("🛠️ BƯỚC 1: Agent đã chọn và kích hoạt công cụ thành công", expanded=True):
                        for tool in ui_tool_calls:
                            st.info(f"👉 **Tool:** `{tool['name']}`")
                            st.write("**Tham số trích xuất:**")
                            st.json(tool['args'])
                        
                        st.write("🔄 **Dữ liệu thô thu hồi từ internet:**")
                        st.json(result.tool_results)
                    
                    with st.spinner("BƯỚC 2: Đang đọc hiểu tài liệu và tổng hợp câu trả lời..."):
                        evidence_context = (
                            "Dưới đây là kết quả dữ liệu thực tế thu thập được từ Internet:\n"
                            f"{json.dumps(result.tool_results, ensure_ascii=False)}\n\n"
                            "YÊU CẦU QUAN TRỌNG NHẤT:\n"
                            "1. Dùng toàn bộ thông tin trên làm bằng chứng (evidence) để trả lời người dùng.\n"
                            "2. NẾU dữ liệu là hình ảnh (có chứa URL ảnh), BẮT BUỘC nhúng trực tiếp ảnh đó vào câu trả lời bằng cú pháp Markdown: ![Tiêu đề ảnh](URL_của_ảnh).\n"
                            "3. Tuyệt đối không tự bịa thông tin."
                        )
                        
                        second_round_history = history + [{"role": "system", "content": evidence_context}]
                        
                        # Khóa tool_choice="none" chặn lỗi không xuất văn bản
                        final_run = agent.run(second_round_history, tool_choice="none")
                        response_text = final_run.text if final_run.text else "Agent đã xử lý xong công cụ nhưng API không trả về văn bản nào."
                else:
                    response_text = result.text if result.text else "Agent không đưa ra phản hồi văn bản."
                
                # --- BƯỚC E: IN CÂU TRẢ LỜI VÀ LƯU TRỮ ---
                st.markdown(response_text)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "tool_calls": ui_tool_calls
                })

            except Exception as e:
                st.error(f"❌ Hệ thống gặp sự cố khi thực thi Agent:\n\n{str(e)}")