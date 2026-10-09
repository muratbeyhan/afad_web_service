# AFAD Web Service — Earthquake Data Dashboard

Bu repository, AFAD (Afet ve Acil Durum Yönetimi Başkanlığı) tarafından sağlanan deprem verilerini web servis üzerinden çekerek interaktif olarak haritalandıran, görselleştiren ve istatistiksel analizler sunan bir Streamlit uygulamasıdır.

Uygulama, AFAD'ın açık API'si olan `https://deprem.afad.gov.tr/apiv2/event/filter` endpoint'ini kullanarak zaman, derinlik, magnitüd ve mekânsal (konumsal) kriterlere göre dinamik deprem analizi olanağı tanır.

## 🚀 Öne Çıkan Özellikler

- **Çift Modlu Mekânsal Filtreleme (Spatial Bounds Source):**
  - **Map Canvas (Interactive Zoom):** Harita üzerinde yaklaştığınız (zoom) veya kaydırdığınız (pan) alanın canlı koordinat sınırlarını (`bounds`) otomatik olarak tespit eder ve sadece o ekrandaki bölgeye ait depremleri çeker.
  - **Manual Coordinate Input:** Kullanıcının sol panelden enlem (`Min/Max Lat`) ve boylam (`Min/Max Lon`) değerlerini elle girerek sorgulama yapmasını sağlar.
- **AFAD API & .NET Uyumluluğu:** AFAD web servisinin `.NET` backend yapısına uygun sayısal biçimlendirme (`fmt_num`) ve katı zaman formatı (`YYYY-MM-DD HH:MM:SS`) uygulanarak `HTTP 500 Internal Server Error` ve `FormatException` hataları engellenmiştir.
- **Hafıza & Görünüm Koruması (State Management):** `st_folium` ve Streamlit oturum hafızası (`st.session_state`) entegrasyonu sayesinde haritada gezinirken, zoom yaparken veya veri çekme butonuna basıldığında harita konumu sıfırlanmaz, son kaldığı odak alanında kararlı bir şekilde kalır.
- **Interaktif Folium Haritası:** Magnitüd değerine göre dinamik olarak ölçeklenen ve renklendirilen `CircleMarker` yapıları. Tıklandığında konum, büyüklük, derinlik ve tarih ayrıntılarını içeren açılır pop-up penceresi.
- **Çoklu Katman Desteği:** OpenStreetMap ve Esri World Imagery (Uydu) varsayılan olarak sunulur. İsteğe bağlı `MAPBOX_API_KEY` tanımı yapıldığında Mapbox Streets katmanı da aktif olur.
- **Gelişmiş Hata Yakalama ve Detaylı Loglama:** API bağlantı hataları, boş yanıtlar veya format uyumsuzlukları doğrudan kullanıcı arayüzünde canlı uyarı kutuları (`st.error`, `st.warning`) ve gizlenebilir teknik debug panelleri üzerinden gösterilir.
- **Grafik ve Tablo İstatistikleri:** Altair kullanılarak hazırlanan büyüklük aralığına göre deprem dağılım grafikleri, özet metrikler (Toplam deprem, Max M, Ortalama derinlik) ve detaylı pandas veri tablosu.

## 🛠️ Nasıl Çalışır / Mimari

1. **Mod Seçimi:** Kullanıcı sol panelden mekânsal sorgulama kaynağını seçer ("Map Canvas" veya "Manual Input").
2. **Parametre Belirleme:** Tarih, saat, magnitüd ve derinlik aralıkları ayarlanır.
3. **Veri Çekme:** "Get Earthquakes" butonuna tıklandığında, seçilen moda göre belirlenen koordinatlar ve filtreler biçimlendirilerek AFAD API endpoint'ine GET isteği atılır.
4. **Veri İşleme:** Dönen JSON yanıtı temizlenir, sayısal veri tiplerine dönüştürülür (`pd.to_numeric`), eksik koordinatlar filtrelenir ve `st.session_state["deprem_df"]` içerisine kaydedilir.
5. **Görselleştirme:** Veriler harita üzerine işlenir; özet metrikler, Altair bar grafiği ve veri tablosu eşzamanlı olarak güncellenir.

## 🔑 Mapbox API Anahtarı (Opsiyonel)

Mapbox uydu/sokak katmanını kullanmak isterseniz `MAPBOX_API_KEY` değerini aşağıdaki şekillerde sisteme tanıtabilirsiniz:

- **Streamlit Secrets (`.streamlit/secrets.toml`):**
  ```toml
  MAPBOX_API_KEY = "your_mapbox_api_key_here"

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

MIT License

Copyright (c) 2026 Murat Beyhan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Gizlilik ve kullanım uyarısı

AFAD'ın verileri kamuya açık kaynaklardan çekilmektedir. Uygulama sadece veri görselleştirme amaçlıdır; canlı afet yönetimi veya erken uyarı sistemleri için kullanılmamalıdır.
