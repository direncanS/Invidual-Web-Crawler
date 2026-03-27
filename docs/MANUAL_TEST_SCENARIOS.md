# Manuel Test Senaryolari - Web Crawler

## Swagger UI ile Nasil Test Edilir?

1. `http://localhost:8000/docs` adresini ac
2. `POST /auth/register` ile kullanici olustur
3. `POST /auth/login` ile giris yap, response'taki `access_token` degerini kopyala
4. Sayfanin sag ustundeki **Authorize** butonuna tikla
5. Acilan kutuya `Bearer <token>` yapistir, **Authorize**'a tikla
6. Artik korunmus endpointleri cagirabilirsin. Her response'ta **status code** ve **body** kontrol et

### Response Dogrulama Kurallari

| Hata Tipi | Status | Body Kontrolu |
|-----------|--------|---------------|
| **Business error** (duplicate email, invalid credentials, vb.) | 400 / 401 | `detail.error.code` + `detail.error.http_status` kontrol et |
| **Validation error** (eksik alan, kisa sifre, gecersiz email) | 422 | `detail` bir **list** doner, `detail.error` beklenmez |
| **Auth yok** (HTTPBearer header yok) | 403 | Sadece status kontrol et, JSON shape bekleme |

Business error formati:
```json
{"detail": {"error": {"code": "<hata_kodu>", "message": "<aciklama>", "http_status": <int>}}}
```

---

## Baslangic: Ortami Ayaga Kaldirma

```bash
docker compose down -v          # Temiz baslangic
docker compose up -d --build    # Tum servisleri baslat
docker compose logs -f backend  # "Uvicorn running" gorunene kadar bekle
```

**Kontrol:**
- `http://localhost:8000/docs` aciliyor mu? (Swagger UI)
- `http://localhost:8025` aciliyor mu? (MailHog)
- `http://localhost:8088` aciliyor mu? (Demo Site)

---

## S1: Health Check

| Adim | Islem | Beklenen Sonuc |
|------|-------|----------------|
| 1.1 | `GET http://localhost:8000/health` | `{"status": "ok"}` - 200 |

---

## S2: Kullanici Kayit (Register)

Swagger UI'da `POST /auth/register` endpoint'ini kullan.

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 2.1 | Basarili kayit | `{"nickname":"testuser","email":"test@example.com","password":"Test1234!"}` | 201 - id, nickname, email donmeli |
| 2.2 | Ayni email ile tekrar kayit | Ayni body | 400 - `detail.error.code == "email_already_exists"` |
| 2.3 | Ayni nickname ile tekrar kayit | `{"nickname":"testuser","email":"test2@example.com","password":"Test1234!"}` | 400 - `detail.error.code == "nickname_already_exists"` |
| 2.4 | Zayif sifre (8 karakterden az) | `{"nickname":"weak","email":"weak@example.com","password":"123"}` | 422 - Pydantic validation error (`detail` bir list) |
| 2.5 | Gecersiz email formati | `{"nickname":"bad","email":"notanemail","password":"Test1234!"}` | 422 - Pydantic validation error (`detail` bir list) |
| 2.6 | Ikinci bir kullanici kaydet | `{"nickname":"testuser2","email":"test2@example.com","password":"Test1234!"}` | 201 - basarili (sonraki testlerde sahiplik kontrolu icin) |

---

## S3: Giris (Login)

Swagger UI'da `POST /auth/login` endpoint'ini kullan.

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 3.1 | Email ile giris | `{"email_or_nickname":"test@example.com","password":"Test1234!"}` | 200 - `access_token` donmeli |
| 3.2 | Nickname ile giris | `{"email_or_nickname":"testuser","password":"Test1234!"}` | 200 - `access_token` donmeli |
| 3.3 | Yanlis sifre | `{"email_or_nickname":"test@example.com","password":"YanlisSifre1!"}` | 401 - `detail.error.code == "invalid_credentials"`, `detail.error.http_status == 401` |
| 3.4 | Olmayan kullanici | `{"email_or_nickname":"yok@example.com","password":"Test1234!"}` | 401 - `detail.error.code == "invalid_credentials"`, `detail.error.http_status == 401` |

> **Not:** 3.1'deki `access_token` degerini kopyala. Bundan sonraki tum testlerde Swagger UI'da "Authorize" butonuna tiklayip `Bearer <token>` olarak yapistir.

> **Uyari:** Login password alani `min_length=8` validasyonuna sahip. 8 karakterden kisa bir yanlis sifre gonderirseniz 401 yerine 422 alirsiniz.

---

## S4: Profil Goruntuleme ve Guncelleme

**On kosul:** S3.1'den alinan token ile authorize olunmali.

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 4.1 | `GET /me` | - | 200 - nickname: "testuser", email: "test@example.com" |
| 4.2 | `PUT /me` - nickname degistir | `{"nickname":"yeniisim"}` | 200 - nickname: "yeniisim" |
| 4.3 | `GET /me` tekrar kontrol | - | 200 - nickname: "yeniisim" (degismis olmali) |
| 4.4 | `PUT /me` - baskasinin nickname'i | `{"nickname":"testuser2"}` | 400 - `detail.error.code == "nickname_already_exists"` |
| 4.5 | `PUT /me` - eski haline dondur | `{"nickname":"testuser"}` | 200 - basarili |
| 4.6 | Token olmadan `GET /me` | Authorize'i kaldir, tekrar dene | 403 - HTTPBearer header yok (JSON body bekleme) |

---

## S5: Sifre Sifirlama (Forgot/Reset Password)

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 5.1 | `POST /auth/forgot-password` | `{"email":"test@example.com"}` | 200 - `{"message": "..."}` |
| 5.2 | MailHog'u kontrol et | `http://localhost:8025` ac | Gelen kutusunda reset emaili gormeli, icinde token olmali |
| 5.3 | Token'i kopyala | MailHog'daki emailden token'i al | - |
| 5.4 | `POST /auth/reset-password` | `{"token":"<kopyalanan_token>","new_password":"YeniSifre1!"}` | 200 - basarili |
| 5.5 | Eski sifre ile giris dene | `POST /auth/login` - eski sifre | 401 - `invalid_credentials` |
| 5.6 | Yeni sifre ile giris | `POST /auth/login` - `"password":"YeniSifre1!"` | 200 - basarili, yeni token alinmali |
| 5.7 | Ayni token'i tekrar kullan | `POST /auth/reset-password` ayni token | 400 - `detail.error.code == "reset_token_used"` |
| 5.8 | Olmayan email icin forgot | `{"email":"yok@example.com"}` | 200 - **ayni mesaj** (email varligini sizmamali, ayni response) |
| 5.9 | 60 saniye suresi dolmus token | Yeni forgot-password yap, 70 saniye bekle, sonra reset-password dene | 400 - `detail.error.code == "reset_token_expired"` |

> **Not:** 5.9'da 70 saniye beklemen gerekiyor. Zamanlama kritik.

---

## S6: Crawl Job Baslatma (Depth Testleri)

**On kosul:** S5.6'dan alinan yeni token ile authorize ol.

### Depth 1 - Sadece Baslangic URL

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 6.1 | `POST /crawl/jobs` | `{"start_url":"http://demo_site/index.html","depth":1}` | 201 - job id, status: "queued" |
| 6.2 | `GET /crawl/jobs/{job_id}` - status `"done"` olana kadar 2 sn arayla tekrar dene (max 30 sn) | - | status: "done" |
| 6.3 | `GET /crawl/jobs/{job_id}/pages` | - | Sadece 1 sayfa: index.html (depth_level=1) |
| 6.4 | `GET /crawl/jobs/{job_id}/pdfs` | - | index.html'de sample.pdf linki var; crawler PDF'leri depth 1'de yakaliyorsa 1 PDF (deduplicated), yakalamiyorsa bos liste |

### Depth 2 - Baslangic + Ayni Host Linkleri

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 6.5 | `POST /crawl/jobs` | `{"start_url":"http://demo_site/index.html","depth":2}` | 201 |
| 6.6 | `GET /crawl/jobs/{job_id}` - status `"done"` olana kadar 2 sn arayla tekrar dene (max 30 sn) | - | status: "done" |
| 6.7 | `GET /crawl/jobs/{job_id}/pages` | - | index.html + level2_a.html + level2_b.html (ayni host sayfalar). deep/ignored.html bu seviyede **OLMAMALI** |
| 6.8 | `GET /crawl/jobs/{job_id}/pdfs` | - | sample.pdf bulunmus olmali (1 adet, deduplicated) |

### Depth 3 - Ayni Host + External Landing

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 6.9 | `POST /crawl/jobs` | `{"start_url":"http://demo_site/index.html","depth":3}` | 201 |
| 6.10 | `GET /crawl/jobs/{job_id}` - status `"done"` olana kadar 2 sn arayla tekrar dene (max 30 sn) | - | status: "done" |
| 6.11 | `GET /crawl/jobs/{job_id}/pages` | - | Depth 2 sayfalari + deep/ignored.html + external_landing.html |
| 6.12 | Kontrol: external_extra.html listede var mi? | - | **OLMAMALI** - external sitede expansion yapilmaz |

### Gecersiz Depth

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 6.13 | Depth 0 ile crawl | `{"start_url":"http://demo_site/index.html","depth":0}` | 422 - validation hatasi (depth ge=1) |
| 6.14 | Depth 4 ile crawl | `{"start_url":"http://demo_site/index.html","depth":4}` | 422 - validation hatasi (depth le=3) |

---

## S7: Crawl Gecmisi (History & Sahiplik)

**On kosul:** S6'daki joblar tamamlanmis olmali.

| Adim | Islem | Beklenen Sonuc |
|------|-------|----------------|
| 7.1 | `GET /crawl/jobs` (testuser token ile) | S6'da olusturulan 3 job listelenmeli |
| 7.2 | testuser2 ile login ol, yeni token al | 200 - token alinir |
| 7.3 | `GET /crawl/jobs` (testuser2 token ile) | Bos liste - baska kullanicinin joblari gorulmemeli |
| 7.4 | testuser2 ile testuser'in job_id'sine `GET /crawl/jobs/{job_id}` | 404 - erisim engellenmeli |
| 7.5 | testuser2 ile `GET /pdfs` | Bos liste - testuser'in PDF'leri gorulmemeli |
| 7.6 | testuser2 ile testuser'in pdf_id'sine `GET /pdfs/{pdf_id}` | 404 - `detail.error.code == "not_found"` |

---

## S8: PDF Islemleri

**On kosul:** S6.8'deki depth 2 crawl tamamlanmis, sample.pdf bulunmus olmali. testuser token'i ile devam et.

| Adim | Islem | Beklenen Sonuc |
|------|-------|----------------|
| 8.1 | `GET /pdfs` | En az 1 PDF listelenmeli (sample.pdf) |
| 8.2 | PDF id'sini not al | Listeden ilk PDF'in id'sini kopyala |
| 8.3 | `GET /pdfs/{pdf_id}` | PDF detaylari: source_url, file_path, sha256, downloaded_at |
| 8.4 | `GET /pdfs/{pdf_id}/download` | PDF dosyasi indirilmeli, Content-Type: application/pdf |
| 8.5 | Indirilen dosyayi ac | Gecerli bir PDF dosyasi olmali, acilabildigi kontrol edilmeli |
| 8.6 | testuser2 token ile `GET /pdfs` | Bos liste veya sadece kendi PDF'leri (testuser'in PDF'leri gorulmemeli) |

---

## S9: PDF Top-10 Kelime Istatistikleri

**On kosul:** S8'deki PDF'in id'si bilinmeli.

| Adim | Islem | Beklenen Sonuc |
|------|-------|----------------|
| 9.1 | `GET /pdfs/{pdf_id}/stats/top-words` | 200 - `words` dizisi donmeli, max 10 eleman |
| 9.2 | Siralama kontrolu | Kelimeler count'a gore azalan sirada, esitlikte alfabetik |
| 9.3 | Normalizasyon kontrolu | Tum kelimeler kucuk harf, noktalama isaretleri yok (sadece 2+ harf iceren kelimeler) |
| 9.4 | Olmayan PDF id ile dene | `GET /pdfs/00000000-0000-0000-0000-000000000000/stats/top-words` | 404 - `detail.error.code == "not_found"` |

> **Not:** Eger stats henuz hesaplanmadiysa (Celery task bitmemisse) 409 `"not_ready"` donebilir. Birkac saniye bekleyip tekrar deneyin.

---

## S10: Kelime ile PDF Arama

**On kosul:** S9 tamamlanmis, en az bir PDF'in top-words'u hesaplanmis olmali.

| Adim | Islem | Beklenen Sonuc |
|------|-------|----------------|
| 10.1 | S9.1'deki kelimelerden birini sec | Ornegin ilk kelime "sample" ise |
| 10.2 | `GET /search/top-words?word=sample` | 200 - results dizisinde en az 1 PDF |
| 10.3 | Olmayan kelime ile ara | `GET /search/top-words?word=xyznonexistent` | 200 - bos results dizisi `[]` (hata degil) |
| 10.4 | Buyuk harfle ara | `GET /search/top-words?word=SAMPLE` | 200 - Sonuc donmeli (search case-insensitive: `word.lower()` kullanilir) |

---

## S11: Wordcloud - Tekli PDF

**On kosul:** S8'deki PDF id bilinmeli.

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 11.1 | `POST /wordclouds/single` | `{"pdf_id":"<pdf_id>"}` | 201 - wordcloud id, mode: "single" |
| 11.2 | Birkac saniye bekle | Celery task'in tamamlanmasini bekle | - |
| 11.3 | `GET /wordclouds/{id}/image` | - | PNG gorsel donmeli, Content-Type: image/png |
| 11.4 | Gorseli indir ve ac | Tarayicida veya goruntleyicide ac | Gecerli bir wordcloud gorseli olmali |

> **Not:** 11.3'te eger gorsel henuz hazir degilse 409 `"not_ready"` donebilir. Birkac saniye bekleyip tekrar deneyin.

---

## S12: Wordcloud - Coklu PDF

**On kosul:** En az 2 PDF gerekli. Eger sadece 1 PDF varsa, yeni bir crawl job daha olustur veya bu adimi atla.

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 12.1 | Tek PDF ile dene | `POST /wordclouds/multi` body: `{"pdf_ids":["<pdf_id_1>"]}` | 422 - validation hatasi (pdf_ids min_length=2) |
| 12.2 | 2+ PDF ile olustur | `{"pdf_ids":["<pdf_id_1>","<pdf_id_2>"]}` | 201 - wordcloud id, mode: "multi" |
| 12.3 | `GET /wordclouds/{id}/image` | - | PNG gorsel donmeli |

> **Not:** Eger sadece 1 PDF varsa, 12.2'yi test edemezsin. Bu durumda farkli URL'lerle yeni crawl olusturup PDF bulmalisin.

---

## S13: Wordcloud - Zaman Araligi

| Adim | Islem | Body | Beklenen Sonuc |
|------|-------|------|----------------|
| 13.1 | Genis aralik (PDF'leri kapsayan) | `POST /wordclouds/interval` body: `{"start_datetime":"2020-01-01T00:00:00","end_datetime":"2030-12-31T23:59:59"}` | 201 - wordcloud olusturulmali |
| 13.2 | `GET /wordclouds/{id}/image` | - | PNG gorsel donmeli |
| 13.3 | Bos aralik (hic PDF olmayan) | `POST /wordclouds/interval` body: `{"start_datetime":"2000-01-01T00:00:00","end_datetime":"2000-01-02T00:00:00"}` | 404 - `detail.error.code == "not_found"` (gorsel uretilmemeli) |

---

## S14: Veri Kaliciligi (Persistence)

| Adim | Islem | Beklenen Sonuc |
|------|-------|----------------|
| 14.1 | `docker compose restart backend worker` | Backend ve worker yeniden baslar |
| 14.2 | Ayni token ile `GET /me` | Token hala gecerli, profil donmeli (JWT_SECRET degismedi) |
| 14.3 | `GET /crawl/jobs` | Onceki joblar hala listelenmeli |
| 14.4 | `GET /pdfs` | PDF'ler hala listelenmeli |
| 14.5 | `GET /pdfs/{pdf_id}/download` | PDF dosyasi hala indirilebilmeli |
| 14.6 | `GET /pdfs/{pdf_id}/stats/top-words` | Istatistikler hala mevcut olmali |
| 14.7 | `GET /wordclouds/{id}/image` | Wordcloud gorseli hala eriselebilir olmali |

---

## S15: Kenar Durumlari ve Guvenlik

| Adim | Islem | Beklenen Sonuc |
|------|-------|----------------|
| 15.1 | Gecersiz JWT token ile `GET /me` | Header: `Authorization: Bearer invalidtoken123` | 401 - `detail.error.code == "invalid_token"` |
| 15.2 | Token olmadan `GET /me` | Authorization header yok | 403 - sadece status kontrol et |
| 15.3 | Olmayan job id | `GET /crawl/jobs/00000000-0000-0000-0000-000000000000` | 404 - `detail.error.code == "not_found"` |
| 15.4 | Olmayan PDF id ile download | `GET /pdfs/00000000-0000-0000-0000-000000000000/download` | 404 - `detail.error.code == "not_found"` |
| 15.5 | Gecersiz UUID formati | `GET /crawl/jobs/not-a-uuid` | 422 - Pydantic path param validation (`detail` list) |
| 15.6 | Bos body ile register | `POST /auth/register` body: `{}` | 422 - Pydantic validation error (`detail` list) |

---

## Hizli Kontrol Listesi (Checklist)

- [ ] S1: Health check calisiyor
- [ ] S2: Kayit - basarili + hata durumlari
- [ ] S3: Giris - email ile, nickname ile, hatali
- [ ] S4: Profil - goruntuleme, guncelleme, yetki kontrolu
- [ ] S5: Sifre sifirlama - tam akis + token suresi
- [ ] S6: Crawl - depth 1, 2, 3 + gecersiz depth
- [ ] S7: Crawl gecmisi - sahiplik kontrolu
- [ ] S8: PDF listeleme, detay, indirme
- [ ] S9: Top-10 kelime istatistikleri
- [ ] S10: Kelime ile arama
- [ ] S11: Tekli wordcloud
- [ ] S12: Coklu wordcloud
- [ ] S13: Zaman aralikli wordcloud
- [ ] S14: Restart sonrasi veri kaliciligi
- [ ] S15: Kenar durumlari ve guvenlik
