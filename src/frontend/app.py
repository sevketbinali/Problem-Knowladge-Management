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
if "similar_problems" not in st.session_state:
    st.session_state.similar_problems = []
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Analysis"

# --- Custom Styling ---
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #3f51b5;
        color: white;
    }
    .stChatFloatingInputContainer {
        padding-bottom: 20px;
    }
    .report-card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        border-left: 5px solid #3f51b5;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .step-node {
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #fff;
        margin-left: 20px;
        border-left: 3px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

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

def render_knowledge_base():
    st.title("📚 Kurumsal Bilgi Bankası")
    st.write("Daha önce tamamlanmış ve AI tarafından analiz edilmiş tüm problem kayıtları.")
    
    with st.spinner("Kayıtlar yükleniyor..."):
        resp = requests.get(f"{API_URL}/records", headers=get_headers())
        if resp.status_code == 200:
            records = resp.json()["data"]
            if not records:
                st.info("Henüz tamamlanmış bir kayıt bulunmuyor.")
            else:
                for r in records:
                    with st.container():
                        st.markdown(f"""
                        <div class='report-card'>
                            <h4>{r['title']}</h4>
                            <p><b>Metodoloji:</b> {r['methodology']} | <b>Tarih:</b> {r['created_at'][:10]}</p>
                            <p><b>Kök Neden:</b> {r['root_cause']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Detayları Gör: {r['id'][:8]}...", key=r['id']):
                            st.session_state.selected_record_id = r['id']
                            st.rerun()
        else:
            st.error("Kayıtlar alınamadı.")

def render_why_chain():
    """Visual representation of 5-Why flow."""
    whys = [msg for msg in st.session_state.chat_history if msg["role"] == "user"]
    if whys:
        st.subheader("🛠️ Analiz Akışı (Neden-Sonuç Zinciri)")
        for i, msg in enumerate(whys):
            st.markdown(f"""
            <div class='step-node' style='margin-left: {i*30}px'>
                <b>{i+1}. Neden:</b> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
            if i < len(whys) - 1:
                st.markdown(f"<div style='margin-left: {i*30 + 40}px'>↓</div>", unsafe_allow_html=True)

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
        st.session_state.view_mode = st.radio("Mod Seçimi", ["Yeni Analiz", "Bilgi Bankası"])
        
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
                st.info("Oturum başlatmak için yan menüyü kullanın.")
            else:
                if st.button("Yeni Oturum Başlat"):
                    st.session_state.finalized_report = None
                    st.rerun()

    # Main Layout
    if st.session_state.view_mode == "Bilgi Bankası":
        render_knowledge_base()
    else:
        col1, col2 = st.columns([2, 1])

        with col1:
            if st.session_state.get("finalized_report"):
                st.title("📄 Çözüm Raporu (One-Pager)")
                report = st.session_state.finalized_report
                st.markdown(f"""
                <div class='report-card'>
                    <h2>{report.get('title', 'Problem Raporu')}</h2>
                    <p><b>Kayıt ID:</b> <code>{report.get('record_id')}</code> | <b>Durum:</b> finalized</p>
                    <hr>
                    <h3>🎓 Alınan Dersler (Lessons Learned)</h3>
                    <p>{report.get('lessons_learned', 'Bilgi yok.')}</p>
                    <hr>
                    <p><small>Bu kayıt otomatik olarak Qdrant Vektör DB'ye indekslenmiştir.</small></p>
                </div>
                """, unsafe_allow_html=True)
                
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
                
                # Visual Analysis Aid
                render_why_chain()
                
                st.divider()
                
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
            st.write("Bilgi bankasındaki semantik eşleşmeler:")
            if st.session_state.similar_problems:
                for prob in st.session_state.similar_problems:
                    with st.expander(f"📌 {prob['payload']['title'][:30]}... ({int(prob['score']*100)}%)"):
                        st.write(f"**Metodoloji:** {prob['payload']['methodology']}")
                        st.write(f"**Kök Neden:** {prob['payload']['root_cause'][:150]}...")
                        st.info(f"Kayıt: {prob['id'][:8]}...")
            else:
                st.info("Bu probleme benzer geçmiş kayıt bulunamadı.")

