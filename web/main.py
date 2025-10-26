import os, json, io
import streamlit as st
from typing import List
from utils_ui import api_health, api_ask, api_upload_file, llm_synthesize_from_questions

# ====== Tải cấu hình ======
CFG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
try:
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        CFG = json.load(f)
except Exception:
    CFG = {
        "site_title": "ViCulture-AI — Dân tộc học",
        "admin_password": "admin@123",
        "welcome_text": "Chào mừng đến với ViCulture-AI. Hỏi đáp tiếng Việt dựa trên tài liệu do tác giả upload.",
        "default_top_k": 3
    }

st.set_page_config(page_title=CFG.get("site_title", "ViCulture-AI"), page_icon="📘", layout="wide")

# ====== CSS gọn nhẹ ======
st.markdown("""
<style>
    .small { font-size: 0.9rem; color: #666; }
    .cite { color:#0d47a1; margin:0.25rem 0; }
    .role-badge { background:#0d47a1; color:#fff; padding:2px 8px; border-radius:999px; font-size:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ====== Header ======
col1, col2 = st.columns([1,8])
with col1:
    st.write("📘")
with col2:
    st.markdown(f"### {CFG.get('site_title', 'ViCulture-AI')}")
    st.caption(CFG.get("welcome_text", ""))

# ====== Session init ======
if "role" not in st.session_state:
    st.session_state["role"] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "q_history" not in st.session_state:
    st.session_state["q_history"] = []  # lưu 10 câu hỏi nhỏ
if "discussion_q" not in st.session_state:
    st.session_state["discussion_q"] = ""

# ====== Sidebar – Đăng nhập vai trò ======
st.sidebar.title("🔑 Đăng nhập")
role = st.sidebar.radio("Chọn vai trò:", ["Student", "Admin"], index=0)
if role == "Admin":
    pw = st.sidebar.text_input("Mật khẩu Admin", type="password")
    if st.sidebar.button("Đăng nhập Admin", use_container_width=True):
        if pw == CFG.get("admin_password", ""):
            st.session_state["role"] = "Admin"
            st.session_state["logged_in"] = True
            st.sidebar.success("Đăng nhập Admin thành công.")
        else:
            st.sidebar.error("Sai mật khẩu.")
else:
    if st.sidebar.button("Vào với vai trò Student", use_container_width=True):
        st.session_state["role"] = "Student"
        st.session_state["logged_in"] = True
        st.sidebar.success("Đăng nhập Student.")

if st.session_state["logged_in"]:
    st.sidebar.markdown(f'<span class="role-badge">{st.session_state["role"]}</span>', unsafe_allow_html=True)
    if st.sidebar.button("🚪 Đăng xuất", use_container_width=True):
        for k in ["role", "logged_in", "q_history", "discussion_q"]:
            st.session_state.pop(k, None)
        st.rerun()

# ====== Kiểm tra API backend ======
api_ok = api_health()
st.sidebar.markdown("### Trạng thái API")
st.sidebar.write("🟢 Sẵn sàng" if api_ok else "🔴 Không kết nối được")
st.sidebar.caption(f"API_BASE_URL = {os.getenv('API_BASE_URL', '') or '(chưa đặt)'}")

if not st.session_state.get("logged_in"):
    st.info("Vui lòng đăng nhập để sử dụng ứng dụng.")
    st.stop()

# ====== Tabs chính ======
tabs = st.tabs(["💬 Hỏi KB", "🧪 10 câu hỏi nhỏ", "🧩 Câu hỏi thảo luận", "⚙️ Admin"])
top_k_default = int(CFG.get("default_top_k", 3))

# ------------------ TAB 1: HỎI KB ------------------
with tabs[0]:
    st.subheader("💬 Hỏi Kho Tri Thức (tiếng Việt)")
    question = st.text_input("Nhập câu hỏi:", placeholder="Ví dụ: Thế nào là 'văn hoá tộc người' trong dân tộc học Việt Nam?")
    c1, c2 = st.columns([1,1])
    with c1:
        top_k = st.number_input("Số trích đoạn (top_k)", min_value=1, max_value=5, value=top_k_default, step=1)
    with c2:
        st.write("")
    if st.button("Hỏi KB", type="primary"):
        if not api_ok:
            st.error("API chưa sẵn sàng. Kiểm tra lại dịch vụ FastAPI.")
        elif not question.strip():
            st.warning("Bạn chưa nhập câu hỏi.")
        else:
            try:
                res = api_ask(question.strip(), top_k=top_k)
                st.markdown("#### 📖 Trả lời")
                st.write(res.get("answer", ""))
                cites = res.get("citations", [])
                if cites:
                    st.markdown("#### 📚 Trích dẫn")
                    for c in cites:
                        st.markdown(f"- <span class='cite'>• {c}</span>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Lỗi gọi API /ask: {e}")

# ------------------ TAB 2: 10 CÂU HỎI NHỎ ------------------
with tabs[1]:
    st.subheader("🧪 Ghi nhận 10 câu hỏi nhỏ")
    st.caption("Sau khi đủ 10 câu, chuyển sang tab **'🧩 Câu hỏi thảo luận'** để sinh câu hỏi tổng hợp.")
    small_q = st.text_input("Nhập câu hỏi nhỏ (tiếng Việt):", placeholder="Ví dụ: Trình bày sự khác nhau giữa ...")
    colA, colB = st.columns([1,1])
    with colA:
        if st.button("Thêm vào danh sách"):
            q = small_q.strip()
            if not q:
                st.warning("Chưa nhập câu hỏi.")
            else:
                st.session_state["q_history"].append(q)
                st.success("Đã thêm câu hỏi nhỏ.")
    with colB:
        if st.button("Xoá danh sách"):
            st.session_state["q_history"].clear()
            st.session_state["discussion_q"] = ""
            st.info("Đã xoá danh sách câu hỏi nhỏ.")

    if st.session_state["q_history"]:
        st.markdown("#### Danh sách hiện có")
        for i, q in enumerate(st.session_state["q_history"], 1):
            st.write(f"{i}. {q}")
        st.caption(f"Hiện có: **{len(st.session_state['q_history'])}/10**")
    else:
        st.info("Chưa có câu hỏi nhỏ nào.")

# ------------------ TAB 3: CÂU HỎI THẢO LUẬN ------------------
with tabs[2]:
    st.subheader("🧩 Sinh 'Câu hỏi thảo luận' sau 10 câu hỏi nhỏ")
    q_list: List[str] = st.session_state.get("q_history", [])
    if len(q_list) < 10:
        st.warning("Cần ít nhất **10 câu hỏi nhỏ**. Vui lòng thêm tại tab '🧪 10 câu hỏi nhỏ'.")
    else:
        if st.button("✨ Tạo câu hỏi thảo luận (từ 10 câu trên)", type="primary"):
            result = llm_synthesize_from_questions(q_list[:10])
            st.session_state["discussion_q"] = result or "(Không tạo được câu hỏi thảo luận.)"

        if st.session_state.get("discussion_q"):
            st.markdown("#### ✅ Câu hỏi thảo luận được tạo")
            st.write(st.session_state["discussion_q"])

# ------------------ TAB 4: ADMIN ------------------
with tabs[3]:
    if st.session_state["role"] != "Admin":
        st.error("Khu vực dành cho Admin.")
    else:
        st.subheader("⚙️ Quản trị")
        st.markdown("**📤 Upload tài liệu vào Kho Tri Thức** (PDF / DOCX / TXT)")
        up = st.file_uploader("Chọn file", type=["pdf", "docx", "txt"])
        if up and st.button("Tải lên KB"):
            if not api_ok:
                st.error("API chưa sẵn sàng.")
            else:
                try:
                    info = api_upload_file((up.name, up.getvalue(), up.type or "application/octet-stream"))
                    st.success(f"✅ Đã upload: doc_id={info.get('doc_id')} | chunks={info.get('chunks')}")
                except Exception as e:
                    st.error(f"Lỗi upload: {e}")

        st.markdown("---")
        st.markdown("**🔐 Đổi mật khẩu Admin (cập nhật file `web/config.json`)**")
        st.caption("Để bảo mật, hãy commit & deploy lại sau khi đổi.")
