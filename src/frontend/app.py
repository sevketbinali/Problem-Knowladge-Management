import os
import streamlit as st
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="PKM | Problem Knowledge Management",
    page_icon="🧠",
    layout="wide"
)

# --- Session State ---
if "token" not in st.session_state:
    st.session_state.token = None
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "similar_problems" not in st.session_state:
    st.session_state.similar_problems = []

def login(email, password):
    resp = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    if resp.status_code == 200:
        data = resp.json()["data"]
        st.session_state.token = data["access_token"]
        st.success("Giriş başarılı!")
        st.rerun()
    else:
        st.error("Giriş başarısız. Lütfen bilgilerinizi kontrol edin.")

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# --- UI Components ---
if not st.session_state.token:
    st.title("🔐 PKM Sistemine Giriş")
    with st.form("login_form"):
        email = st.text_input("Email", "admin@pkm.local")
        password = st.text_input("Şifre", "Admin123!", type="password")
        submit = st.form_submit_button("Giriş Yap")
        if submit:
            login(email, password)
else:
    # Sidebar
    with st.sidebar:
        st.header("🧠 PKM Menü")
        st.write("Hoş Geldiniz!")
        if st.button("Çıkış Yap"):
            st.session_state.token = None
            st.session_state.current_session_id = None
            st.session_state.chat_history = []
            st.rerun()
            
        st.divider()
        st.subheader("Oturum Kontrolü")
        
        if "finalized_report" not in st.session_state:
            st.session_state.finalized_report = None
            
        if st.session_state.current_session_id:
            st.success(f"Aktif Oturum: {st.session_state.current_session_id[:8]}...")
            if st.button("Oturumu Finalize Et"):
                with st.spinner("Lessons Learned üretiliyor... (Bu işlem AI modeline göre biraz sürebilir)"):
                    resp = requests.post(
                        f"{API_URL}/sessions/{st.session_state.current_session_id}/finalize",
                        headers=get_headers()
                    )
                    if resp.status_code == 200:
                        data = resp.json()["data"]
                        st.session_state.current_session_id = None
                        st.session_state.chat_history = []
                        st.session_state.finalized_report = data
                        st.success("Oturum başarıyla tamamlandı ve veritabanına kaydedildi!")
                        st.rerun()
                    else:
                        st.error(f"Hata: {resp.json().get('error', 'Bilinmeyen hata')}")
        else:
            if not st.session_state.get("finalized_report"):
                st.info("Yeni bir problem oturumu başlatabilirsiniz.")
            else:
                if st.button("Yeni Oturum Başlat"):
                    st.session_state.finalized_report = None
                    st.rerun()

    # Main Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.session_state.get("finalized_report"):
            st.title("📄 Çözüm Raporu (Lessons Learned)")
            report = st.session_state.finalized_report
            st.success("Bu problem bilgi bankamıza (Knowledge Base) başarıyla eklendi!")
            
            st.subheader(report.get("title", "Problem Raporu"))
            st.write(f"**Kayıt ID:** `{report.get('record_id')}`")
            st.write(f"**Durum:** `{report.get('status')}`")
            
            st.markdown("### 🎓 Alınan Dersler (Lessons Learned)")
            st.info(report.get("lessons_learned", "Bilgi yok."))
            
        elif not st.session_state.current_session_id:
            st.title("Yeni Problem Çözüm Oturumu")
            with st.form("new_session_form"):
                problem_desc = st.text_area("Problem Açıklaması", height=100, placeholder="En az 20 karakter uzunluğunda problemi detaylıca açıklayın...")
                methodology = st.selectbox("Metodoloji", ["5why", "ishikawa", "8d", "pdca"])
                start_btn = st.form_submit_button("Oturumu Başlat")
                
                if start_btn:
                    if len(problem_desc) < 20:
                        st.error("Problem açıklaması çok kısa.")
                    else:
                        with st.spinner("Bağlam analiz ediliyor..."):
                            resp = requests.post(
                                f"{API_URL}/sessions",
                                headers=get_headers(),
                                json={"problem_description": problem_desc, "methodology": methodology}
                            )
                            if resp.status_code == 200:
                                data = resp.json()["data"]
                                st.session_state.current_session_id = data["session_id"]
                                st.session_state.similar_problems = data.get("similar_problems", [])
                                st.session_state.chat_history = [
                                    {"role": "assistant", "content": data["next_prompt"]}
                                ]
                                st.rerun()
                            else:
                                st.error(resp.json().get("error", "Bilinmeyen hata"))
        else:
            st.title("💬 Problem Analizi")
            
            # Chat history
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
            # Chat input
            if prompt := st.chat_input("Yanıtınızı girin..."):
                # Display user message
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)
                    
                # Send to API
                with st.spinner("AI düşünüyor..."):
                    resp = requests.post(
                        f"{API_URL}/sessions/{st.session_state.current_session_id}/steps",
                        headers=get_headers(),
                        json={"response": prompt}
                    )
                    
                    if resp.status_code == 200:
                        data = resp.json()["data"]
                        if data["status"] == "completed":
                            ai_msg = data.get("message", "Analiz tamamlandı. Lütfen soldaki menüden oturumu finalize edin.")
                        else:
                            ai_msg = data["next_prompt"]
                            
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_msg})
                        st.rerun()
                    else:
                        st.error(resp.json().get("error", "Yanıt işlenemedi."))

    with col2:
        st.header("🔍 Benzer Problemler")
        if st.session_state.similar_problems:
            for prob in st.session_state.similar_problems:
                with st.expander(f"📌 {prob['payload']['title'][:30]}... ({prob['score']}%)"):
                    st.write(f"**Metodoloji:** {prob['payload']['methodology']}")
                    st.write(f"**Kök Neden:** {prob['payload']['root_cause'][:100]}...")
                    st.write(f"**Durum:** {prob['payload']['resolution_status']}")
        else:
            st.info("Bu probleme benzer geçmiş kayıt bulunamadı.")
