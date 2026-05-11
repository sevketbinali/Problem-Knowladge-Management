# 🗄️ PKM Veri Yönetimi ve Kayıt Erişimi Rehberi

Problem Knowledge Management (PKM) sistemi, verileri hem operasyonel devamlılık hem de akıllı arama yetenekleri için iki farklı katmanda saklar.

---

## 1. Veri Saklama Katmanları

### A. İlişkisel Veritabanı (PostgreSQL)
Tüm yapılandırılmış verilerin "ana kaynağı" (Source of Truth) burasıdır.
- **Tablo:** `problem_records`
- **İçerik:** Problem açıklaması, kullanılan metodoloji, adım adım verilen tüm yanıtlar, kök neden ve AI tarafından üretilen "Lessons Learned" raporu.
- **Erişim:** SQL üzerinden veya API'deki `/api/v1/records` endpoint'i üzerinden erişilebilir.

### B. Vektör Veritabanı (Qdrant)
Anlamsal (semantic) arama ve "Benzer Problemleri Getir" özelliği için kullanılır.
- **Koleksiyon:** `problem_records`
- **İçerik:** Problemlerin metin içeriklerinin vektör karşılıkları ve meta veriler.
- **Erişim:** Qdrant Dashboard (Port 6333) veya API'deki RAG motoru üzerinden erişilebilir.

---

## 2. Kayıtlara Nasıl Erişilir?

### A. Arayüz Üzerinden (Önerilen)
Sistem arayüzünde sol menüden **"Bilgi Bankası"** modunu seçerek:
1. Tüm geçmiş kayıtları listeleyebilirsiniz.
2. Kayıtların özetlerini (Kök neden, tarih, metodoloji) görebilirsiniz.
3. **Kayıt ID** (UUID) numarasını alarak teknik takip yapabilirsiniz.

### B. API Üzerinden (Teknik)
Eğer verileri başka bir sisteme aktarmak veya dışarıdan sorgulamak isterseniz:
- `GET /api/v1/records`: Tüm kayıtları listeler.
- `GET /api/v1/records/{id}`: Belirli bir kaydın tüm detaylarını (soru-cevap geçmişi dahil) getirir.

---

## 3. Kayıt ID (UUID) Nedir?
Her problem kaydı, dünyada eşi olmayan bir kimlik numarasına (UUID) sahiptir. Örn: `550e8400-e29b-41d4-a716-446655440000`. 
Bu ID;
- Nginx/App loglarında problemi takip etmek,
- Vektör veritabanında silme/güncelleme yapmak,
- Şirket içi raporlarda referans vermek için kullanılır.

---

## 4. Kayıtların Doğrulanması (RAG Testi)
Eğer girdiğiniz bir problem "Benzer Problemler" kısmında çıkmıyorsa:
1. Oturumu **"Finalize Et"** butonuna basarak bitirdiğinizden emin olun. (Sadece finalize edilenler bilgi bankasına kaydedilir).
2. Arka planda `embedding` servisinin (Gemini API) aktif olduğunu kontrol edin.
3. `pkm_api` loglarında "Successfully embedded record" mesajını görün.

---
*Bu sistem, her analiz sonunda kurumsal hafızanızı bir adım daha ileriye taşır.* 🧠
