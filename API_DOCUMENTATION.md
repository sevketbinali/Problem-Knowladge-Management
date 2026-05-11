# 📚 Problem Knowledge Management (PKM) - API Dökümantasyonu

Bu döküman, Problem Bilgi Yönetim Sistemi'nin (PKM) dışa açık olan REST API mimarisini, endpoint detaylarını ve iletişim standartlarını tanımlar. Bu doküman projenin evrimine paralel olarak güncel tutulacaktır.

## 🔗 Temel Bilgiler

* **Base URL:** `http://localhost:8000/api/v1`
* **Content-Type:** `application/json`
* **OpenAPI (Swagger) UI:** `http://localhost:8000/docs`

---

## 📦 Standart Yanıt Zarfı (Envelope)

Sistemdeki başarılı veya başarısız **tüm istekler** (Healthcheck haricinde) aşağıdaki `APIResponse` zarf yapısına uygun olarak döner. Bu sayede istemciler (Frontend/Mobil) standart bir hata/başarı kontrolü yapabilir.

```json
{
  "status": "success | error",
  "data": { ... } // Başarılı yanıtta veri buradadır, hata varsa null olur.
  "error": "hata detayı" // Hata durumunda detay buradadır, başarılıysa null olur.
  "message": "opsiyonel mesaj" // Kullanıcıya gösterilebilecek dostane bir metin.
}
```

---

## 🔐 Kimlik Doğrulama (Authentication)

API, yetkilendirme için **JWT (JSON Web Token)** kullanır. Korumalı endpointlere erişmek için Header'da `Authorization: Bearer <TOKEN>` gönderilmelidir.

### `POST /auth/login`
Sisteme giriş yapar ve Access Token döndürür.
* **Gövde (Body):** `{"email": "admin@pkm.local", "password": "..."}`
* **Başarılı Yanıt:** `{"access_token": "eyJhbG...", "token_type": "bearer", "user": {"id": "...", "role": "admin", ...}}`

---

## 💬 Problem Çözüm Oturumları (Sessions)

Kullanıcıların yapay zeka ile etkileşime girip adım adım problem çözdükleri akıştır.

### `POST /sessions`
Yeni bir problem çözme oturumu başlatır.
* **Gövde (Body):**
  ```json
  {
    "problem_description": "Üretim hattındaki 3 numaralı sensör aşırı ısınıyor.",
    "methodology": "5why" // Desteklenenler: 5why, ishikawa, 8d, pdca
  }
  ```
* **Yanıt:**
  ```json
  "data": {
    "session_id": "uuid-...",
    "methodology": "5why",
    "current_step": 0,
    "next_prompt": "Bu problem neden oluşuyor?",
    "similar_problems": [ ... ] // RAG'dan gelen benzer geçmiş problemler
  }
  ```

### `POST /sessions/{session_id}/steps`
Aktif oturumdaki soruya yanıt verir.
* **Gövde (Body):** `{"response": "Kablo bağlantısında bir kopukluk tespit ettik."}`
* **Yanıt:** Yapay zekanın ürettiği bir sonraki soruyu (`next_prompt`) döndürür.

### `POST /sessions/{session_id}/back`
Kullanıcı yanlış bir cevap verdiğinde bir önceki adıma geri dönmesini sağlar. LLM bağlamı geri alınır.
* **Yanıt:** Önceki soruyu ve kullanıcının verdiği eski yanıtı döndürür.

### `POST /sessions/{session_id}/finalize`
Tüm adımlar (örneğin 5. Neden) tamamlandığında oturumu sonlandırır, Alınan Dersler'i (Lessons Learned) oluşturur ve veritabanına kaydeder.
* **Yanıt:** Kaydedilen problemin referans numarasını ve analiz özetini döner.

---

## 🧠 Bilgi Bankası (Knowledge Base / RAG)

Önceden çözülmüş ve vektör veritabanına kaydedilmiş problemlerde arama yapar.

### `POST /knowledge/search`
Anlamsal arama (Semantic Search) yapar. Redis üzerinden önbelleklenir.
* **Gövde (Body):**
  ```json
  {
    "query": "Isınma ve sensör arızaları",
    "filters": {"department": "Üretim", "resolution_status": "resolved"},
    "limit": 5
  }
  ```
* **Yanıt:** Benzerlik skoruna (`score`) göre sıralanmış `SearchResult` listesi döndürür. Qdrant ulaşılamazsa 503 (Degraded Mode) hatası döner.

---

## 🗄️ Kayıt Yönetimi (Records)

*Sadece yetkisi olan yöneticiler kullanabilir.*

### `GET /records`
Sayfalama (Pagination) destekli tüm kayıtları listeler.
* **Query Params:** `?skip=0&limit=20`

### `GET /records/{record_id}`
ID'si verilen problemin kök nedeni, adımları ve alınan dersleri dahil tüm detaylarını döner.

### `PUT /records/{record_id}`
Kayıt detaylarını günceller. Qdrant (Vektör DB) tarafındaki gömülmeleri (embeddings) de otomatik günceller. İşlem başarısız olursa PostgreSQL atomik olarak Rollback yapar.

### `DELETE /records/{record_id}`
Kaydı hem ilişkisel veritabanından hem de vektör veritabanından kalıcı olarak siler.

---

## 🩺 Sistem Durumu (Healthcheck)

### `GET /health/ready`
Sistemin (PostgreSQL, Qdrant, Redis) tamamen çalışır durumda olup olmadığını kontrol eder. CI/CD veya Docker Healthcheck tarafından kullanılır.

---

## 🛑 Rate Limiting ve Hatalar

API, **Redis** tabanlı bir sınırlandırma (Rate Limit) kullanır. Bir IP adresinden 60 saniyede yapılabilecek istek sayısı sınırlıdır (örn: 100).
Aşıldığı takdirde:
* **HTTP 429 Too Many Requests** döner.

**Sık Karşılaşılan Hata Kodları:**
* `400 Bad Request`: Beklenmeyen oturum durumu.
* `401 Unauthorized`: Token geçersiz veya süresi dolmuş.
* `403 Forbidden`: Admin yetkisi gereken endpoint'e standart kullanıcı isteği.
* `422 Unprocessable Entity`: Validasyon hatası (örn. 10 karakterden az yanıt girilmesi).
* `503 Service Unavailable`: Qdrant/Redis gibi alt servislerin kapalı olması durumu.
