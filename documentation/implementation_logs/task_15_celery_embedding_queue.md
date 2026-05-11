# Uygulama Günlüğü: Celery ve Embedding Kuyruğu (Task 15.3)

## Görev Özeti
Arama ve analiz süreçlerinde kullanılan vektör (embedding) üretiminin, API performansını etkilememesi için arka plan görevlerine (Celery) aktarılması ve hata durumunda yeniden deneme mekanizmasının kurulması.

## Yapılan İşlemler
- `src/infrastructure/celery_app.py`: Celery uygulaması Redis broker ve backend kullanacak şekilde yapılandırıldı.
- `src/infrastructure/tasks.py`: `generate_embedding_task` görevi yazıldı. Bu görev, verilen metni vektöre çevirir ve asenkron olarak Qdrant veritabanına indeksler.
- **Retry Logic**: Görev üzerinde `@celery_app.task(bind=True, max_retries=3)` kullanılarak, API hatalarında (hız sınırı, network kesintisi vb.) 1 dakika arayla 3 kez otomatik yeniden deneme sağlandı.

## Başarı Kriterleri ve Sonuçlar
- **Performans**: Vektör üretimi artık HTTP isteği dışında yapıldığı için API yanıt süreleri iyileştirildi.
- **Güvenilirlik**: Qdrant veya Gemini API geçici olarak ulaşılamaz olduğunda, veriler kaybolmadan kuyrukta bekletilip tekrar denenebilir hale geldi.

## Karşılaşılan Hatalar ve Çözümler
### 1. Hata: Async Context inside Sync Task
- **Nedeni**: Celery görevlerinin varsayılan olarak senkron çalışması, ancak `EmbeddingService` ve `QdrantRepository` metodlarımızın `async` olması.
- **Çözüm**: Görev gövdesi içerisinde `asyncio.run()` kullanılarak asenkron metodların güvenli bir şekilde çalıştırılması sağlandı.

### 2. Hata: Task Serialization
- **Nedeni**: UUID nesnelerinin JSON formatında serileştirilememesi.
- **Çözüm**: Görev parametreleri olarak `uuid.UUID` yerine `str(uuid)` kullanıldı ve görev içerisinde tekrar UUID nesnesine dönüştürüldü.
