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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
    }

    /* Global Styles */
    .main {
        padding: 2rem;
    }

    /* Professional Card Styling */
    .report-card {
        padding: 1.5rem;
        border-radius: 0.75rem;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 1.5rem;
        transition: all 0.2s;
    }
    .report-card:hover {
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        border-color: #cbd5e1;
    }

    .report-card h4 {
        color: #0f172a;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-size: 1.25rem;
    }

    /* Department & Tag Layout */
    .meta-row {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }

    .dept-badge {
        background: #0f172a;
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    .tag-container {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }

    .tag-badge {
        background: #f1f5f9;
        color: #475569;
        padding: 2px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        border: 1px solid #e2e8f0;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        color: #f8fafc;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #cbd5e1;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* Step Nodes */
    .step-node {
        padding: 1rem;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin-bottom: 0.75rem;
        font-size: 0.925rem;
        color: #334155;
    }

    .connector {
        color: #3b82f6;
        font-weight: bold;
        text-align: center;
        margin: -4px 0 8px 0;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 0.5rem;
        font-weight: 500;
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
    
    # --- Filter UI ---
    with st.expander("🔍 Arama ve Filtreleme", expanded=True):
        col_search, col_dept, col_meth, col_sort = st.columns([2, 1, 1, 1])
        with col_search:
            search_query = st.text_input("Anahtar Kelime Ara", placeholder="Problem, neden veya çözüm...")
        with col_dept:
            dept_filter = st.selectbox("Bölüm", ["Tümü", "Üretim", "Lojistik", "Kalite", "Bilgi İşlem", "Finans"])
        with col_meth:
            meth_filter = st.selectbox("Metodoloji", ["Tümü", "5why", "ishikawa", "8d", "pdca"])
        with col_sort:
            sort_order = st.selectbox("Sıralama", ["Yeniden Eskiye", "Eskiden Yeniye"])

    # Prepare params
    params = {}
    if search_query: params["q"] = search_query
    if dept_filter != "Tümü": params["department"] = dept_filter
    if meth_filter != "Tümü": params["methodology"] = meth_filter
    params["sort"] = "newest" if sort_order == "Yeniden Eskiye" else "oldest"

    st.divider()
    
    with st.spinner("Kayıtlar yükleniyor..."):
        resp = requests.get(f"{API_URL}/records", headers=get_headers(), params=params)
        if resp.status_code == 200:
            records = resp.json()["data"]
            if not records:
                st.info("Arama kriterlerine uygun kayıt bulunamadı.")
            else:
                for r in records:
                    with st.container():
                        # Tags display
                        tags_html = "".join([f"<span class='tag-badge'>#{t}</span>" for t in r.get('tags', [])])
                        
                        st.markdown(f"""
                        <div class='report-card'>
                            <h4>{r['title']}</h4>
                            <div class='meta-row'>
                                <span class='dept-badge'>{r.get('department', 'GENEL')}</span>
                                <div class='tag-container'>{tags_html}</div>
                                <span style='color: #64748b; font-size: 0.75rem; margin-left: auto;'>{r['methodology'].upper()} | {r['created_at'][:10]}</span>
                            </div>
                            <p style='color: #334155; font-size: 0.95rem;'><b>Kök Neden:</b> {r['root_cause'][:200]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Detayları Gör: {r['id'][:8]}...", key=r['id']):
                            st.session_state.selected_record_id = r['id']
                            st.rerun()
        else:
            st.error("Kayıtlar alınamadı.")

def render_record_detail(record_id):
    if st.button("⬅️ Listeye Geri Dön"):
        st.session_state.selected_record_id = None
        st.rerun()
        
    with st.spinner("Detaylar getiriliyor..."):
        resp = requests.get(f"{API_URL}/records/{record_id}", headers=get_headers())
        if resp.status_code == 200:
            r = resp.json()["data"]
            st.title(f"📄 {r['title']}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Tags & Meta
                tags_html = "".join([f"<span class='tag-badge'>#{t}</span>" for t in r.get('tags', [])])
                st.markdown(f"""
                <div class='meta-row' style='margin-bottom: 1.5rem;'>
                    <span class='dept-badge'>{r.get('department', 'Genel')}</span>
                    <div class='tag-container'>{tags_html}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='report-card'>
                    <h3 style='color: #0f172a; font-size: 1.1rem; margin-top: 0;'>🎯 Problem Tanımı</h3>
                    <p style='color: #334155;'>{r['problem_description']}</p>
                    <hr style='border: 0; border-top: 1px solid #e2e8f0; margin: 1.5rem 0;'>
                    <h3 style='color: #0f172a; font-size: 1.1rem;'>🔍 Kök Neden</h3>
                    <p style='color: #0f172a; font-weight: 600;'>{r['root_cause']}</p>
                    <hr style='border: 0; border-top: 1px solid #e2e8f0; margin: 1.5rem 0;'>
                    <h3 style='color: #0f172a; font-size: 1.1rem;'>🎓 Alınan Dersler</h3>
                    <p style='color: #334155;'>{r['lessons_learned']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.info(f"**Bölüm:** {r.get('department', 'Genel')}")
                st.info(f"**Metodoloji:** {r['methodology'].upper()}")
                st.info(f"**Tarih:** {r['created_at'][:10]}")
                
                # If it's a 5-Why, we can try to show the chain if step_responses exist
                if r['methodology'] == '5why' and r.get('step_responses'):
                    st.subheader("⛓️ Neden Zinciri")
                    steps = r['step_responses']
                    if isinstance(steps, dict):
                        for i in range(1, 6):
                            val = steps.get(str(i)) or steps.get(i)
                            if val:
                                st.markdown(f"<div class='step-node'><b>{i}. Neden:</b><br>{val}</div>", unsafe_allow_html=True)
        else:
            st.error("Kayıt detayları alınamadı.")

def render_why_chain():
    """Visual representation of 5-Why flow."""
    whys = [msg for msg in st.session_state.chat_history if msg["role"] == "user"]
    if whys:
        st.subheader("⛓️ Analiz Akışı (Neden-Sonuç Zinciri)")
        for i, msg in enumerate(whys):
            st.markdown(f"""
            <div class='step-node' style='margin-left: {i*25}px'>
                <b>{i+1}. NEDEN</b>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
            if i < len(whys) - 1:
                st.markdown(f"<div class='connector' style='margin-left: {i*25 + 40}px'>↓</div>", unsafe_allow_html=True)
        st.divider()

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
        if st.session_state.get("selected_record_id"):
            render_record_detail(st.session_state.selected_record_id)
        else:
            render_knowledge_base()
    else:
        col1, col2 = st.columns([2, 1])

        with col1:
            if st.session_state.get("finalized_report"):
                st.title("📄 Çözüm Raporu (One-Pager)")
                report = st.session_state.finalized_report
                # Prepare Tags HTML
                tags = report.get('tags', [])
                tags_html = "".join([f"<span style='background: #e1f5fe; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; color: #0288d1; margin-right: 8px; border: 1px solid #b3e5fc;'>#{t}</span>" for t in tags])
                
                st.markdown(f"""
                <div class='report-card'>
                    <h2>{report.get('title', 'Problem Raporu')}</h2>
                    <p><b>Bölüm:</b> {report.get('department', 'Genel')} | <b>Metodoloji:</b> {report.get('methodology', '').upper()}</p>
                    <p><b>Kayıt ID:</b> <code>{report.get('record_id')}</code> | <b>Durum:</b> finalized</p>
                    <div style='margin: 15px 0;'>{tags_html}</div>
                    <hr>
                    <h3>🎓 Alınan Dersler (Lessons Learned)</h3>
                    <p>{report.get('lessons_learned', 'Bilgi yok.')}</p>
                    <hr>
                    <p><small>Bu kayıt otomatik olarak Qdrant Vektör DB'ye ve PostgreSQL'e indekslenmiştir.</small></p>
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
                
                # Check if session is actually completed to show review form
                session_completed = any("Analiz tamamlandı" in str(msg.get("content", "")) for msg in st.session_state.chat_history)
                
                if session_completed and not st.session_state.get("finalized_report"):
                    st.success("✅ Analiz Adımları Tamamlandı!")
                    st.write("Lütfen kaydı finalize etmeden önce AI tarafından önerilen detayları inceleyin:")
                    
                    # Fetch suggestions if not already in session state
                    if "suggestions" not in st.session_state:
                        with st.spinner("AI önerileri hazırlanıyor..."):
                            resp = requests.get(
                                f"{API_URL}/sessions/{st.session_state.current_session_id}/suggestions",
                                headers=get_headers()
                            )
                            if resp.status_code == 200:
                                st.session_state.suggestions = resp.json()["data"]
                            else:
                                st.session_state.suggestions = {"department": "Üretim", "summary": "Problem Özeti", "tags": []}

                    sug = st.session_state.suggestions
                    
                    # Track edits
                    if "edited_fields" not in st.session_state:
                        st.session_state.edited_fields = set()

                    def mark_edited(field):
                        st.session_state.edited_fields.add(field)

                    with st.form("finalize_review_form"):
                        st.subheader("📋 Kayıt Detaylarını Gözden Geçir")
                        
                        col_a, col_b = st.columns(2)
                        
                        # Department
                        with col_a:
                            is_dept_ai = "department" not in st.session_state.edited_fields
                            dept_label = "Bölüm" + (" ✨" if is_dept_ai else "")
                            dept = st.selectbox(
                                dept_label, 
                                ["Üretim", "Lojistik", "Kalite", "Bilgi İşlem", "Finans"],
                                index=["Üretim", "Lojistik", "Kalite", "Bilgi İşlem", "Finans"].index(sug.get("department", "Üretim")),
                                help="Yapay Zeka tarafından önerildi" if is_dept_ai else None,
                                on_change=mark_edited, args=("department",)
                            )
                        
                        # Summary
                        with col_b:
                            is_sum_ai = "summary" not in st.session_state.edited_fields
                            sum_label = "Özet Başlık" + (" ✨" if is_sum_ai else "")
                            summary = st.text_input(
                                sum_label, 
                                value=sug.get("summary", ""),
                                help="Yapay Zeka tarafından önerildi" if is_sum_ai else None,
                                on_change=mark_edited, args=("summary",)
                            )
                        
                        # Tags
                        is_tags_ai = "tags" not in st.session_state.edited_fields
                        tags_label = "Etiketler (Virgülle ayırın)" + (" ✨" if is_tags_ai else "")
                        suggested_tags = ", ".join(sug.get("tags", []))
                        tags_str = st.text_input(
                            tags_label, 
                            value=suggested_tags,
                            help="Yapay Zeka tarafından önerildi" if is_tags_ai else None,
                            on_change=mark_edited, args=("tags",)
                        )
                        
                        st.caption("✨ simgesi olan alanlar AI tarafından önerilmiştir. Değişiklik yaparsanız simge kaybolur.")
                        
                        final_btn = st.form_submit_button("✅ Onayla ve Bilgi Bankasına Kaydet")
                        if final_btn:
                            with st.spinner("Rapor üretiliyor ve kaydediliyor..."):
                                resp = requests.post(
                                    f"{API_URL}/sessions/{st.session_state.current_session_id}/finalize",
                                    headers=get_headers(),
                                    json={"department": dept, "summary": summary, "tags": tags_str}
                                )
                                if resp.status_code == 200:
                                    data = resp.json()["data"]
                                    st.session_state.current_session_id = None
                                    st.session_state.chat_history = []
                                    st.session_state.suggestions = None
                                    st.session_state.edited_fields = set()
                                    st.session_state.finalized_report = data
                                    st.success("Kayıt başarıyla tamamlandı!")
                                    st.rerun()
                                else:
                                    st.error("Finalize işlemi sırasında bir hata oluştu.")
                else:
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
                                    ai_msg = "✅ Analiz tamamlandı. Lütfen yukarıdaki formu doldurarak kaydı bitirin."
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
                        st.write(f"**Bölüm:** {prob['payload'].get('department', 'Belirtilmemiş')}")
                        st.write(f"**Metodoloji:** {prob['payload']['methodology']}")
                        st.write(f"**Kök Neden:** {prob['payload']['root_cause'][:150]}...")
                        st.info(f"Kayıt: {prob['id'][:8]}...")
            else:
                st.info("Bu probleme benzer geçmiş kayıt bulunamadı.")
