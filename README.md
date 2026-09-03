# AFAD Web Service — Earthquake Data Dashboard

Bu repository, AFAD (Afet ve Acil Durum Yönetimi Başkanlığı) tarafından sağlanan deprem verilerini alıp görselleştirmek için geliştirilmiş bir Streamlit uygulamasını içerir. Uygulama, AFAD'ın açık API'sinden deprem olaylarını çekerek kullanıcıya filtreleme, harita üzerinde görselleştirme ve temel istatistiksel analizler sunar.

## Öne çıkan özellikler

- AFAD API'sinden gerçek zamanlı veya tarih aralığına göre deprem verisi çekme
- Enlem/boylam, tarih/saat, magnitüd ve derinlik filtreleri
- Interaktif Folium haritası üzerinde her bir deprem için `CircleMarker` (büyüklüğe göre ölçeklenen)
- Harita altlık (base layer) seçici: OpenStreetMap ve Uydu (Esri World Imagery). Opsiyonel olarak Mapbox desteklenir (API anahtarı gerekirse)
- Haritanın sağ alt köşesinde magnitüd için açıklayıcı lejant
- Altair ile hazırlanan magnitüd dağılımı grafikler ve veri tablosu
- Kullanıcı arayüzü İngilizce diline çevrildi ve koyu (premium) bir tema ile stilize edildi

## Nasıl çalışır / Mimari

1. Kullanıcı sol panelden tarih, saat, koordinat kutusu (min/max lat/lon), magnitüd ve derinlik aralığını seçer.
2. "Get Earthquakes" butonuna basıldığında uygulama AFAD'ın `https://deprem.afad.gov.tr/apiv2/event/filter` endpoint'ine istek gönderir.
3. Dönen JSON veriler bir pandas DataFrame'e dönüştürülür, gerekli alanlar sayısal tipe çevrilir ve haritada gösterilir.
4. Her deprem noktası bir popup ile detay (konum, magnitüd, derinlik, tarih) gösterir.
5. Harita üzerinde kullanıcı istediği altlık haritayı (OpenStreetMap veya Satellite) seçebilir. Eğer `MAPBOX_API_KEY` sağlanırsa Mapbox Streets de alternatif olarak görünür.

## API Anahtarı (Mapbox)

Mapbox kullanımı isteğe bağlıdır. Eğer Mapbox tabanlı bir stil eklemek isterseniz aşağıdaki şekillerden birine `MAPBOX_API_KEY` ekleyin:

- Streamlit Cloud secrets: `MAPBOX_API_KEY`
- Ortam değişkeni: `export MAPBOX_API_KEY=your_key_here`

Uygulama anahtar yoksa Mapbox katmanı gösterilmez, OpenStreetMap ve Uydu katmanları çalışır.

## Çalıştırma (lokal)

1. Ortamı hazırlayın (ör. conda veya venv) ve bağımlılıkları kurun. Bu repoda `requirements.txt` kullanılmalıdır.

```bash
conda create -n geo python=3.10 -y
conda activate geo
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:

```bash
streamlit run app.py
```

3. Tarayıcıda `http://localhost:8501` adresini açın.

## Yayınlama

Bu repo Streamlit Community Cloud üzerinde deploy edilebilir. Deploy ayarlarında `MAPBOX_API_KEY` gerekiyorsa `Secrets` bölümüne ekleyin.

## Dosya yapısı

- `app.py` — Streamlit uygulaması ana dosyası
- `requirements.txt` — Çalıştırma için gerekli paketler (Streamlit, folium, pandas, requests, altair, streamlit-folium, branca)

## Katkıda bulunma

Pull request'ler hoş karşılanır. Yeni özellik önerileri veya hata raporları için issue açabilirsiniz.

## Lisans

Bu proje açık kaynak olarak paylaşılmıştır — uygun gördüğünüz lisans metnini ekleyin (varsayılan: MIT).

## Gizlilik ve kullanım uyarısı

AFAD'ın verileri kamuya açık kaynaklardan çekilmektedir. Uygulama sadece veri görselleştirme amaçlıdır; canlı afet yönetimi veya erken uyarı sistemleri için kullanılmamalıdır.
