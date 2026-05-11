# Proje Uygulama Günlükleri (Implementation Logs)

Bu dizin, Problem Knowledge Management projesinin geliştirme sürecindeki tüm aşamaların detaylı dökümantasyonunu içerir.

## Döküman Listesi

1.  **[Gemini API Geçişi](task_01_gemini_migration.md)**: OpenAI'dan Gemini SDK v2'ye geçiş ve model yapılandırması.
2.  **[Auth & Güvenlik](task_05_auth_implementation.md)**: Kullanıcı yönetimi, JWT ve şifre hashleme güvenliği.
3.  **[Doğrulama & Metodoloji](task_07_09_validation_methodology.md)**: Domain validator'ları ve Methodology Engine (Ishikawa, 8D vb.).
4.  **[LLM & RAG Altyapısı](task_14_16_llm_rag_infrastructure.md)**: Vektör veritabanı (Qdrant), Embedding servisi ve Gemini üretici yapay zeka entegrasyonu.
5.  **[Redis & Hız Sınırlandırma](task_17_redis_rate_limiting.md)**: Önbellekleme yapısı ve API hız sınırlandırması.
6.  **[Celery & Embedding Kuyruğu](task_15_celery_embedding_queue.md)**: Arka planda vektör üretimi ve yeniden deneme mekanizması.
7.  **[Oturum Yönetimi](task_19_session_service.md)**: Problem çözme oturumları, adım takibi ve LLM takip soruları.
8.  **[Analiz ve Raporlama](task_20_analysis_reporting.md)**: Nihai rapor üretimi, Lessons Learned ve otomatik indeksleme.
9.  **[Arama Servisi](task_21_search_service.md)**: Semantik arama, önbellekleme ve denetim izleri.
10. **[API Router'ları](task_22_api_routers.md)**: Auth, Session, Analysis ve Search uç noktalarının FastAPI entegrasyonu.
11. **[Degraded Mode](task_23_degraded_mode.md)**: Bağımlılık kontrolü ve kısıtlı çalışma modu stratejileri.

## Güncelleme Politikası
Her büyük görev (Task) veya özellik (Feature) tamamlandığında, aşağıdaki şablona göre yeni bir günlük dosyası eklenmelidir:
- Görev Özeti
- Yapılan İşlemler
- Başarı Kriterleri ve Sonuçlar
- Karşılaşılan Hatalar ve Çözümler
