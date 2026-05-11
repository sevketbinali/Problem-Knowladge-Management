# Uygulama Günlüğü: Proje Kurulumu ve Gemini API Geçişi

## Görev Özeti
Projenin temel iskeletinin kurulması, Docker ortamının yapılandırılması ve OpenAI'dan Google Gemini API'ya (SDK v2) tam geçişin sağlanması.

## Yapılan İşlemler
- `docker-compose.yml` ve `Dockerfile` yapılandırılarak PostgreSQL, Qdrant ve Redis servisleri ayağa kaldırıldı.
- `pyproject.toml` içerisindeki `openai` bağımlılığı kaldırılarak yerine en güncel `google-genai` (v0.3.0+) SDK'sı eklendi.
- `.env` ve `.env.example` dosyaları temizlendi; sadece `GEMINI_API_KEY` odaklı yapılandırmaya geçildi.
- `src/core/config.py` güncellenerek tüm ortam değişkenlerinin tip güvenli bir şekilde yüklenmesi sağlandı.

## Başarı Kriterleri ve Sonuçlar
- **SDK Doğrulaması**: `google-genai` kütüphanesi Docker konteynerine başarıyla kuruldu.
- **Model Erişimi**: Yapılan testlerde `gemini-3-flash-preview` modelinin aktif olduğu ve API anahtarının yetkili olduğu doğrulandı.
- **Kod Temizliği**: Kod tabanında OpenAI'ya dair hiçbir referans kalmadı.

## Karşılaşılan Hatalar ve Çözümler
### 1. Hata: `404 Model Not Found`
- **Nedeni**: Eski `google-generativeai` SDK'sı ile `gemini-1.5-flash` modeline erişilmeye çalışılması.
- **Çözüm**: SDK en yeni `google-genai` sürümüne yükseltildi ve 2026 bağlamında güncel olan `gemini-3-flash-preview` modeline geçiş yapıldı.

### 2. Hata: `Permission Denied` (Pip Install)
- **Nedeni**: Docker içerisinde `pip install` komutunun kısıtlı yetkili kullanıcı ile çalıştırılması.
- **Çözüm**: Komut `docker exec -u root` (veya uygun yetki) ile çalıştırılarak `google-genai` ve `tenacity` paketlerinin kurulumu sağlandı.
