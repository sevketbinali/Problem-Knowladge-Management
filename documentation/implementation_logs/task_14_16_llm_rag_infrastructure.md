# Uygulama Günlüğü: LLM ve Vektör Veritabanı Altyapısı (Task 14, 15, 16)

## Görev Özeti
Google Gemini API kullanılarak metin üretimi ve vektör (embedding) oluşturma süreçlerinin kurulması, Qdrant ile semantik arama altyapısının hazırlanması.

## Yapılan İşlemler
- `src/infrastructure/services/llm_service.py`: Gemini modeline prompt gönderen ve takip soruları üreten servis yazıldı.
- `src/infrastructure/services/embedding_service.py`: `text-embedding-004` modelini kullanarak 768 boyutlu vektörler üreten servis yazıldı.
- `src/infrastructure/repositories/qdrant_repository.py`: Qdrant asenkron istemcisi ile koleksiyon yönetimi ve "Semantic Similarity Search" metodları eklendi.
- `src/domain/rag_engine.py`: Vektör üretimi ve Qdrant indekslemesini birleştiren orkestrasyon katmanı kuruldu.

## Başarı Kriterleri ve Sonuçlar
- **Semantik Arama**: 0.5 benzerlik eşiği ve Cosine Distance kullanılarak en alakalı 10 sonucu getiren yapı kuruldu.
- **Hata Toleransı**: LLM veya Embedding servislerinde oluşabilecek hatalar için boş sonuç/varsayılan metin dönen fallback stratejileri uygulandı.

## Karşılaşılan Hatalar ve Çözümler
### 1. Hata: Qdrant Koleksiyon Bulunamadı
- **Nedeni**: Servis ilk ayağa kalktığında `problem_records` koleksiyonunun manuel olarak oluşturulmamış olması.
- **Çözüm**: `QdrantRepository` içerisine `ensure_collection` metodu eklendi. Bu metod, koleksiyon yoksa 768 boyutlu ve Cosine mesafeli olarak otomatik oluşturuyor.

### 2. Hata: Senkron SDK vs Asenkron FastAPI
- **Nedeni**: `google-genai` kütüphanesinin bazı metodlarının bloklayıcı (synchronous) olması.
- **Çözüm**: API çağrıları `asyncio.to_thread` içerisine alınarak FastAPI'nin asenkron event loop'unun bloklanması engellendi.
