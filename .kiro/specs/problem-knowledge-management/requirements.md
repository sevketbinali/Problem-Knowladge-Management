# Gereksinimler Dokümanı

## Giriş

Bu doküman, üretim, otomotiv ve lojistik gibi endüstriyel sektörlerde karşılaşılan sorunların sistematik biçimde çözülmesini ve kurumsal hafızaya aktarılmasını sağlayan **AI destekli Problem Bilgi Yönetim Sistemi**'nin gereksinimlerini tanımlar.

Sistem; Ishikawa, 8D, 5 Why gibi profesyonel problem çözme metodolojilerini chatbot arayüzü üzerinden adım adım rehberlik ederek uygular. Çözüm sürecinin sonunda elde edilen "lessons learned" kayıtları, RAG (Retrieval-Augmented Generation) mimarisi ile şirketin bilgi havuzuna işlenir. Böylece gelecekte benzer sorunlar yaşandığında geçmiş deneyimlere anında erişim sağlanır.

Sistem, FastAPI & Python backend, Docker ortamı ve vektör tabanlı bilgi tabanı üzerine inşa edilecektir.

---

## Sözlük

- **System**: Problem Bilgi Yönetim Sistemi'nin tamamı.
- **Chatbot**: Kullanıcıyla doğal dil üzerinden etkileşim kuran, problem çözme sürecini yönlendiren yapay zeka ajanı.
- **Problem_Record**: Bir sorunun tanımını, kök neden analizini, uygulanan çözümü ve öğrenilen dersleri içeren yapılandırılmış kayıt.
- **Methodology**: Ishikawa, 8D, 5 Why, Balık Kılçığı gibi sistematik problem çözme yöntemlerinden biri.
- **Session**: Kullanıcının bir problem için başlattığı, tamamlanana veya iptal edilene kadar devam eden etkileşim oturumu.
- **Knowledge_Base**: Geçmiş Problem_Record'larının vektör gömülü biçimde saklandığı RAG deposu.
- **RAG_Engine**: Kullanıcı sorgularına karşılık Knowledge_Base üzerinde anlamsal arama yaparak ilgili geçmiş kayıtları getiren bileşen.
- **LLM**: Chatbot'un doğal dil anlama ve üretme kapasitesini sağlayan büyük dil modeli.
- **Embedding_Service**: Metin içeriklerini vektör temsillerine dönüştüren servis.
- **Vector_Store**: Vektör gömülü Problem_Record'larının saklandığı ve anlamsal sorgu ile erişilen veritabanı.
- **Template**: Belirli bir Methodology'ye ait, adım adım doldurulacak yapılandırılmış form şablonu.
- **Lessons_Learned**: Problem çözüm sürecinin sonunda elde edilen, gelecekte benzer sorunların önlenmesine yönelik çıkarımlar.
- **User**: Sistemi kullanan mühendis, teknisyen veya yönetici.
- **Admin**: Sistem yapılandırmasını ve kullanıcı yönetimini gerçekleştiren yetkili kişi.
- **API**: FastAPI tabanlı HTTP arayüzü.
- **Docker_Environment**: Sistemin çalıştığı konteyner tabanlı dağıtım ortamı.

---

## Gereksinimler

### Gereksinim 1: Problem Çözme Oturumu Başlatma

**Kullanıcı Hikayesi:** Bir Kullanıcı olarak, problemimi tanımlayarak yeni bir problem çözme oturumu başlatmak istiyorum; böylece Chatbot beni uygun metodoloji üzerinden yönlendirebilsin.

#### Kabul Kriterleri

1. WHEN bir Kullanıcı 20 ile 2000 karakter arasında bir problem açıklaması gönderdiğinde, THE Chatbot SHALL problem açıklamasının alındığını onaylayan bir mesaj göstermeli ve 3 saniye içinde mevcut Metodoloji seçeneklerinin listesini sunmalıdır.
2. WHEN bir Kullanıcı sunulan listeden bir Metodoloji seçtiğinde, THE Chatbot SHALL ilgili Şablonu yüklemeli ve 2 saniye içinde ilk adımı Kullanıcıya göstermelidir.
3. IF bir Kullanıcı 20 karakterden kısa bir problem açıklaması gönderirse, THEN THE System SHALL açıklamanın en az 20 karakter uzunluğunda olması gerektiğini belirten bir doğrulama hata mesajı döndürmeli ve Oturum oluşturmadan işlemi sonlandırmalıdır.
4. IF bir Kullanıcı 2000 karakteri aşan bir problem açıklaması gönderirse, THEN THE System SHALL izin verilen maksimum uzunluğu belirten bir doğrulama hata mesajı döndürmeli ve Oturum oluşturmadan işlemi sonlandırmalıdır.
5. THE System SHALL her yeni problem çözme oturumuna oluşturulma anında benzersiz bir Oturum tanımlayıcısı atamalı ve bunu Kullanıcıya dönen yanıta dahil etmelidir.
6. WHEN bir Oturum oluşturulduğunda ve Bilgi_Tabanı erişilebilir olduğunda, THE RAG_Engine SHALL Bilgi_Tabanı'nı anlamsal olarak benzer geçmiş Problem_Kayıtları için sorgulamalı ve rehberli adımlar başlamadan önce Kullanıcıya en fazla 5 ilgili sonuç sunmalıdır.
7. IF Oturum oluşturma sırasında Bilgi_Tabanı erişilemez durumdaysa, THEN THE System SHALL Oturum oluşturmaya devam etmeli ve Kullanıcıya benzer problem önerilerinin geçici olarak kullanılamadığını bildiren bir uyarı göstermelidir; bu uyarı YALNIZCA Bilgi_Tabanı gerçekten erişilemez olduğunda gösterilmelidir.
8. IF Sistemde hiçbir Metodoloji seçeneği mevcut değilse, THEN THE System SHALL hiçbir metodolojinin yapılandırılmadığını belirten bir hata mesajı döndürmeli ve Oturum oluşturmayı engellemelidir.

---

### Gereksinim 2: Adım Adım Metodoloji Rehberliği

**Kullanıcı Hikayesi:** Bir Kullanıcı olarak, Chatbot'un beni seçilen metodoloji üzerinden adım adım yönlendirmesini istiyorum; böylece yapılandırılmış ve eksiksiz bir kök neden analizi gerçekleştirebileyim.

#### Kabul Kriterleri

1. WHILE bir Oturum aktif olduğunda, THE Chatbot SHALL bir seferde yalnızca bir metodoloji adımı sunmalı ve bir sonraki adıma geçmeden önce Kullanıcının girdisini beklemelidir.
2. WHEN bir Kullanıcı boş olmayan ve en az 10 karakter içeren bir adım yanıtı sağladığında, THE Chatbot SHALL yalnızca 10 karakterlik uzunluk gereksinimini esas alarak ek geçerlilik kriteri uygulamadan otomatik olarak bir sonraki adıma geçmelidir.
3. IF bir Kullanıcı bir adıma belirsiz veya eksik bir yanıt sağlarsa, THEN THE Chatbot SHALL 5 saniye içinde LLM kullanarak açıklayıcı bir takip sorusu üretmeli; bir adım başına en fazla 3 takip sorusu sorulabilir; WHEN 3 takip sorusu sınırına ulaşıldığında, THE Chatbot SHALL o adım için daha fazla açıklayıcı soru üretmeyi durdurmalı ve Kullanıcının ilerlemesine izin vermelidir.
4. THE Chatbot SHALL şu Metodoloji türlerini desteklemelidir: Ishikawa (Balık Kılçığı), 8D (Sekiz Disiplin), 5 Why (5 Neden) ve PDCA.
5. WHEN bir Kullanıcı önceki bir adıma geri dönmek istediğinde, THE Chatbot SHALL o adımın kayıtlı yanıtını ve soru metnini geri yüklemeli ve Kullanıcının yanıtı revize etmesine izin vermelidir; IF Kullanıcı zaten ilk adımdaysa, THE System SHALL Kullanıcıya önceki bir adımın bulunmadığını bildirmelidir.
6. WHERE seçilen Metodoloji 8D ise, THE Chatbot SHALL Oturumun sonlandırılmasına izin vermeden önce 8 disiplinin tamamının en az 10 karakter yanıt içermesini zorunlu kılmalıdır; WHEN 8 disiplinin tamamı uzunluk gereksinimini karşıladığında, THE System SHALL ek bir tamamlanma kontrolü gerektirmeden otomatik olarak sonlandırmaya izin vermelidir.
7. WHEN bir Kullanıcı herhangi bir adıma yanıt gönderdiğinde, THE System SHALL bağlantı kesilse dahi veri kaybı yaşanmaması için bu yanıtı 2 saniye içinde Oturum kaydına kalıcı olarak yazmalıdır.
8. IF açıklayıcı bir takip sorusu gerektiğinde LLM erişilemez durumdaysa, THEN THE System SHALL Kullanıcıdan daha fazla ayrıntı sağlamasını isteyen statik bir yedek mesaj göstermeli ve ilerlemeyi engellememelidir.

---

### Gereksinim 3: Ishikawa (Balık Kılçığı) Analizi

**Kullanıcı Hikayesi:** Bir Kullanıcı olarak, yapay zeka desteğiyle Ishikawa analizi gerçekleştirmek istiyorum; böylece standart neden kategorileri genelinde tüm olası kök nedenleri sistematik biçimde belirleyebileyim.

#### Kabul Kriterleri

1. WHEN bir Kullanıcı Ishikawa Metodolojisini seçtiğinde, THE Chatbot SHALL altı standart neden kategorisini sırasıyla sunmalıdır: İnsan (Man), Makine (Machine), Yöntem (Method), Malzeme (Material), Ölçüm (Measurement) ve Çevre (Environment).
2. WHILE Kullanıcı bir Ishikawa Oturumunu tamamlarken, THE Chatbot SHALL bir sonraki kategoriye geçmeden önce Kullanıcıdan her kategori için 1 ile 500 karakter arasında en az bir neden girmesini istemelidir; IF Kullanıcı boş veya yalnızca boşluk içeren bir yanıt gönderirse, THE System SHALL bir doğrulama hatası döndürmeli ve aynı kategori sorusunu yeniden sunmalıdır; IF Kullanıcı 500 karakteri aşan bir neden girerse, THE System SHALL Kullanıcının girişi düzenlemesine izin vermeli ve doğrulamayı yalnızca Kullanıcı girişini onayladığında gerçekleştirmelidir.
3. WHEN altı kategorinin tamamı tamamlandığında, THE LLM SHALL kategoriler genelinde en sık bahsedilen 5 kök nedeni sıralayan bir özet oluşturmalı ve Kullanıcıya sunmalıdır.
4. WHEN altı kategorinin tamamı tamamlandığında, THE System SHALL her kategori adını ve ilişkili nedenler listesini içeren yapılandırılmış bir Ishikawa veri nesnesini Oturum kaydına kaydetmelidir.
5. IF kök neden özeti istendiğinde LLM erişilemez durumdaysa, THEN THE System SHALL Kullanıcıya bir hata mesajı göstermeli ve özet oluşturmadan — doğrulamayı geçemeyen yanıtlar dahil — tüm kategori yanıtlarını Oturum kaydında korumalıdır.
6. WHEN LLM, Kullanıcı tarafından girilen bir nedenin farklı bir kategoriye daha uygun olduğunu tespit ettiğinde, THE Chatbot SHALL tam olarak bir alternatif kategori önerisi sunmalı ve Kullanıcıdan orijinal kategoriyi onaylamasını ya da önerilen kategoriyi kabul etmesini istemelidir.

---

### Gereksinim 4: 5 Why (5 Neden) Analizi

**Kullanıcı Hikayesi:** Bir Kullanıcı olarak, 5 Why analizini etkileşimli biçimde gerçekleştirmek istiyorum; böylece yinelemeli sorgulama yoluyla bir problemin kök nedenine ulaşabileyim.

#### Kabul Kriterleri

1. WHEN bir Kullanıcı 5 Why Metodolojisini seçtiğinde, THE Chatbot SHALL problem ifadesini göstermeli ve ilk soru olarak "Bu problem neden oluşuyor?" sorusunu sunmalıdır.
2. WHEN bir Kullanıcı bir "Neden" sorusuna yanıt verdiğinde, THE Chatbot SHALL LLM kullanarak Kullanıcının önceki yanıtına dayalı bağlamsal olarak ilgili bir sonraki "Neden" sorusunu 3 saniye içinde üretmelidir; IF LLM çağrısı denenmiş ve 3 saniye içinde yanıt vermemişse, THE System SHALL bir hata mesajı göstermeli ve zaman aşımının ne zaman gerçekleştiğinden bağımsız olarak Kullanıcının yeniden denemesine izin vermelidir; IF zaman aşımı gerçekleştiğinde LLM henüz çağrılmamışsa, THE System SHALL yeniden deneme seçeneği sunmamalıdır.
3. THE System SHALL Oturum başına en az 3, en fazla 7 yinelemeli "Neden" sorusunu desteklemelidir; WHEN Kullanıcı en az 3 soruyu yanıtladığında, THE System SHALL Kullanıcının açık bir tetikleyici gerektirmeden manuel olarak kök neden onayına geçmesine izin vermelidir; WHEN 7. yanıt gönderildiğinde, THE System SHALL LLM'in kök neden tespiti sinyali verip vermediğinden bağımsız olarak otomatik olarak kök neden onayına geçmelidir.
4. WHEN Kullanıcı onayladığında veya LLM kök nedenin tespit edildiğini bildirdiğinde, THE Chatbot SHALL her Neden sorusunu ve karşılık gelen yanıtını sırasıyla listeleyen bir özet göstermeli ve sonlandırmadan önce Kullanıcıdan tespit edilen kök nedeni onaylamasını istemelidir.
5. IF bir Kullanıcının "Neden" sorusuna verdiği yanıt, aynı zincirdeki önceki yanıtlardan herhangi biriyle %70'ten fazla kelime örtüşmesi paylaşıyorsa, THEN THE Chatbot SHALL döngüsel mantık uyarısı göstermeli ve yanıtı kabul etmeden önce Kullanıcıdan farklı bir bakış açısı sunmasını istemelidir.
6. WHEN Kullanıcı kök nedeni onayladığında, THE System SHALL tam Why zincirini ve onaylanan kök nedeni Oturum kaydına kaydetmelidir.

---

### Gereksinim 5: 8D Problem Çözme Süreci

**Kullanıcı Hikayesi:** Bir Kullanıcı olarak, yapılandırılmış rehberlik eşliğinde 8D problem çözme sürecini tamamlamak istiyorum; böylece kapsamlı bir düzeltici eylem raporu oluşturabileyim.

#### Kabul Kriterleri

1. WHEN bir Kullanıcı 8D Metodolojisini seçtiğinde, THE Chatbot SHALL sekiz disiplini sırasıyla sunmalıdır: D1 (Ekip Oluşturma), D2 (Problem Tanımı), D3 (Geçici Önlemler), D4 (Kök Neden Analizi), D5 (Düzeltici Eylemler), D6 (Uygulama), D7 (Önleme), D8 (Kapanış).
2. WHEN bir disiplin Kullanıcıya sunulduğunda, THE Chatbot SHALL disiplinin amacının açıklamasını ve en az iki yönlendirici soruyu göstermelidir; bir disiplin, Kullanıcının her yönlendirici soruya en az 1 karakter içeren boş olmayan bir yanıt verdiğinde tamamlanmış sayılır.
3. WHEN bir Kullanıcı D4'ü tamamladığında, THE LLM SHALL Bilgi_Tabanı'nı aynı problem kategorisindeki veya en az bir eşleşen anahtar kelimeyi paylaşan ve çözülmüş durumda olan Problem_Kayıtları için sorgulamalı ve Kullanıcıya en fazla 5 eşleşen düzeltici eylemi sunmalıdır; IF eşleşen kayıt bulunamazsa, THE Chatbot SHALL Kullanıcıyı bilgilendirmeli ve yeni düzeltici eylemler tanımlamasını istemelidir.
4. WHEN 8D Metodolojisi kullanılan bir Oturum tamamlandığında, THE System SHALL sekiz disiplinin tamamını ve yanıtlarını içeren yapılandırılmış bir 8D raporu JSON formatında oluşturmalı ve Problem_Kaydı'na eklemelidir; IF rapor oluşturma başarısız olursa, THE System SHALL Problem_Kaydı'na kısmi rapor eklememelidir ve Kullanıcıya hata döndürmelidir. THE System SHALL ayrıca başarıyla oluşturulmuş bir 8D raporunun Oturum tamamlanma durumundan bağımsız olarak bir Problem_Kaydı'na eklenmesine izin vermelidir.
5. IF bir Kullanıcı sekiz disiplinin tamamı tamamlanmadan Oturumu sonlandırmaya çalışırsa, THEN THE System SHALL tamamlanmamış disiplinlerin tanımlayıcılarını listeleyen bir hata mesajı döndürmelidir.

---

### Gereksinim 6: Problem Kaydı Oluşturma ve Bilgi Havuzuna İşleme

**Kullanıcı Hikayesi:** Bir Kullanıcı olarak, tamamlanan problem çözme oturumunun otomatik olarak Bilgi Havuzuna Problem Kaydı olarak kaydedilmesini istiyorum; böylece organizasyon bu deneyimden gelecekte yararlanabilsin.

#### Kabul Kriterleri

1. WHEN bir Kullanıcı bir Oturumu sonlandırdığında, THE System SHALL şu bilgileri içeren bir Problem_Kaydı oluşturmalıdır: oturum tanımlayıcısı, problem açıklaması, seçilen Metodoloji, tüm adım yanıtları, tespit edilen kök neden, uygulanan düzeltici eylemler ve Öğrenilen Dersler.
2. WHEN bir Problem_Kaydı oluşturulduğunda, THE Embedding_Service SHALL Problem_Kaydı'nın birleşik metin içeriğinin vektör gömülüsünü üretmeli ve 10 saniye içinde Vektör_Deposu'na kaydetmelidir; hem gömülü üretimi hem de depolama işleminin bu 10 saniyelik süre içinde tamamlanması zorunludur.
3. WHEN Problem_Kaydı ve gömülüsü başarıyla kaydedildiğinde, THE System SHALL Kullanıcıya kaydın Bilgi_Tabanı'na kaydedildiğini belirten bir onay mesajı göstermelidir; THE System SHALL onay mesajının gösterilememesi durumunda bile Oturumun kapanmasına izin vermelidir.
4. IF Embedding_Service ilk denemede gömülü üretmeyi başaramazsa, THEN THE System SHALL Problem_Kaydı'nı bekleyen kuyruğa almalı ve 30 saniyelik aralıklarla en fazla 3 kez gömülü işlemini yeniden denemelidir; IF 3 denemenin tamamı başarısız olursa, THE System SHALL kaydı gömülü-başarısız olarak işaretlemeli ve Admin'i uyarmalıdır.
5. WHEN bir Problem_Kaydı oluşturulduğunda, THE System SHALL şu metadata etiketlerini atamalıdır: endüstri sektörü, departman, problem kategorisi, kullanılan metodoloji ve çözüm tarihi; IF herhangi bir metadata alanı Kullanıcı tarafından sağlanmamışsa, THE System SHALL o alanı null olarak ayarlamalıdır.

---

### Gereksinim 7: Öğrenilen Dersler Üretimi

**Kullanıcı Hikayesi:** Bir Kullanıcı olarak, problem çözme oturumunun sonunda sistemin otomatik olarak Öğrenilen Dersler özeti oluşturmasını istiyorum; böylece temel çıkarımlar yapılandırılmış ve yeniden kullanılabilir bir formatta kayıt altına alınsın.

#### Kabul Kriterleri

1. WHEN bir Oturum sonlandırma adımına ulaştığında, THE LLM SHALL tam Oturum içeriğine dayalı olarak en az 100, en fazla 500 kelimeden oluşan bir Öğrenilen_Dersler özeti oluşturmalı ve Kullanıcıya sunmalıdır.
2. WHEN Öğrenilen_Dersler özeti sunulduğunda, THE System SHALL Kullanıcının kaydetmeden önce içeriği bir metin alanında düzenlemesine izin vermelidir; IF Kullanıcı içeriği düzenlemezse, THE System SHALL orijinal LLM tarafından üretilen içeriği açık bir düzenleme gerektirmeden doğrulamalıdır; kaydedilmek üzere gönderilen içeriğin kabul edilebilmesi için 100 ile 500 kelime arasında olması zorunludur.
3. WHEN Kullanıcı Öğrenilen_Dersler içeriğini onay için gönderdiğinde, THE System SHALL en az 100 kelime içerdiğini doğrulamalıdır; IF içerik 100 kelimeden azsa, THE System SHALL kaydetmeden bir doğrulama hatası döndürmelidir.
4. THE Öğrenilen_Dersler özeti SHALL şu bileşenleri içermelidir: kök nedenin açıklaması, alınan düzeltici eylemler, sonuç ve en az bir önleyici öneri; IF LLM tarafından üretilen özet bu dört bileşenden herhangi birini içermiyorsa, THE System SHALL eksik her bileşen için yapılandırılmış bir yer tutucu eklemeli ve ardından Kullanıcıya sunmalıdır.
5. IF LLM 15 saniye içinde Öğrenilen_Dersler özeti oluşturmayı başaramazsa, THEN THE System SHALL Kullanıcıya manuel tamamlama için etiketli alanlar içeren yapılandırılmış bir şablon sunmalıdır: kök neden açıklaması, alınan düzeltici eylemler, sonuç ve önleyici öneri.

---

### Gereksinim 8: Bilgi Tabanı Sorgulama ve Benzer Problem Arama

**Kullanıcı Hikayesi:** Bir Kullanıcı olarak, Bilgi Tabanı'nda benzer geçmiş problemleri aramak istiyorum; böylece sıfırdan başlamadan kanıtlanmış çözümlere hızlıca ulaşabileyim.

#### Kabul Kriterleri

1. WHEN bir Kullanıcı 10 ile 500 karakter arasında bir arama sorgusu gönderdiğinde, THE RAG_Engine SHALL Bilgi_Tabanı'ndan anlamsal olarak benzer Problem_Kayıtlarının sıralı listesini 5 saniye içinde döndürmeli; sonuçlar anlamsal benzerlik skoruna göre azalan sırada sıralanmalıdır.
2. WHEN arama sonuçları döndürüldüğünde, THE System SHALL sonuçları anlamsal benzerlik skoruna göre azalan sırada göstermeli; sorgu başına en fazla 10 sonuç sunulmalıdır.
3. WHEN arama sonuçları döndürüldüğünde, THE System SHALL her sonuç için şu bilgileri göstermelidir: problem başlığı, kullanılan metodoloji, kök neden özeti, çözüm durumu ve tam sayı yüzde olarak benzerlik skoru.
4. WHEN bir Kullanıcı arama sonuçlarından bir Problem_Kaydı seçtiğinde, THE System SHALL tüm adım yanıtları ve Öğrenilen_Dersler dahil tam kaydı 2 saniye içinde göstermelidir.
5. WHEN bir Kullanıcı aramaya filtre uyguladığında, THE RAG_Engine SHALL seçilen filtreler tüm arama yürütmesi boyunca aktif kalacak şekilde Bilgi_Tabanı üzerinde anlamsal aramayı yeniden çalıştırmalıdır; desteklenen filtreler şunlardır: endüstri sektörü, departman, metodoloji, tarih aralığı ve çözüm durumu.
6. IF Bilgi_Tabanı belirli bir sorgu için 0,5'in üzerinde anlamsal benzerlik skoruna sahip kayıt içermiyorsa, THEN THE System SHALL Kullanıcıya benzer problem bulunamadığını bildiren bir mesaj göstermeli ve yeni Oturum başlatmak için bir düğme sunmalıdır.
7. IF bir Kullanıcı 10 karakterden kısa bir arama sorgusu gönderirse, THEN THE System SHALL arama yapmadan minimum sorgu uzunluğunu belirten bir doğrulama hata mesajı döndürmelidir.

---

### Gereksinim 9: Problem Kaydı Yönetimi (CRUD)

**Kullanıcı Hikayesi:** Bir Kullanıcı olarak, mevcut Problem Kayıtlarını görüntülemek, düzenlemek ve yönetmek istiyorum; böylece Bilgi Tabanı'nı doğru ve güncel tutabileyim.

#### Kabul Kriterleri

1. WHEN bir Kullanıcı sayfalandırılmış Problem_Kayıtları listesi istediğinde, THE System SHALL varsayılan sayfa boyutu 20 ve maksimum sayfa boyutu 100 olacak şekilde bir kayıt sayfası döndürmeli; yanıtta toplam kayıt sayısı ve mevcut sayfa numarası yer almalıdır; IF bir Kullanıcı 100'ü aşan bir sayfa boyutu isterse, THE System SHALL varsayılan sayfa boyutu olan 20'yi kullanmalıdır.
2. WHEN bir Kullanıcı tanımlayıcısıyla belirli bir Problem_Kaydı istediğinde, THE System SHALL tam kaydı 2 saniye içinde döndürmelidir.
3. WHEN yetkili bir Kullanıcı bir Problem_Kaydı güncellemesi gönderdiğinde, THE System SHALL yapılandırılmış kaydı güncellemeli ve 15 saniye içinde Vektör_Deposu'ndaki vektör gömülüsünü yeniden üretmelidir; IF Vektör_Deposu gömülü yeniden üretimi başarısız olursa, THE System SHALL yapılandırılmış kayıt güncellemesini geri almalı ve Kullanıcıya hata döndürmelidir.
4. WHEN yetkili bir Kullanıcı bir Problem_Kaydı sildiğinde ve hem yapılandırılmış kayıt silme hem de vektör gömülüsü kaldırma işlemi başarılı olduğunda, THE System SHALL başarı yanıtı döndürmelidir; IF Vektör_Deposu kaldırma işlemi başarısız olursa, THE System SHALL yapılandırılmış kayıt silme işlemini geri almalı ve Kullanıcıya hata döndürmelidir.
5. WHEN bir Problem_Kaydı üzerinde herhangi bir oluşturma, güncelleme veya silme işlemi gerçekleştirildiğinde, THE System SHALL şu bilgileri içeren bir denetim logu kaydı yazmalıdır: Kullanıcı tanımlayıcısı, zaman damgası, işlem türü (oluşturma/güncelleme/silme) ve değiştirilen tüm alanların önceki ve sonraki değerleri.
6. IF yetkisiz bir Kullanıcı bir Problem_Kaydı oluşturmaya, güncellemeye veya silmeye çalışırsa, THEN THE System SHALL yetkilendirme başarısızlığı noktasında istek işlemenin ne kadar ilerlediğinden bağımsız olarak herhangi bir veriyi değiştirmeden HTTP 403 Forbidden yanıtı döndürmelidir.
7. IF bir güncelleme sırasında Vektör_Deposu gömülü yeniden üretimi başarısız olursa, THEN THE System SHALL yapılandırılmış kaydı önceki durumuna geri almalı ve hata yanıtı döndürmeli; yapılandırılmış depo ile Vektör_Deposu arasında kısmi durum oluşmamalıdır.

---

### Gereksinim 10: Kullanıcı Kimlik Doğrulama ve Yetkilendirme

**Kullanıcı Hikayesi:** Bir Admin olarak, sisteme erişimi rol tabanlı izinlerle kontrol etmek istiyorum; böylece hassas problem kayıtları korunabilsin ve yalnızca yetkili kullanıcılar Bilgi Tabanı'nı değiştirebilsin.

#### Kabul Kriterleri

1. WHEN bir API isteği geçerli bir kimlik doğrulama token'ı ile alındığında (mevcut, doğru imzalı, süresi dolmamış ve iptal edilmemiş), THE System SHALL isteği kimliği doğrulanmış Kullanıcının rolüne göre işlemelidir.
2. THE System SHALL iki rolü desteklemelidir: Kullanıcı (okuma ve oluşturma erişimi) ve Admin (tüm Kullanıcı izinleri artı güncelleme ve silme erişimi).
3. WHEN bir kimlik doğrulama token'ının süresi dolduğunda, THE System SHALL HTTP 401 Unauthorized yanıtı döndürmeli ve istemcinin yeniden kimlik doğrulaması yapmasını istemelidir; IF bir API isteği eksik token ile alınırsa, THE System SHALL format doğrulaması yapmadan HTTP 401 Unauthorized yanıtı döndürmelidir; IF bir API isteği hatalı biçimli token ile alınırsa, THE System SHALL önce token formatını doğrulamalı ve süresi dolmuş token yanıtından farklı uygun bir HTTP hata kodu döndürmelidir.
4. IF bir Admin yeni bir kullanıcı hesabı oluşturursa, THEN THE System SHALL yeni kullanıcıya bir onay bildirimi göndermeli ve yeni kullanıcının ilk girişte en az 8 karakter, en az bir büyük harf, bir küçük harf, bir rakam ve bir özel karakter içeren bir şifre belirlemesini zorunlu kılmalıdır.
5. THE System SHALL tüm saklanan şifreleri minimum 12 maliyet faktörü ile bcrypt kullanarak hashlemelidir.
6. IF bir API isteği eksik kimlik doğrulama token'ı ile alınırsa, THEN THE System SHALL format doğrulaması yapmadan HTTP 401 Unauthorized yanıtı döndürmelidir; IF bir API isteği hatalı biçimli kimlik doğrulama token'ı ile alınırsa, THEN THE System SHALL önce token formatını doğrulamalı ve token'ın ayrıştırılabilir kullanıcı verisi içerip içermediğinden bağımsız olarak isteği işlemeden HTTP 401 Unauthorized yanıtı döndürmelidir.
7. IF kimliği doğrulanmış bir Kullanıcının rolü istenen işlem için gerekli izni içermiyorsa, THEN THE System SHALL isteği işlemeden HTTP 403 Forbidden yanıtı döndürmelidir.

---

### Gereksinim 11: API Tasarımı ve Entegrasyon

**Kullanıcı Hikayesi:** Bir geliştirici olarak, iyi belgelenmiş bir RESTful API istiyorum; böylece frontend ve üçüncü taraf sistemler Problem Bilgi Yönetim Sistemi ile güvenilir biçimde entegre olabilsin.

#### Kabul Kriterleri

1. THE API SHALL tüm temel işlemleri (oturum yönetimi, bilgi tabanı arama, problem kaydı CRUD) GET, POST, PUT ve DELETE HTTP yöntemlerini kullanan RESTful endpoint'ler olarak sunmalıdır.
2. THE API SHALL tüm yanıtları tutarlı bir zarf yapısıyla JSON formatında döndürmelidir; zarf şu alanları içermelidir: `status` alanı (string), `data` alanı (nesne veya dizi, hata durumunda null) ve `error` alanı (kod ve mesaj içeren nesne, başarı durumunda null); her yanıtta `data` veya `error` alanlarından tam olarak biri null olmalı, katı karşılıklı dışlamalılık zorunlu tutulmalıdır; sistem uygun JSON zarfı oluşturamayacak kadar bozulduğunda döndürülen HTTP 503 yanıtları bu gereksinimden muaftır.
3. WHEN `/docs` endpoint'i istendiğinde, THE System SHALL mevcut tüm endpoint'leri, istek şemalarını ve yanıt şemalarını açıklayan bir OpenAPI 3.0 spesifikasyon belgesi döndürmelidir.
4. WHEN API hatalı biçimli JSON gövdesi içeren bir istek aldığında, THE System SHALL belirli alan veya sözdizimi sorununu tanımlayan bir hata mesajıyla HTTP 422 Unprocessable Entity yanıtı döndürmelidir.
5. WHEN kimliği doğrulanmış bir Kullanıcı 60 saniyelik pencerede 100 API isteğini aştığında, THE System SHALL rate limit'in ne zaman sıfırlanacağını belirten `Retry-After` header'ı ile HTTP 429 Too Many Requests yanıtı döndürmelidir; IF sistem zaten bozulmuş durumdaysa ve HTTP 503 yanıtları döndürüyorsa, THE System SHALL rate limiting'i atlayarak HTTP 503 yanıtlarının HTTP 429'a göre öncelikli olmasına izin vermelidir.
6. WHEN `/health` endpoint'i istendiğinde, THE System SHALL yalnızca API süreci çalışıyor ve tüm bağımlı servisler (veritabanı, Vektör_Deposu) erişilebilir durumdaysa HTTP 200, aksi halde HTTP 503 döndürmelidir; WHEN `/ready` endpoint'i istendiğinde, THE System SHALL yalnızca tüm bağımlı servisler (veritabanı, Vektör_Deposu) erişilebilir durumdaysa HTTP 200, aksi halde HTTP 503 döndürmelidir.

---

### Gereksinim 12: Performans ve Ölçeklenebilirlik

**Kullanıcı Hikayesi:** Bir Kullanıcı olarak, eşzamanlı kullanım altında bile sistemin hızlı yanıt vermesini istiyorum; böylece problem çözme oturumları performans darboğazları nedeniyle kesintiye uğramasın.

#### Kabul Kriterleri

1. THE API SHALL tek kullanıcı p95 taban çizgisi en fazla 2000 milisaniye olmak üzere, p95 yanıt süresi 2400 milisaniyeyi aşmadan en az 50 eşzamanlı Oturumu işleyebilmelidir.
2. WHEN RAG_Engine en fazla 10.000 Problem_Kaydı içeren bir Bilgi_Tabanı üzerinde anlamsal arama gerçekleştirdiğinde, THE System SHALL sonuçları 5 saniye içinde döndürmelidir.
3. WHEN önceki özdeş bir sorgudan itibaren 300 saniye içinde aynı parametrelerle bir Bilgi_Tabanı arama sorgusu alındığında, THE System SHALL önbelleğe alınmış sonucu p95 yanıt süresi 500 milisaniyeyi aşmadan döndürmelidir.
4. WHILE Docker_Ortamı çalışırken, THE System SHALL yapılandırılmış log çıktısına 60 saniyelik aralıklarla bellek kullanımını ve CPU kullanımını kaydetmeli; yalnızca bir alt küme toplanabiliyorsa mevcut metrikleri kaydetmelidir; WHEN Docker_Ortamı kapandığında, THE System SHALL günlük kaydını atomik olarak durdurmalıdır — herhangi bir kapatma süreci başlamadan önce loglama durmalıdır.
5. IF Vektör_Deposu 10 saniyelik pencerede 3 ardışık bağlantı hatası kaydederse, THEN THE System SHALL tüm anlamsal arama isteklerinde anlamsal aramanın geçici olarak kullanılamadığını belirten bozulmuş mod yanıtı döndürmeli; yeni Oturumların oluşturulmasına ve kalıcı olarak kaydedilmesine izin vermelidir; WHEN sistem bozulmuş moddayken, THE System SHALL yeni Oturumların anlamsal arama isteği yapmasını tamamen engellemelidir.

---

### Gereksinim 13: Problem Kaydı Serileştirme ve Ayrıştırma (Parser/Serializer)

**Kullanıcı Hikayesi:** Bir geliştirici olarak, Problem Kayıtlarının JSON'a güvenilir biçimde serileştirilmesini ve JSON'dan ayrıştırılmasını istiyorum; böylece depolama, erişim ve API taşıması sırasında veri bütünlüğü korunabilsin.

#### Kabul Kriterleri

1. WHEN bir Problem_Kaydı nesnesi JSON'a serileştirildiğinde, THE Serializer SHALL Problem_Kaydı JSON Şemasına uygun geçerli bir JSON belgesi üretmelidir.
2. WHEN Problem_Kaydı JSON Şemasına uygun geçerli bir JSON belgesi Parser'a sağlandığında, THE Parser SHALL her alanın değeri ve türünün kaynak JSON belgesiyle eşleştiği bir Problem_Kaydı nesnesi üretmelidir.
3. WHEN bir Problem_Kaydı JSON belgesi Pretty_Printer tarafından biçimlendirildiğinde, THE Pretty_Printer SHALL her iç içe geçme seviyesinde 2 boşluk girintili ve sözlüksel sırayla sıralanmış anahtarlarla çıktı üretmelidir.
4. FOR ANY geçerli Problem_Kaydı nesnesi P için, WHEN P JSON'a serileştirilip elde edilen JSON ayrıştırıldığında, THE elde edilen nesne SHALL P ile alan bazında değer ve tür eşitliğine sahip olmalıdır.
5. IF Parser'a sağlanan JSON belgesi Problem_Kaydı JSON Şemasında tanımlanmayan alanlar içeriyorsa, THEN THE Parser SHALL bu alanları görmezden gelmeli ve hata oluşturmadan tanımlı tüm alanları başarıyla ayrıştırmalıdır.
6. IF Parser'a sağlanan JSON belgesinde Problem_Kaydı JSON Şemasında zorunlu olarak işaretlenmiş bir alan eksikse, THEN THE Parser SHALL eksik zorunlu alanın adını açıkça belirten bir doğrulama hata mesajı döndürmelidir.

---

### Gereksinim 14: Docker Ortamı ve Dağıtım

**Kullanıcı Hikayesi:** Bir geliştirici olarak, tüm sistemin Docker ortamında çalışmasını istiyorum; böylece dağıtım tekrarlanabilir ve ortamdan bağımsız olsun.

#### Kabul Kriterleri

1. THE System SHALL tüm gerekli servisleri tanımlayan bir `docker-compose.yml` dosyası sağlamalıdır: FastAPI backend, Vektör_Deposu (örn. ChromaDB veya Qdrant), ilişkisel veritabanı ve önbellek gibi yardımcı servisler.
2. WHEN `docker-compose up` önceden mevcut volume'lar olmayan temiz bir ortamda çalıştırıldığında, THE System SHALL manuel müdahale olmaksızın 120 saniye içinde `/ready` endpoint'inin HTTP 200 döndürdüğü bir duruma ulaşmalıdır.
3. THE System SHALL LLM API anahtarları, Vektör_Deposu bağlantı dizeleri ve veritabanı kimlik bilgileri dahil tüm yapılandırma değerleri için ortam değişkenlerini kullanmalıdır; hiçbir gizli değer herhangi bir kaynak dosyaya veya commit edilmiş `docker-compose.yml` dosyasına sabit kodlanmamalıdır; tüm gerekli ortam değişkeni adlarını yer tutucu değerlerle listeleyen bir `.env.example` dosyası sağlanmalıdır.
4. WHEN bir Docker konteyneri yeniden başlatıldığında, THE System SHALL `docker-compose.yml` dosyasında tanımlanan adlandırılmış kalıcı volume'lardan tüm veritabanı kayıtlarını ve Vektör_Deposu gömülülerini veri kaybı olmadan geri yüklemelidir.
5. THE FastAPI backend için `Dockerfile` SHALL sıkıştırılmış boyutu 1 GB'ı aşmayan bir imaj üretmelidir; bu sınırın 50 MB'a kadar üzerinde bir tolerans kabul edilebilir.
6. THE depo SHALL tüm gerekli ortam değişkeni adlarını gizli olmayan yer tutucu değerlerle listeleyen bir `.env.example` dosyası içermeli ve `.env` dosyası kazara gizli bilgi ifşasını önlemek için `.gitignore` dosyasında listelenmelidir.

---

### Gereksinim 15: Gözlemlenebilirlik ve Loglama

**Kullanıcı Hikayesi:** Bir Admin olarak, tüm sistem operasyonları için yapılandırılmış loglar ve izleme istiyorum; böylece üretim ortamında sorunları teşhis edebilir ve sistem sağlığını takip edebileyim.

#### Kabul Kriterleri

1. WHEN bir API isteği işlendiğinde, THE System SHALL INFO seviyesinde şu bilgileri içeren yapılandırılmış bir JSON log kaydı yayınlamalıdır: zaman damgası (ISO 8601), istek yöntemi, endpoint yolu, yanıt durum kodu ve milisaniye cinsinden yanıt süresi.
2. WHEN işlenmeyen bir istisna oluştuğunda, THE System SHALL tam yığın izini ERROR seviyesinde kaydetmeli ve iç uygulama ayrıntılarını veya yığın izi içeriğini açığa çıkarmadan beklenmedik bir hata oluştuğunu belirten bir mesaj içeren HTTP 500 yanıtı döndürmelidir; tüm işlenmeyen istisnalar için ERROR seviyesi loglama ve HTTP 500 yanıtları zorunludur.
3. WHEN bir LLM API çağrısı yapıldığında, THE System SHALL şu bilgileri içeren yapılandırılmış bir kayıt oluşturmalıdır: model adı, prompt token sayısı, tamamlama token sayısı, milisaniye cinsinden gecikme ve başarı veya başarısızlık durumu.
4. WHEN bir Bilgi_Tabanı yazma işlemi gerçekleştirildiğinde, THE System SHALL şu bilgileri içeren yapılandırılmış bir kayıt oluşturmalıdır: Problem_Kaydı tanımlayıcısı, işlem türü ve şu değerlerden biri olarak gömülü üretim durumu: `success` (başarılı), `failure` (başarısız) veya `pending` (beklemede).
5. IF bir log kaydı Kullanıcı tarafından sağlanan içerik barındırıyorsa, THEN THE System SHALL log kaydını yazmadan önce bu içerikteki tespit edilen adları, e-posta adreslerini veya IP adreslerini `[REDACTED]` token'ı ile değiştirmelidir.
