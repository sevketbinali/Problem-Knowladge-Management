<div align="center">

![PKM Banner](file:///C:/Users/sevke/.gemini/antigravity/brain/0ea3a970-4e9c-415b-8bde-6959c0a28b6f/pkm_banner_1778527812022.png)

# 🧠 Problem Knowledge Management (PKM)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Qdrant](https://img.shields.io/badge/Qdrant-f33?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech/)

**Kurumsal Hafızanızı Yapay Zeka ile Güçlendirin.**  
*Problemleri sadece çözmekle kalmayın, onları birer öğrenme fırsatına dönüştürün.*

[Kurulum Videosu](#) • [API Dökümantasyonu](API_DOCUMENTATION.md) • [Hata Bildir](#)

</div>

---

## ✨ Temel Özellikler

PKM, karmaşık problemleri çözmek ve bu çözümleri kurumsal hafızaya kazandırmak için tasarlanmış uçtan uca bir platformdur.

*   **🛠️ Standart Metodolojiler:** 5-Why, Ishikawa (Balık Kılçığı), 8D ve PDCA akışlarını AI rehberliğinde yönetin.
*   **🤖 Akıllı Rehberlik:** Gemini 3 Flash ile her adımda dinamik sorular ve yönlendirmeler.
*   **🔍 Semantik Arama (RAG):** Qdrant vektör veritabanı sayesinde, benzer geçmiş problemleri anında bulun.
*   **🎓 Otomatik Raporlama:** Oturum sonunda AI tarafından üretilen "Lessons Learned" (Alınan Dersler) raporları.
*   **🔐 Güvenli Yönetim:** JWT tabanlı kullanıcı yetkilendirme ve admin kontrol paneli.

---

## 🏗️ Sistem Mimarisi

PKM, modern ve ölçeklenebilir bir mikroservis yapısı üzerine inşa edilmiştir:

```mermaid
graph TD
    User([Kullanıcı / Streamlit]) <--> API[FastAPI Backend]
    API <--> LLM[Google Gemini 3 Flash]
    API <--> RAG[Qdrant Vector DB]
    API <--> DB[(PostgreSQL)]
    API <--> Cache[(Redis)]
    
    subgraph "Infrastructure"
        DB
        RAG
        Cache
    end
```

---

## 🚀 Hızlı Kurulum

Sistemi sadece birkaç dakika içinde ayağa kaldırabilirsiniz.

### 1. Hazırlık
`.env.example` dosyasını `.env` olarak kopyalayın ve **Google Gemini API Anahtarınızı** ekleyin:
```bash
cp .env.example .env
# Gemini API anahtarınızı dosyaya eklemeyi unutmayın!
```

### 2. Sistemi Başlat (Docker)
Tüm servisleri (API, Arayüz, Veritabanları) tek bir komutla ayağa kaldırın:
```bash
docker-compose up -d --build
```

*Not: Bu işlem ilk seferinde gerekli imajları indireceği için internet hızınıza bağlı olarak 1-2 dakika sürebilir.*

Sistem ayağa kalktığında:
- **Arayüz (Streamlit):** [http://localhost:8501](http://localhost:8501)
- **API (FastAPI):** [http://localhost:8000](http://localhost:8000)
- **API Dökümantasyonu:** [http://localhost:8000/docs](http://localhost:8000/docs)

adreslerinden erişilebilir olacaktır.

---

### 🔑 Giriş Bilgileri
Sistem ayağa kalkarken **otomatik olarak şu Admin hesabını tanımlayacaktır:**
* **E-mail:** `admin@pkm.local`
* **Şifre:** `Admin123!`

---

## 📸 Ekran Görüntüleri

| Giriş Ekranı | Analiz Süreci | Çözüm Raporu |
| :---: | :---: | :---: |
| ![Login]() | ![Chat]() | ![Report]() |

---

## 📂 Proje Yapısı

```text
├── src/
│   ├── api/            # API Endpoints (FastAPI)
│   ├── core/           # İş Mantığı & Metodolojiler
│   ├── infrastructure/ # DB & Servis Entegrasyonları
│   └── frontend/       # Streamlit Uygulaması
├── docker-compose.yml  # Konteyner Yapılandırması
└── README.md           # Bu dosya
```

