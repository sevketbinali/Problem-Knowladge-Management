# 📚 Problem Knowledge Management (PKM) - API Dökümantasyonu

Bu döküman, Problem Bilgi Yönetim Sistemi'nin (PKM) REST API mimarisini, endpoint detaylarını ve veri standartlarını tanımlar. Sistem, yapay zeka destekli problem çözme ve anlamsal arama (RAG) yeteneklerine odaklanmıştır.

## 🔗 Temel Bilgiler

* **Base URL:** `http://localhost:8000/api/v1`
* **Content-Type:** `application/json`
* **OpenAPI (Swagger) UI:** `http://localhost:8000/docs`
* **Zaman Damgaları:** ISO 8601 (UTC)

---

## 📦 Standart Yanıt Yapısı

Sistemdeki tüm yanıtlar aşağıdaki standart zarf (envelope) yapısını kullanır:

```json
{
  "status": "success | error",
  "data": { ... },       // Başarılı işlemde dönen veri (object veya array)
  "error": "hata detayı", // Hata durumunda teknik açıklama
  "message": "mesaj"     // Kullanıcıya yönelik bilgilendirme metni
}
```

---

## 🔐 Kimlik Doğrulama (Authentication)

API, **JWT (JSON Web Token)** kullanır. Korumalı endpoint'ler için `Authorization: Bearer <TOKEN>` header'ı zorunludur.

### `POST /auth/login`
Sisteme giriş yapar.
- **Request:** `{"email": "...", "password": "..."}`
- **Success:** Token ve kullanıcı bilgilerini döner.

---

## 💬 Problem Çözüm Oturumları (Sessions)

### `POST /sessions`
Yeni bir problem analiz oturumu başlatır.
- **Request:** 
  ```json
  {
    "problem_description": "Üretim hattındaki sensörlerde aşırı ısınma.",
    "methodology": "8d" // 5why, ishikawa, 8d, pdca
  }
  ```
- **Response:** `session_id`, ilk soru (`next_prompt`) ve benzer geçmiş vakalar (`similar_problems`).

### `POST /sessions/{session_id}/steps`
Yapay zekanın sorduğu soruya yanıt gönderir. AI, cevabı analiz ederek bir sonraki adımı belirler.

### `POST /sessions/{session_id}/finalize`
Analiz tamamlandığında oturumu kapatır. AI tarafından üretilen **Kök Neden** ve **Alınan Dersler** sentezlenerek veritabanına ve RAG motoruna (Qdrant) kaydedilir.

---

## 🧠 Bilgi Bankası (Knowledge Base / RAG)

Sistem, anlamsal benzerlik (Semantic Similarity) kullanarak arama yapar.

### `GET /knowledge/search`
Anlamsal arama gerçekleştirir.
- **Query Params:** `query`, `industry`, `department`
- **Logic:** Minimum **0.65** benzerlik eşiği uygulanır.
- **Response:** `SearchResult` listesi (id, score, payload).

---

## 🗄️ Kayıt Yönetimi (Records)

### `GET /records`
Sistemdeki tüm problem kayıtlarını listeler.
- **Dönen Veri:** `title`, `methodology`, `created_by` (oluşturan adı), `resolution_status` ("Tamamlandı" vb.), `created_at`.

### `GET /records/{record_id}`
Belirli bir kaydın tüm detaylarını döner. MarkDown formatındaki raporları da içerir.

### `DELETE /records/{record_id}`
Kaydı PostgreSQL ve Qdrant üzerinden kalıcı olarak siler.

---

## 🩺 Sistem Sağlığı ve Güvenlik

- **Healthcheck:** `GET /health/ready` ile tüm alt bileşenlerin (Postgres, Qdrant, Redis) durumu izlenebilir.
- **Rate Limiting:** IP bazlı istek sınırlandırma aktiftir. Limit aşıldığında `429 Too Many Requests` hatası döner.
- **Degraded Mode:** Qdrant veya Redis devre dışı kaldığında, sistem ana işlevlerini (problem çözme) sürdürmeye devam eder ancak arama özellikleri geçici olarak devre dışı bırakılır.

---
<div align="right">
  <sub>Son Güncelleme: 13 Mayıs 2026</sub>
</div>
