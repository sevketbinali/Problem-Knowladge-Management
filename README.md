<div align="center">

<img src="https://raw.githubusercontent.com/sevketbinali/Problem-Knowladge-Management/main/docs/assets/pkm_banner.png" alt="PKM Banner" width="100%" />

# 🧠 Problem Knowledge Management (PKM)
### *Kurumsal Hafızayı Yapay Zeka ile Akıllı Bir Varlığa Dönüştürün*

[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-f33?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![Gemini AI](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)

</div>

---

## 📌 Problem Tanımı ve Değer Önerisi

Endüstriyel ve kurumsal süreçlerde problemler kaçınılmazdır. Ancak asıl problem, **bilgi kaybıdır**. Çözülen sorunların detayları, kök nedenleri ve alınan dersler genellikle kişisel notlarda veya dağınık dosyalarda kaybolur.

**PKM (Problem Knowledge Management)**, bu bilgi kaybını önlemek için tasarlandı. Standart problem çözme metodolojilerini (8D, Ishikawa, 5-Why) yapay zeka ile birleştirerek;
- Problemleri yapılandırılmış bir şekilde analiz eder.
- Geçmişteki benzer vakaları **Semantik Arama (RAG)** ile anında hatırlar.
- Çözüm süreçlerinden otomatik olarak "Kurumsal Öğrenme" çıktıları üretir.

---

## 🛠️ Temel Arayüzler ve Kullanıcı Deneyimi

PKM, karmaşık analiz süreçlerini basitleştiren, yüksek estetikli (Premium Dark Theme) bir arayüz sunar.

### 🔐 1. Güvenli Erişim (Login UI)
JWT tabanlı yetkilendirme sistemi ile güvenli giriş. Kullanıcı bazlı kayıt takibi ve yetkilendirme hiyerarşisi.

### 💬 2. İnteraktif Analiz (Session & Methodology)
8D, Ishikawa ve 5-Why gibi karmaşık metodolojiler artık birer yük değil. 
- **AI Rehberliği:** Yapay zeka, seçilen metoda göre dinamik sorular sorar, kullanıcıyı yönlendirir ve tutarsız cevapları (Döngüsel Mantık Tespiti) fark eder.
- **Benzer Problem Önerisi:** Analiz sırasında, girilen bilgilere istinaden ilişkili olabilecek ve daha önce yaşanmış problemler anlık olarak gösterilir.

### 🧠 3. Bilgi Bankası & Semantic Search
Klasik anahtar kelime aramasının ötesine geçin.
- **Anlamsal Hafıza:** Qdrant Vektör Veritabanı sayesinde, anlamsal olarak benzer geçmiş problemler benzerlik oranlarına göre listelenir.
- **Filtreleme:** Departman, metodoloji veya etiket bazlı gelişmiş daraltma seçenekleri.

### 📊 4. Problem Kayıtları Yönetimi (Unified Visualization)
Tüm problem kayıtları; açıklamalar, kök neden analizleri ve alınan dersler ile hiyerarşik ve okunabilir bir yapıda sunulur. Geçmişteki tüm vakaların durum takibi ve yönetimi tek bir merkezden yapılır.

---

## ⚙️ Teknik Mimari ve AI Entegrasyonu

Proje, modern bir mikroservis ve RAG (Retrieval-Augmented Generation) mimarisi üzerine kurulmuştur.

- **Backend:** FastAPI (Python) - Yüksek performanslı asenkron yapı.
- **Frontend:** Next.js 14 - Hızlı, SEO dostu ve reaktif arayüz.
- **AI Engine:** Google Gemini 1.5 Flash & Text-Embedding-004.
- **Vector DB:** Qdrant - Milyonlarca kayıt arasında milisaniyeler içinde benzerlik araması.
- **Relational DB:** PostgreSQL - Yapılandırılmış verilerin ve kullanıcı ilişkilerinin yönetimi.
- **Caching:** Redis - Arama sonuçlarının ve oturum verilerinin hızlandırılması.

---

## 🚀 Hızlı Başlangıç (Docker)

Sistemi tüm bileşenleriyle ayağa kaldırmak için:

1.  `.env.example` dosyasını `.env` olarak kopyalayın ve Gemini API anahtarınızı girin.
2.  Terminalde aşağıdaki komutu çalıştırın:

```bash
docker-compose up -d --build
```

**Erişim Noktaları:**
- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **API Dökümantasyonu:** `http://localhost:8000/docs`

---

## 🌟 Neden PKM? (Yenilikçilik)

PKM, sadece bir veri giriş formu değildir. **"Semantik Kurumsal Hafıza"** kavramını hayata geçirir. 
- **Otomatik Sentez:** Analiz bitiminde AI, tüm süreci özetleyerek "Alınan Dersler" (Lessons Learned) bölümünü otomatik yazar.
- **Hata Önleme:** AI, analiz sırasında verilen cevapların kalitesini denetler, yetersiz cevaplarda kullanıcıyı daha derin analiz yapmaya zorlar.

---
<div align="center">
  <sub>Problem Çözme Mükemmeliyeti İçin Tasarlandı • 2026</sub>
</div>
