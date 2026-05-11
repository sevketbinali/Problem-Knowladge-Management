# Uygulama Günlüğü: Arama Servisi (Task 21)

## Görev Özeti
Kayıtlı problem kayıtları üzerinde semantik ve filtrelenmiş arama yapılması, sonuçların önbelleğe alınması ve arama faaliyetlerinin denetlenmesi (Audit Logging).

## Yapılan İşlemler
- `src/infrastructure/services/search_service.py`: RAG motoru, Redis ve PostgreSQL repository'lerini birleştiren merkezi arama servisi yazıldı.
- **Önbellekleme (Caching)**: Aynı sorgu ve filtre kombinasyonları için Redis üzerinden 60 dakikalık hızlı erişim sağlandı.
- **Denetim İzleri (Audit Logs)**: Her arama işlemi (önbellekten gelsin ya da gelmesin) kullanıcı ID'si ve sorgu detaylarıyla birlikte `audit_logs` tablosuna kaydedildi.

## Başarı Kriterleri ve Sonuçlar
- **Hibrit Arama**: Hem metin benzerliği (Semantic) hem de metadata filtreleri (Departman, Sektör vb.) aynı anda kullanılabiliyor.
- **Hız**: Redis entegrasyonu sayesinde tekrarlanan sorgularda yanıt süresi milisaniyeler mertebesine indirildi.
- **İzlenebilirlik**: Kimin neyi, ne zaman aradığı veritabanı seviyesinde kayıt altına alındı.

## Karşılaşılan Hatalar ve Çözümler
### 1. Hata: Cache Key Çakışması
- **Nedeni**: Sadece sorgu metnine dayalı anahtar oluşturulmasının, farklı filtrelerle yapılan aramaların birbirinin üzerine yazmasına neden olması.
- **Çözüm**: Filtrelerin alfabetik olarak sıralanıp string'e dönüştürülmesi ve anahtarın bir parçası haline getirilmesi sağlandı (`f"search:{query}:{filter_str}"`).

### 2. Hata: Audit Log Entity ID
- **Nedeni**: Arama işlemi belirli bir kayda ait olmadığı için `entity_id` alanına ne yazılacağının belirsizliği.
- **Çözüm**: Arama işlemleri için sabit bir "Dummy UUID" (tümü sıfır) kullanılarak veritabanı tutarlılığı korundu.
