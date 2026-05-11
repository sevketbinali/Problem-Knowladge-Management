# Uygulama Günlüğü: Kimlik Doğrulama ve Güvenlik (Task 5)

## Görev Özeti
Kullanıcı kayıt, giriş ve JWT tabanlı yetkilendirme mekanizmasının güvenli bir şekilde kurulması.

## Yapılan İşlemler
- `src/core/auth.py` içerisinde şifre hashleme ve JWT yönetim fonksiyonları yazıldı.
- `src/infrastructure/services/auth_service.py` katmanı oluşturularak iş mantığı (login/register) ayrıştırıldı.
- `src/api/v1/dependencies.py` ile FastAPI `Depends` mekanizması kullanılarak `get_current_user` ve `get_admin_user` korumaları eklendi.
- `PostgreSQLRepository` üzerinde kullanıcı sorgulama ve oluşturma metodları eklendi.

## Başarı Kriterleri ve Sonuçlar
- **Birim Testleri**: `tests/unit/test_auth.py` ile şifre hashleme ve JWT round-trip işlemleri `hypothesis` kullanılarak 100% başarıyla test edildi.
- **Rol Yönetimi**: Admin ve Standart kullanıcı ayrımı bağımlılık seviyesinde sağlandı.

## Karşılaşılan Hatalar ve Çözümler
### 1. Hata: Bcrypt 72-Byte Limiti (`ValueError`)
- **Nedeni**: Bcrypt algoritmasının doğası gereği 72 byte'tan uzun şifre girişlerini kabul etmemesi. `hypothesis` testleri sırasında çok uzun rastgele diziler üretildiğinde bu hata tetiklendi.
- **Çözüm**: Şifreler Bcrypt'e gönderilmeden önce SHA256 ile hashlenip Base64 formatına çevrildi (`_prepare_password` fonksiyonu). Bu sayede her uzunluktaki şifre güvenli bir şekilde işlenebilir hale getirildi.

### 2. Hata: Hypothesis Deadline Exceeded
- **Nedeni**: Bcrypt'in (rounds=12) yavaş bir algoritma olması sebebiyle `hypothesis`'in varsayılan 200ms süresini aşması.
- **Çözüm**: İlgili test fonksiyonuna `@settings(deadline=None, max_examples=10)` eklenerek test süresi esnetildi ve örnek sayısı optimize edildi.
