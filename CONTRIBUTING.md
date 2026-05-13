# PKM Katkıda Bulunma Rehberi

Problem Knowledge Management (PKM) projesine katkıda bulunmak istediğiniz için teşekkürler! Bu döküman, geliştirme sürecine nasıl dahil olabileceğinizi açıklar.

## 🛠️ Geliştirme Ortamı Kurulumu

Proje, tam izole bir geliştirme ortamı için Docker kullanır.

1. **Repoyu Forklayın ve Klonlayın:**
   ```bash
   git clone https://github.com/sevketbinali/Problem-Knowladge-Management.git
   ```

2. **Bağımlılıkları İnceleyin:**
   - **Backend:** FastAPI (Python 3.11+)
   - **Frontend:** Next.js (TypeScript)
   - **Veritabanları:** Postgres, Qdrant, Redis

3. **Çalıştırma:**
   ```bash
   docker-compose up --build
   ```

## 📜 Kod Standartları

- **Python:** PEP 8 standartlarına uygun kod yazılmalıdır.
- **TypeScript/React:** Temiz bileşen mimarisi ve `globals.css` içindeki tema değişkenleri (`var(--color-...)`) kullanılmalıdır.
- **Dökümantasyon:** Yeni bir endpoint eklendiğinde `API_DOCUMENTATION.md` güncellenmelidir.

## 🌿 Branch Yapısı

- `main`: Kararlı sürüm.
- `develop`: Geliştirme yapılan ana dal.
- `feature/...`: Yeni özellikler için kullanılan dallar.

## 🚀 Pull Request Süreci

1. Yeni bir branch oluşturun.
2. Değişikliklerinizi yapın ve test edin.
3. Değişikliklerinizi açıklayan net bir PR açın.
4. Kod incelemesinden sonra `develop` dalına merge edilecektir.

---
<sub>Sistem hakkında sorularınız için [sevketbinali@gmail.com](mailto:sevketbinali@gmail.com) adresine ulaşabilirsiniz.</sub>
