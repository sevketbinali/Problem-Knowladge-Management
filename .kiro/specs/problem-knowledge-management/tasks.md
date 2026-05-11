# Uygulama Planı: Problem Bilgi Yönetim Sistemi

## Genel Bakış

Bu plan, FastAPI + PostgreSQL + Qdrant + Redis + Celery mimarisi üzerine inşa edilen Problem Bilgi Yönetim Sistemi'ni katman katman uygular. Her görev tek bir sorumluluğa sahiptir; her alt görev somut ve doğrulanabilir bir başarı kriteri içerir.

**Uygulama dili:** Python (FastAPI, SQLAlchemy 2.0 async, Pydantic v2, Hypothesis)

---

## Görevler

- [x] 1. Proje iskeletini ve temel yapılandırmayı oluştur
  - `src/`, `tests/unit/`, `tests/integration/`, `tests/smoke/` dizin yapısını oluştur
  - `pyproject.toml` veya `requirements.txt` içine bağımlılıkları ekle: fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, pydantic, redis, celery, qdrant-client, google-generativeai, bcrypt, hypothesis, pytest, pytest-asyncio
  - `.env.example` dosyasını oluştur: `DATABASE_URL`, `QDRANT_URL`, `REDIS_URL`, `GEMINI_API_KEY`, `JWT_SECRET` yer tutucu değerleriyle
  - `docker-compose.yml` dosyasını yaz: fastapi, postgresql, qdrant, redis servisleri + adlandırılmış kalıcı volume'lar
  - `Dockerfile` yaz: sıkıştırılmış imaj boyutu ≤ 1 GB
  - Doğrulama: `docker-compose up --build` → `/ready` endpoint 120 saniye içinde HTTP 200 döndürür; `docker-compose down -v && docker-compose up` → veri kaybı yok
  - _Gereksinimler: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 2. Domain modelleri ve doğrulama katmanını uygula
  - [x] 2.1 Pydantic enum ve temel modelleri yaz
    - `MethodologyType`, `SessionStatus`, `EmbeddingStatus` enum'larını tanımla
    - `ProblemRecord`, `IshikawaData`, `WhyChain`, `EightDReport` Pydantic modellerini yaz
    - `APIResponse[T]` generic zarf modelini ve `ErrorDetail` modelini yaz
    - Doğrulama: Her modeli geçerli ve geçersiz verilerle örnekle; Pydantic `ValidationError` beklenen alanlarda fırlatılmalı
    - _Gereksinimler: 6.1, 11.2, 13.1_

  - [x] 2.2 Özellik 30 için property testi yaz — Serileştirme round-trip
    - **Özellik 30: Problem Kaydı Serileştirme Round-Trip**
    - `st.builds(ProblemRecord, ...)` stratejisiyle herhangi bir geçerli `ProblemRecord` nesnesi P için: `P == parse(serialize(P))` alan bazında değer ve tür eşitliği
    - Doğrulama: `pytest tests/unit/test_serialization.py::test_roundtrip` geçmeli
    - **Doğrular: Gereksinim 13.4**

  - [x] 2.3 Özellik 31 için property testi yaz — JSON şema uygunluğu
    - **Özellik 31: Serileştirme JSON Şema Uygunluğu**
    - `st.builds(ProblemRecord, ...)` stratejisiyle üretilen her JSON belgesi `ProblemRecord` JSON şemasına uygun olmalı
    - Doğrulama: `pytest tests/unit/test_serialization.py::test_schema_compliance` geçmeli
    - **Doğrular: Gereksinim 13.1**

  - [x] 2.4 Özellik 32 için property testi yaz — Ayrıştırma alan eşleşmesi
    - **Özellik 32: Ayrıştırma Alan Eşleşmesi**
    - Geçerli her JSON belgesi için ayrıştırılan nesnenin tüm alanları kaynak JSON ile değer ve tür olarak eşleşmeli
    - Doğrulama: `pytest tests/unit/test_serialization.py::test_parse_field_match` geçmeli
    - **Doğrular: Gereksinim 13.2**

  - [ ]* 2.5 Özellik 33 için property testi yaz — Pretty printer formatı
    - **Özellik 33: Pretty Printer Çıktı Formatı**
    - Her geçerli `ProblemRecord` için pretty printer çıktısı 2 boşluk girintili ve anahtarlar sözlüksel sırada olmalı
    - Doğrulama: `pytest tests/unit/test_serialization.py::test_pretty_printer` geçmeli
    - **Doğrular: Gereksinim 13.3**

  - [ ]* 2.6 Özellik 34 için property testi yaz — Bilinmeyen alan toleransı
    - **Özellik 34: Bilinmeyen Alan Toleransı**
    - Geçerli JSON'a ek bilinmeyen alanlar eklendiğinde ayrıştırma başarılı olmalı, bilinmeyen alanlar görmezden gelinmeli
    - Doğrulama: `pytest tests/unit/test_serialization.py::test_unknown_field_tolerance` geçmeli
    - **Doğrular: Gereksinim 13.5**

  - [ ]* 2.7 Özellik 35 için property testi yaz — Eksik zorunlu alan hata mesajı
    - **Özellik 35: Eksik Zorunlu Alan Hata Mesajı**
    - `st.sampled_from(required_fields)` stratejisiyle zorunlu alan eksik her JSON için hata mesajı eksik alanın adını açıkça belirtmeli
    - Doğrulama: `pytest tests/unit/test_serialization.py::test_missing_field_error` geçmeli
    - **Doğrular: Gereksinim 13.6**

- [~] 3. Kontrol noktası — Temel modeller
  - Tüm birim testleri geçmeli: `pytest tests/unit/test_serialization.py -v`
  - Soru varsa kullanıcıya sor.


- [ ] 4. Veritabanı altyapısını uygula
  - [x] 4.1 PostgreSQL şemasını ve SQLAlchemy modellerini yaz

    - `USERS`, `SESSIONS`, `PROBLEM_RECORDS`, `AUDIT_LOGS`, `EMBEDDING_QUEUE` tablolarını SQLAlchemy 2.0 async ORM ile tanımla
    - Alembic migration dosyasını oluştur
    - Bağlantı havuzu: min 5, max 20 bağlantı; tüm yazma işlemleri transaction içinde
    - Doğrulama: `alembic upgrade head` hatasız tamamlanmalı; tüm tablolar ve foreign key'ler oluşturulmalı
    - _Gereksinimler: 6.1, 9.5_

  - [x] 4.2 `PostgreSQLRepository` sınıfını yaz

    - `create_session`, `get_session`, `update_session`, `create_record`, `get_record`, `update_record`, `delete_record`, `list_records`, `create_audit_log` metodlarını uygula
    - Tüm metodlar async; yazma işlemleri transaction içinde
    - Doğrulama: Her metod için birim testi: geçerli girdi → beklenen dönüş; kayıt bulunamadığında `None` veya exception
    - _Gereksinimler: 6.1, 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 4.3 Özellik 23 için property testi yaz — Denetim logu bütünlüğü
    - **Özellik 23: Denetim Logu Bütünlüğü**
    - `st.sampled_from(["create","update","delete"])` stratejisiyle her işlem için: kullanıcı ID, zaman damgası, işlem türü ve önceki/sonraki değerler audit log kaydında bulunmalı
    - Doğrulama: `pytest tests/integration/test_audit.py::test_audit_log_integrity` geçmeli
    - **Doğrular: Gereksinim 9.5**

  - [ ]* 2.8 Özellik 16 için property testi yaz — Metadata null atama
    - **Özellik 16: Metadata Null Atama**
    - `st.fixed_dictionaries(...)` stratejisiyle sağlanan metadata alanları kaydedilmeli; sağlanmayanlar null olmalı
    - Doğrulama: `pytest tests/integration/test_records.py::test_metadata_null_assignment` geçmeli
    - **Doğrular: Gereksinim 6.5**

- [x] 5. Kimlik doğrulama ve yetkilendirme katmanını uygula
  - [x] 5.1 `AuthService` ve JWT middleware'i yaz
    - JWT token oluşturma, doğrulama ve yenileme fonksiyonlarını uygula
    - Bcrypt şifre hashleme: minimum 12 cost factor; düz metin şifre hiçbir zaman saklanmaz
    - `User` ve `Admin` rol kontrolü middleware'i yaz
    - Doğrulama: Geçerli token → 200; süresi dolmuş → 401; eksik → 401 (format doğrulaması yapılmadan); hatalı biçimli → 401 (format doğrulaması sonrası); yetersiz yetki → 403
    - _Gereksinimler: 10.1, 10.2, 10.3, 10.5, 10.7_

  - [x] 5.2 Özellik 25 için property testi yaz — Token durumu ve HTTP yanıt kodu eşleşmesi
    - **Özellik 25: Token Durumu ve HTTP Yanıt Kodu Eşleşmesi**
    - `st.sampled_from(TokenState)` stratejisiyle her token durumu için beklenen HTTP kodu döndürülmeli
    - Doğrulama: `pytest tests/unit/test_auth.py::test_token_http_code_mapping` geçmeli
    - **Doğrular: Gereksinim 10.1, 10.3, 10.7**

  - [x] 5.3 Özellik 26 için property testi yaz — Şifre hashleme güvenliği
    - **Özellik 26: Şifre Hashleme Güvenliği**
    - `st.text(min_size=8, max_size=100)` stratejisiyle her şifre için: saklanan hash bcrypt formatında ve ≥12 cost factor; düz metin hiçbir zaman saklanmaz
    - Doğrulama: `pytest tests/unit/test_auth.py::test_password_hashing_security` geçmeli
    - **Doğrular: Gereksinim 10.5**

- [x] 6. Kontrol noktası — Altyapı katmanı

  - `pytest tests/unit/test_auth.py tests/integration/test_audit.py -v` geçmeli
  - Soru varsa kullanıcıya sor.

- [x] 7. Doğrulama mantığını uygula
  - [x] 7.1 Problem açıklaması uzunluk doğrulayıcısını yaz
    - `validate_problem_description(text: str) -> None` fonksiyonu: 20–2000 karakter geçerli; dışarısı `ValidationError` fırlatır
    - Doğrulama: 19 karakter → hata; 20 karakter → geçer; 2000 karakter → geçer; 2001 karakter → hata
    - _Gereksinimler: 1.1, 1.3, 1.4_

  - [x] 7.2 Özellik 1 için property testi yaz — Problem açıklaması uzunluk doğrulaması
    - **Özellik 1: Problem Açıklaması Uzunluk Doğrulaması**
    - `st.text(min_size=0, max_size=3000)` stratejisiyle: 20–2000 arası → geçer; dışarısı → `ValidationError`
    - Doğrulama: `pytest tests/unit/test_validation.py::test_problem_description_length` geçmeli
    - **Doğrular: Gereksinim 1.1, 1.3, 1.4**

  - [x] 7.3 Adım yanıtı uzunluk doğrulayıcısını yaz
    - `validate_step_response(text: str) -> None` fonksiyonu: ≥10 karakter geçerli; <10 karakter `ValidationError` fırlatır
    - Doğrulama: 9 karakter → hata; 10 karakter → geçer; 1000 karakter → geçer
    - _Gereksinimler: 2.2_

  - [x] 7.4 Özellik 4 için property testi yaz — Adım yanıtı minimum uzunluk doğrulaması
    - **Özellik 4: Adım Yanıtı Minimum Uzunluk Doğrulaması**
    - `st.text(min_size=0, max_size=1000)` stratejisiyle: ≥10 karakter → kabul; <10 → reddedilir
    - Doğrulama: `pytest tests/unit/test_validation.py::test_step_response_min_length` geçmeli
    - **Doğrular: Gereksinim 2.2**

  - [x] 7.5 Arama sorgusu uzunluk doğrulayıcısını yaz
    - `validate_search_query(text: str) -> None` fonksiyonu: 10–500 karakter geçerli; <10 → `ValidationError`
    - Doğrulama: 9 karakter → hata; 10 karakter → geçer; 500 karakter → geçer; 501 karakter → hata
    - _Gereksinimler: 8.1, 8.7_

  - [ ]* 7.6 Özellik 19 için property testi yaz — Arama sonuçları sıralama ve sayı sınırı
    - **Özellik 19: Arama Sonuçları Sıralama ve Sayı Sınırı**
    - `st.text(min_size=0, max_size=600)` stratejisiyle: 10–500 arası sorgu → sonuçlar azalan sırada ve ≤10; <10 karakter → `ValidationError`
    - Doğrulama: `pytest tests/integration/test_search.py::test_search_ordering_and_limit` geçmeli
    - **Doğrular: Gereksinim 8.1, 8.2, 8.7**

  - [x] 7.7 Lessons Learned kelime sayısı doğrulayıcısını yaz
    - `validate_lessons_learned(text: str) -> None` fonksiyonu: 100–500 kelime geçerli; dışarısı `ValidationError` fırlatır
    - Doğrulama: 99 kelime → hata; 100 kelime → geçer; 500 kelime → geçer; 501 kelime → hata
    - _Gereksinimler: 7.1, 7.3_

  - [ ]* 7.8 Özellik 17 için property testi yaz — Lessons Learned kelime sayısı doğrulaması
    - **Özellik 17: Lessons Learned Kelime Sayısı Doğrulaması**
    - `st.text()` stratejisiyle: 100–500 kelime → kabul; dışarısı → reddedilir
    - Doğrulama: `pytest tests/unit/test_lessons.py::test_lessons_word_count` geçmeli
    - **Doğrular: Gereksinim 7.1, 7.3**

  - [~] 7.9 Ishikawa kategori yanıtı doğrulayıcısını yaz
    - `validate_ishikawa_cause(text: str) -> None` fonksiyonu: 1–500 karakter geçerli; boş veya >500 → `ValidationError`
    - Doğrulama: boş string → hata; 1 karakter → geçer; 500 karakter → geçer; 501 karakter → hata
    - _Gereksinimler: 3.2_

  - [ ]* 7.10 Özellik 8 için property testi yaz — Ishikawa kategori yanıtı doğrulaması
    - **Özellik 8: Ishikawa Kategori Yanıtı Doğrulaması**
    - `st.text(min_size=0, max_size=600)` stratejisiyle: 1–500 karakter → kabul; boş veya >500 → reddedilir
    - Doğrulama: `pytest tests/unit/test_ishikawa.py::test_ishikawa_category_validation` geçmeli
    - **Doğrular: Gereksinim 3.2**

- [~] 8. Kontrol noktası — Doğrulama katmanı
  - `pytest tests/unit/test_validation.py tests/unit/test_lessons.py tests/unit/test_ishikawa.py -v` geçmeli
  - Soru varsa kullanıcıya sor.


- [ ] 9. Metodoloji motorunu uygula
  - [~] 9.1 `MethodologyEngine` sınıfını yaz
    - `get_template`, `get_step`, `validate_response`, `is_complete` metodlarını uygula
    - Ishikawa, 8D, 5 Why, PDCA şablonlarını tanımla
    - Doğrulama: Her metodoloji için `get_template` doğru adım sayısını döndürmeli; `is_complete` tüm adımlar dolu olduğunda `True` döndürmeli
    - _Gereksinimler: 1.2, 2.1, 2.4_

  - [~] 9.2 Takip sorusu sınırı mantığını uygula
    - `SessionService.submit_step_response` içinde: bir adım başına en fazla 3 takip sorusu; 3. soru üretildikten sonra kullanıcı ilerleyebilir
    - Doğrulama: 3 takip sorusu üretildikten sonra `can_proceed = True` olmalı; 4. takip sorusu üretilmemeli
    - _Gereksinimler: 2.3_

  - [ ]* 9.3 Özellik 5 için property testi yaz — Takip sorusu sayısı sınırı
    - **Özellik 5: Takip Sorusu Sayısı Sınırı**
    - `st.integers(min_value=1, max_value=5)` stratejisiyle: herhangi bir adım için takip sorusu sayısı hiçbir zaman 3'ü aşmamalı
    - Doğrulama: `pytest tests/unit/test_chatbot.py::test_followup_question_limit` geçmeli
    - **Doğrular: Gereksinim 2.3**

  - [~] 9.4 Adım geri alma mantığını uygula
    - `SessionService.go_back_step` metodunu uygula: önceki adımın kayıtlı yanıtını ve soru metnini geri yükler; ilk adımda hata döndürür
    - Doğrulama: Adım 2'de geri dön → adım 1'in orijinal yanıtı ve sorusu geri yüklenmeli; adım 1'de geri dön → hata mesajı
    - _Gereksinimler: 2.5_

  - [ ]* 9.5 Özellik 6 için property testi yaz — Adım geri alma round-trip
    - **Özellik 6: Adım Geri Alma Round-Trip**
    - `st.lists(st.text(min_size=10))` stratejisiyle: geri dönülen adımın yanıt ve prompt metni orijinal kaydedilen değerlerle birebir eşleşmeli
    - Doğrulama: `pytest tests/unit/test_session.py::test_step_back_roundtrip` geçmeli
    - **Doğrular: Gereksinim 2.5**

  - [~] 9.6 8D tamamlanma zorunluluğunu uygula
    - `SessionService.finalize_session` içinde: 8D oturumunda 8 disiplinin tamamı ≥10 karakter yanıt içermeden finalize edilemez; eksik disiplinler hata mesajında listelenir
    - Doğrulama: D1–D7 dolu, D8 boş → hata mesajında "D8" geçmeli; tümü dolu → finalize başarılı
    - _Gereksinimler: 2.6, 5.5_

  - [ ]* 9.7 Özellik 7 için property testi yaz — 8D tamamlanma zorunluluğu
    - **Özellik 7: 8D Tamamlanma Zorunluluğu**
    - `st.sets(st.integers(min_value=1, max_value=8))` stratejisiyle: eksik disiplinler varken finalize → hata; tümü dolu → başarı
    - Doğrulama: `pytest tests/unit/test_8d.py::test_8d_completion_requirement` geçmeli
    - **Doğrular: Gereksinim 2.6, 5.5**

- [ ] 10. Ishikawa analizi özelliklerini uygula
  - [~] 10.1 Ishikawa oturum akışını uygula
    - 6 kategoriyi sırasıyla sun: Man, Machine, Method, Material, Measurement, Environment
    - Her kategori için 1–500 karakter doğrulaması; boş yanıt → aynı kategori yeniden sunulur
    - Doğrulama: Kategori sırası doğru; boş yanıt → hata ve aynı soru; 501 karakter → hata
    - _Gereksinimler: 3.1, 3.2_

  - [~] 10.2 Ishikawa veri nesnesini oturum kaydına kaydet
    - 6 kategori tamamlandığında `IshikawaData` nesnesini `step_responses` alanına yaz
    - Doğrulama: Kaydedilen nesne geri okunduğunda 6 kategori ve ilişkili nedenler listesi orijinal verilerle eşleşmeli
    - _Gereksinimler: 3.4_

  - [ ]* 10.3 Özellik 9 için property testi yaz — Ishikawa veri depolama round-trip
    - **Özellik 9: Ishikawa Veri Depolama Round-Trip**
    - `st.fixed_dictionaries(...)` stratejisiyle: kaydedilen `IshikawaData` geri okunduğunda orijinal verilerle birebir eşleşmeli
    - Doğrulama: `pytest tests/unit/test_ishikawa.py::test_ishikawa_storage_roundtrip` geçmeli
    - **Doğrular: Gereksinim 3.4**

  - [~] 10.4 Ishikawa kategori yeniden atama önerisini uygula
    - LLM bir nedenin farklı kategoriye uygun olduğunu tespit ettiğinde tam olarak bir alternatif kategori önerisi sun; kullanıcı orijinali onaylayabilir veya öneriyi kabul edebilir
    - Doğrulama: LLM yanıtı mock ile test et; öneri mesajı tam olarak bir alternatif kategori içermeli
    - _Gereksinimler: 3.6_

- [ ] 11. 5 Why analizi özelliklerini uygula
  - [~] 11.1 5 Why oturum akışını uygula
    - İlk soru: "Bu problem neden oluşuyor?"; her yanıt sonrası LLM ile bağlamsal sonraki soru üret (3 saniye timeout)
    - Minimum 3, maksimum 7 soru; 3. yanıt sonrası manuel ilerleme seçeneği; 7. yanıt sonrası otomatik kök neden onayına geç
    - Doğrulama: 2 yanıt sonrası ilerleme → engellenmeli; 3 yanıt sonrası → izin verilmeli; 7. yanıt → otomatik geçiş
    - _Gereksinimler: 4.1, 4.2, 4.3_

  - [ ]* 11.2 Özellik 10 için property testi yaz — 5 Why soru sayısı sınırları
    - **Özellik 10: 5 Why Soru Sayısı Sınırları**
    - `st.integers(min_value=1, max_value=10)` stratejisiyle: soru sayısı 3–7 arasında; <3 → ilerleme engellenir; 7. yanıt → otomatik geçiş
    - Doğrulama: `pytest tests/unit/test_5why.py::test_5why_question_count_limits` geçmeli
    - **Doğrular: Gereksinim 4.3**

  - [~] 11.3 Döngüsel mantık tespitini uygula
    - `detect_circular_logic(current_answer: str, previous_answers: list[str]) -> bool` fonksiyonu: mevcut yanıt ile önceki yanıtlardan herhangi biri arasında %70+ kelime örtüşmesi → `True`
    - Doğrulama: Aynı cümle → `True`; tamamen farklı cümle → `False`; %69 örtüşme → `False`; %70 örtüşme → `True`
    - _Gereksinimler: 4.5_

  - [ ]* 11.4 Özellik 11 için property testi yaz — 5 Why döngüsel mantık tespiti
    - **Özellik 11: 5 Why Döngüsel Mantık Tespiti**
    - `st.lists(st.text(), min_size=2)` stratejisiyle: %70+ kelime örtüşmesi → uyarı ve yanıt reddedilir
    - Doğrulama: `pytest tests/unit/test_5why.py::test_circular_logic_detection` geçmeli
    - **Doğrular: Gereksinim 4.5**

  - [~] 11.5 5 Why zincirini oturum kaydına kaydet
    - Kök neden onaylandığında `WhyChain` nesnesini (sorular, yanıtlar, onaylanan kök neden) `step_responses` alanına yaz
    - Doğrulama: Kaydedilen zincir geri okunduğunda sorular, yanıtlar ve kök neden orijinal verilerle eşleşmeli
    - _Gereksinimler: 4.6_

  - [ ]* 11.6 Özellik 12 için property testi yaz — 5 Why zinciri depolama round-trip
    - **Özellik 12: 5 Why Zinciri Depolama Round-Trip**
    - `st.lists(st.tuples(st.text(), st.text()))` stratejisiyle: kaydedilen `WhyChain` geri okunduğunda orijinal verilerle birebir eşleşmeli
    - Doğrulama: `pytest tests/unit/test_5why.py::test_5why_chain_roundtrip` geçmeli
    - **Doğrular: Gereksinim 4.6**

- [ ] 12. 8D raporu özelliklerini uygula
  - [~] 12.1 8D raporu JSON üretimini uygula
    - Oturum tamamlandığında 8 disiplini ve yanıtlarını içeren `EightDReport` nesnesini JSON formatında üret ve `Problem_Record`'a ekle
    - Rapor üretimi başarısız olursa kısmi rapor eklenmez; kullanıcıya hata döndürülür
    - Doğrulama: Tüm 8 disiplin dolu → JSON raporu üretilir ve şemaya uygun; üretim hatası → `Problem_Record`'da rapor alanı boş
    - _Gereksinimler: 5.4_

  - [ ]* 12.2 Özellik 13 için property testi yaz — 8D raporu JSON şema uygunluğu
    - **Özellik 13: 8D Raporu JSON Şema Uygunluğu**
    - `st.fixed_dictionaries(...)` stratejisiyle: üretilen her 8D JSON raporu şemaya uygun ve 8 disiplinin tamamını içermeli
    - Doğrulama: `pytest tests/unit/test_8d.py::test_8d_report_schema_compliance` geçmeli
    - **Doğrular: Gereksinim 5.4**

- [~] 13. Kontrol noktası — Metodoloji katmanı
  - `pytest tests/unit/test_session.py tests/unit/test_8d.py tests/unit/test_5why.py tests/unit/test_ishikawa.py -v` geçmeli
  - Soru varsa kullanıcıya sor.


- [ ] 14. LLM servisini uygula
  - [~] 14.1 `LLMService` sınıfını yaz
    - `generate_clarification`, `generate_next_why`, `generate_lessons_learned`, `generate_ishikawa_summary`, `suggest_category_reassignment` metodlarını uygula
    - Her metod için timeout ve fallback stratejisi: takip sorusu → statik fallback; Lessons Learned → 15 saniye timeout sonrası şablon; 5 Why sorusu → 3 saniye timeout sonrası hata + yeniden deneme
    - Doğrulama: LLM mock ile test et; timeout senaryosunda fallback devreye girmeli; fallback ilerlemeyi engellememeli
    - _Gereksinimler: 2.8, 4.2, 7.5_

  - [~] 14.2 Lessons Learned yapısal bileşen kontrolünü uygula
    - LLM çıktısında kök neden, düzeltici eylemler, sonuç ve en az bir önleyici öneri yoksa eksik bileşenler için yapılandırılmış placeholder ekle
    - Doğrulama: 4 bileşen tam → placeholder eklenmez; 1 bileşen eksik → o bileşen için placeholder eklenir
    - _Gereksinimler: 7.4_

  - [ ]* 14.3 Özellik 18 için property testi yaz — Lessons Learned yapısal bileşen kontrolü
    - **Özellik 18: Lessons Learned Yapısal Bileşen Kontrolü**
    - `st.builds(LessonsLearned, ...)` stratejisiyle: kök neden, düzeltici eylemler, sonuç ve önleyici öneri bileşenlerinin tamamı mevcut olmalı; eksik bileşenler için placeholder eklenmeli
    - Doğrulama: `pytest tests/unit/test_lessons.py::test_lessons_structural_components` geçmeli
    - **Doğrular: Gereksinim 7.4**

- [x] 15. Embedding ve Qdrant altyapısını uygula
  - [x] 15.1 `EmbeddingService` sınıfını yaz
    - `generate_embedding` ve `generate_batch_embeddings` metodlarını uygula (Gemini `text-embedding-004`, 768 boyut)
    - Doğrulama: Geçerli metin → 768 boyutlu float listesi döner; Gemini API mock ile test et
    - _Gereksinimler: 6.2_

  - [x] 15.2 `QdrantRepository` sınıfını yaz
    - `index_record`, `search_similar`, `update_record`, `delete_record` metodlarını uygula
    - Koleksiyon: `problem_records`; vektör boyutu: 768; mesafe: Cosine; HNSW: m=16, ef_construct=100
    - Doğrulama: Kayıt ekle → arama ile geri bul; silinen kayıt → arama sonuçlarında görünmemeli
    - _Gereksinimler: 6.2, 8.1_

  - [x] 15.3 Embedding yeniden deneme kuyruğunu uygula (Celery)
    - `EMBEDDING_QUEUE` tablosuna ekle; Celery worker 30 saniye aralıklarla en fazla 3 kez yeniden dener; 3 başarısız denemeden sonra `embedding-failed` olarak işaretle ve Admin'e bildirim gönder
    - Doğrulama: 3 başarısız deneme sonrası kayıt durumu `embedding-failed` olmalı; 4. deneme yapılmamalı
    - _Gereksinimler: 6.4_

  - [ ]* 15.4 Özellik 15 için property testi yaz — Embedding yeniden deneme sınırı
    - **Özellik 15: Embedding Yeniden Deneme Sınırı**
    - `st.integers(min_value=1, max_value=5)` stratejisiyle: en fazla 3 yeniden deneme; tüm denemeler başarısız → `embedding-failed` durumu
    - Doğrulama: `pytest tests/integration/test_embedding.py::test_embedding_retry_limit` geçmeli
    - **Doğrular: Gereksinim 6.4**

- [x] 16. RAG motorunu uygula
  - [~] 16.1 `RAGEngine` sınıfını yaz
    - `search_similar`, `index_record`, `update_record`, `delete_record` metodlarını uygula
    - Arama sonuçları anlamsal benzerlik skoruna göre azalan sırada; en fazla 10 sonuç; 0.5 altı skor → sonuç döndürülmez
    - Doğrulama: 10 kayıt ekle → arama → sonuçlar azalan sırada; 11. sonuç döndürülmemeli; 0.5 altı skor → boş liste
    - _Gereksinimler: 8.1, 8.2, 8.6_

  - [x] 16.2 Arama filtresi mantığını uygula
    - Sektör, departman, metodoloji, tarih aralığı ve çözüm durumu filtrelerini Qdrant payload filtreleme ile uygula
    - Doğrulama: Filtre uygulandığında dönen tüm sonuçlar filtre kriterlerini karşılamalı; filtre dışı kayıt döndürülmemeli
    - _Gereksinimler: 8.5_

  - [ ]* 16.3 Özellik 3 için property testi yaz — RAG sonuç sayısı sınırı
    - **Özellik 3: RAG Sonuç Sayısı Sınırı**
    - `st.text(min_size=20, max_size=2000)` stratejisiyle: döndürülen benzer kayıt sayısı 0–5 arasında (oturum oluşturma için)
    - Doğrulama: `pytest tests/integration/test_rag.py::test_rag_result_count_limit` geçmeli
    - **Doğrular: Gereksinim 1.6**

  - [ ]* 16.4 Özellik 21 için property testi yaz — Arama filtresi tutarlılığı
    - **Özellik 21: Arama Filtresi Tutarlılığı**
    - `st.builds(SearchFilters, ...)` stratejisiyle: filtre kombinasyonu uygulandığında dönen tüm sonuçlar filtre kriterlerini karşılamalı
    - Doğrulama: `pytest tests/integration/test_search.py::test_search_filter_consistency` geçmeli
    - **Doğrular: Gereksinim 8.5**

  - [ ]* 16.5 Özellik 20 için property testi yaz — Arama sonucu alan bütünlüğü
    - **Özellik 20: Arama Sonucu Alan Bütünlüğü**
    - `st.builds(SearchResult, ...)` stratejisiyle: her sonuç problem başlığı, metodoloji, kök neden özeti, çözüm durumu ve tam sayı yüzde benzerlik skoru içermeli
    - Doğrulama: `pytest tests/integration/test_search.py::test_search_result_field_completeness` geçmeli
    - **Doğrular: Gereksinim 8.3**

- [x] 17. Redis önbellek ve rate limiting altyapısını uygula
  - [~] 17.1 `RedisRepository` sınıfını yaz
    - Arama sonuçları önbelleği (TTL: 300 saniye) ve rate limiting sayaçları (pencere: 60 saniye) için metodları uygula
    - Doğrulama: Aynı sorgu 300 saniye içinde tekrarlandığında önbellekten dönmeli; 301. saniyede yeni sorgu yapılmalı
    - _Gereksinimler: 12.3_

  - [~] 17.2 Rate limiting middleware'ini uygula
    - 60 saniyelik pencerede 100 istek aşıldığında HTTP 429 + `Retry-After` header döndür
    - Doğrulama: 100. istek → 200; 101. istek → 429 + `Retry-After` header mevcut
    - _Gereksinimler: 11.5_

  - [ ]* 17.3 Özellik 29 için property testi yaz — Arama sonucu önbellek tutarlılığı
    - **Özellik 29: Arama Sonucu Önbellek Tutarlılığı**
    - `st.text(min_size=10, max_size=500)` stratejisiyle: 300 saniye içinde aynı parametrelerle tekrarlanan sorgu önbellekten dönmeli ve p95 < 500ms
    - Doğrulama: `pytest tests/integration/test_cache.py::test_search_cache_consistency` geçmeli
    - **Doğrular: Gereksinim 12.3**

  - [ ]* 17.4 Özellik 28 için property testi yaz — Rate limiting sınırı
    - **Özellik 28: Rate Limiting Sınırı**
    - `st.integers(min_value=100, max_value=200)` stratejisiyle: 60 saniyede 100 isteği aşan istekler HTTP 429 + `Retry-After` ile reddedilmeli
    - Doğrulama: `pytest tests/integration/test_api.py::test_rate_limiting` geçmeli
    - **Doğrular: Gereksinim 11.5**

- [~] 18. Kontrol noktası — Servis katmanı
  - `pytest tests/integration/ -v` geçmeli
  - Soru varsa kullanıcıya sor.

- [x] 19. Oturum yönetimi servisini uygula
  - [~] 19.1 `SessionService` sınıfını yaz
    - `create_session`, `get_session`, `submit_step_response`, `go_back_step`, `finalize_session`, `get_session_history` metodlarını uygula
    - `create_session`: oturum oluşturulduğunda benzersiz UUID ata; RAG motoru ile benzer kayıtları sorgula (en fazla 5 sonuç)
    - `submit_step_response`: yanıtı 2 saniye içinde oturum kaydına yaz
    - Doğrulama: Oturum oluştur → UUID döner; aynı anda N oturum oluştur → tüm UUID'ler farklı; yanıt gönder → 2 saniye içinde kaydedilmeli
    - _Gereksinimler: 1.5, 1.6, 2.7_

  - [ ]* 19.2 Özellik 2 için property testi yaz — Oturum tanımlayıcısı benzersizliği
    - **Özellik 2: Oturum Tanımlayıcısı Benzersizliği**
    - `st.integers(min_value=2, max_value=50)` stratejisiyle: N eşzamanlı oturum oluşturma isteği → tüm UUID'ler birbirinden farklı
    - Doğrulama: `pytest tests/unit/test_session.py::test_session_id_uniqueness` geçmeli
    - **Doğrular: Gereksinim 1.5**

- [x] 20. Problem kaydı servisini uygula
  - [~] 20.1 `KnowledgeService` sınıfını yaz
    - `create_record`, `get_record`, `update_record`, `delete_record`, `list_records`, `search_records` metodlarını uygula
    - `create_record`: oturum finalize edildiğinde zorunlu alanların tamamını içeren kayıt oluştur; embedding kuyruğuna ekle
    - `update_record`: PostgreSQL güncelle + Qdrant embedding yeniden üret; Qdrant başarısız → PostgreSQL rollback
    - `delete_record`: PostgreSQL sil + Qdrant sil; Qdrant başarısız → PostgreSQL rollback
    - Doğrulama: Kayıt oluştur → 7 zorunlu alan mevcut; Qdrant hatası simüle et → PostgreSQL rollback gerçekleşmeli
    - _Gereksinimler: 6.1, 9.3, 9.4_

  - [ ]* 20.2 Özellik 14 için property testi yaz — Problem kaydı zorunlu alan bütünlüğü
    - **Özellik 14: Problem Kaydı Zorunlu Alan Bütünlüğü**
    - `st.builds(Session, ...)` stratejisiyle: finalize edilen her oturum için oluşturulan kayıt 7 zorunlu alanın tamamını içermeli
    - Doğrulama: `pytest tests/integration/test_records.py::test_record_required_field_completeness` geçmeli
    - **Doğrular: Gereksinim 6.1**

  - [ ]* 20.3 Özellik 24 için property testi yaz — Güncelleme atomikliği (rollback)
    - **Özellik 24: Güncelleme Atomikliği (Rollback)**
    - `st.builds(RecordUpdate, ...)` stratejisiyle: Qdrant embedding yeniden üretimi başarısız olduğunda PostgreSQL kaydı önceki durumuna geri alınmalı
    - Doğrulama: `pytest tests/integration/test_records.py::test_update_atomicity_rollback` geçmeli
    - **Doğrular: Gereksinim 9.3, 9.7**

  - [~] 20.4 Sayfalama mantığını uygula
    - Varsayılan sayfa boyutu: 20; maksimum: 100; 100'ü aşan istek → varsayılan 20 kullanılır; yanıtta toplam kayıt sayısı ve sayfa numarası
    - Doğrulama: Sayfa boyutu 150 → 20 kayıt döner; sayfa boyutu 50 → 50 kayıt döner; yanıtta `total` ve `page` alanları mevcut
    - _Gereksinimler: 9.1_

  - [ ]* 20.5 Özellik 22 için property testi yaz — Sayfalama boyutu sınırları
    - **Özellik 22: Sayfalama Boyutu Sınırları**
    - `st.integers(min_value=1, max_value=200)` stratejisiyle: döndürülen kayıt sayısı istenen sayfa boyutunu aşmamalı; 100'ü aşan istek → varsayılan 20
    - Doğrulama: `pytest tests/unit/test_pagination.py::test_pagination_size_limits` geçmeli
    - **Doğrular: Gereksinim 9.1**

- [x] 21. FastAPI router'larını uygula
  - [~] 21.1 `auth_router` endpoint'lerini yaz
    - `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout` endpoint'lerini uygula
    - Doğrulama: Geçerli kimlik bilgileri → JWT token döner; geçersiz → 401; token yenileme → yeni token döner
    - _Gereksinimler: 10.1, 10.3_

  - [~] 21.2 `session_router` endpoint'lerini yaz
    - `POST /api/v1/sessions`, `GET /api/v1/sessions/{id}`, `POST /api/v1/sessions/{id}/steps`, `POST /api/v1/sessions/{id}/back`, `POST /api/v1/sessions/{id}/finalize`, `GET /api/v1/sessions` endpoint'lerini uygula
    - Doğrulama: Oturum oluştur → 200 + session_id; geçersiz problem açıklaması → 422; yetkisiz → 401
    - _Gereksinimler: 1.1, 1.5, 2.1, 2.5, 6.1_

  - [~] 21.3 `knowledge_router` endpoint'lerini yaz
    - `GET /api/v1/knowledge/search`, `GET /api/v1/knowledge/records/{id}` endpoint'lerini uygula
    - Doğrulama: Geçerli sorgu → sonuçlar azalan sırada; <10 karakter sorgu → 422; kayıt ID → tam kayıt 2 saniye içinde
    - _Gereksinimler: 8.1, 8.3, 8.4_

  - [~] 21.4 `records_router` endpoint'lerini yaz
    - `GET /api/v1/records`, `GET /api/v1/records/{id}`, `PUT /api/v1/records/{id}`, `DELETE /api/v1/records/{id}` endpoint'lerini uygula
    - Doğrulama: Admin → güncelleme/silme başarılı; User → güncelleme/silme → 403; yetkisiz → 401
    - _Gereksinimler: 9.1, 9.2, 9.3, 9.4, 9.6_

  - [~] 21.5 `health_router` endpoint'lerini yaz
    - `GET /api/v1/health`, `GET /api/v1/ready`, `GET /api/v1/docs` endpoint'lerini uygula
    - `/health`: tüm bağımlı servisler erişilebilir → 200; değilse → 503
    - `/ready`: tüm bağımlı servisler erişilebilir → 200; değilse → 503
    - Doğrulama: Tüm servisler ayakta → /health 200; Qdrant kapalı → /health 503
    - _Gereksinimler: 11.6_

  - [~] 21.6 Global exception handler ve API yanıt zarfını uygula
    - Tüm yanıtlar `APIResponse[T]` zarfında: `status`, `data`, `error`; `data` ve `error`'dan tam olarak biri null
    - Global exception handler: stack trace yanıtta yer almaz; 500 döner
    - Hatalı JSON gövdesi → 422 + alan/sözdizimi hatası mesajı
    - Doğrulama: Başarılı yanıt → `data` dolu, `error` null; hata yanıtı → `data` null, `error` dolu; HTTP 503 → zarf zorunluluğu muaf
    - _Gereksinimler: 11.2, 11.4_

  - [ ]* 21.7 Özellik 27 için property testi yaz — API yanıt zarfı tutarlılığı
    - **Özellik 27: API Yanıt Zarfı Tutarlılığı**
    - `st.sampled_from(all_endpoints)` stratejisiyle: her yanıt `status`, `data`, `error` içermeli; `data` ve `error`'dan tam olarak biri null (HTTP 503 hariç)
    - Doğrulama: `pytest tests/integration/test_api.py::test_api_response_envelope_consistency` geçmeli
    - **Doğrular: Gereksinim 11.2**

- [~] 22. Kontrol noktası — API katmanı
  - `pytest tests/integration/test_api.py -v` geçmeli
  - Soru varsa kullanıcıya sor.

- [x] 23. Degraded mode ve hata stratejilerini uygula
  - [~] 23.1 Qdrant bağlantı başarısızlığı degraded mode'unu uygula
    - 10 saniye içinde 3 ardışık bağlantı hatası → degraded mode; anlamsal arama istekleri 503 döner; yeni oturumlar oluşturulabilir
    - Bağlantı yeniden sağlandığında otomatik normal moda geç
    - Doğrulama: 3 ardışık hata simüle et → /search → 503; /sessions POST → 200; bağlantı yeniden sağla → /search → 200
    - _Gereksinimler: 12.5_

  - [~] 23.2 Bilgi tabanı erişilemez olduğunda oturum oluşturma akışını uygula
    - Bilgi tabanı erişilemezse oturum oluşturmaya devam et; kullanıcıya uyarı göster (yalnızca gerçekten erişilemez olduğunda)
    - Doğrulama: Qdrant kapalı → oturum oluşturulur + uyarı mesajı döner; Qdrant açık → uyarı mesajı döndürülmez
    - _Gereksinimler: 1.7_


- [ ] 24. Performans ve loglama altyapisini uygula
  - [~] 24.1 Yapilandirilmis metrik loglama middleware'ini yaz
    - Docker ortaminda 60 saniyelik araliklarla bellek ve CPU kullanimini yapilandirilmis log ciktisina yaz
    - Docker kapandiginda loglama atomik olarak durur
    - Dogrulama: 60 saniye bekle log dosyasinda bellek ve CPU metrikleri mevcut; docker-compose down log kaydi durur
    - _Gereksinimler: 12.4_

  - [~] 24.2 OpenAPI 3.0 dokumantasyonunu yapilandir
    - /docs endpoint'i tum endpoint'leri, istek semalarini ve yanit semalarini aciklayan OpenAPI 3.0 belgesi dondurmeli
    - Dogrulama: GET /api/v1/docs 200 + gecerli OpenAPI 3.0 JSON; tum router'lar belgede mevcut
    - _Gereksinimler: 11.3_

- [ ] 25. Entegrasyon ve smoke testlerini yaz
  - [~] 25.1 Docker Compose baslatma smoke testini yaz
    - docker-compose up 120 saniye icinde /ready HTTP 200 dondurmeli
    - Dogrulama: pytest tests/smoke/test_docker_startup.py gecmeli
    - _Gereksinimler: 14.2_

  - [~] 25.2 Ortam degiskeni yapilandirma smoke testini yaz
    - Tum gerekli ortam degiskenleri .env.example'daki mevcut degilse uygulama baslamaz
    - Dogrulama: pytest tests/smoke/test_env_config.py gecmeli
    - _Gereksinimler: 14.3_

  - [ ]* 25.3 PostgreSQL + Qdrant atomik guncelleme entegrasyon testini yaz
    - Qdrant embedding yeniden uretimi basarisiz PostgreSQL rollback; kismi durum olusmamalı
    - Dogrulama: pytest tests/integration/test_records.py::test_atomic_update_rollback gecmeli
    - _Gereksinimler: 9.3, 9.7_

  - [ ]* 25.4 Celery embedding yeniden deneme kuyrugu entegrasyon testini yaz
    - Embedding basarisiz kuyrukta bekler 3 deneme embedding-failed
    - Dogrulama: pytest tests/integration/test_embedding.py::test_celery_retry_queue gecmeli
    - _Gereksinimler: 6.4_

- [~] 26. Son kontrol noktasi - Tum testler
  - pytest tests/ -v gecmeli
  - docker-compose up --build /ready 200 dondurmeli
  - Soru varsa kullaniciya sor.

---

## Notlar

- * ile isaretli alt gorevler istege baglidir; hizli MVP icin atlanabilir
- Her gorev tek bir sorumluluga sahiptir (SKILL.md: Single Responsibility)
- Her alt gorev somut ve dogrulanabilir bir basari kriteri icerir (SKILL.md: Goal-Driven Execution)
- Property testleri hypothesis kutuphanesi ile yazilir; her property icin minimum 100 iterasyon
- Spekulatif veya gelecekte lazim olabilir gorevler eklenmemistir (SKILL.md: Simplicity First)
- Her degisen satir dogrudan bir gereksinime izlenebilir (SKILL.md: Surgical Changes)


## Gorev Bagimlilik Grafigi

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["2.1", "4.1"]
    },
    {
      "id": 1,
      "tasks": ["2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "4.2"]
    },
    {
      "id": 2,
      "tasks": ["4.3", "2.8", "5.1", "7.1", "7.3", "7.5", "7.7", "7.9"]
    },
    {
      "id": 3,
      "tasks": ["5.2", "5.3", "7.2", "7.4", "7.6", "7.8", "7.10", "9.1"]
    },
    {
      "id": 4,
      "tasks": ["9.2", "9.4", "9.6", "10.1", "10.2", "11.1", "11.3", "11.5", "12.1", "14.1", "15.1", "15.2"]
    },
    {
      "id": 5,
      "tasks": ["9.3", "9.5", "9.7", "10.3", "10.4", "11.2", "11.4", "11.6", "12.2", "14.2", "14.3", "15.3", "15.4"]
    },
    {
      "id": 6,
      "tasks": ["16.1", "17.1", "17.2", "19.1", "20.1", "20.4"]
    },
    {
      "id": 7,
      "tasks": ["16.2", "16.3", "16.4", "16.5", "17.3", "17.4", "19.2", "20.2", "20.3", "20.5"]
    },
    {
      "id": 8,
      "tasks": ["21.1", "21.2", "21.3", "21.4", "21.5", "21.6", "23.1", "23.2", "24.1", "24.2"]
    },
    {
      "id": 9,
      "tasks": ["21.7", "25.1", "25.2", "25.3", "25.4"]
    }
  ]
}
```
