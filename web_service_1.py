from datetime import datetime
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import requests


def afad_deprem_haritasi(
    start=None,
    end=None,
    minlat=None,
    maxlat=None,
    minlon=None,
    maxlon=None,
    minmag=None,
    maxmag=None,
    mindepth=None,
    maxdepth=None,
    cikti_dosyasi="deprem_haritasi.html",
):
    base_url = "https://deprem.afad.gov.tr/apiv2/event/filter"

    # Parametre sözlüğünü oluştur
    params = {}
    if start:
        params["start"] = start  # Format: "YYYY-MM-DD HH:MM:SS"
    if end:
        params["end"] = end
    if minlat is not None:
        params["minlat"] = minlat
    if maxlat is not None:
        params["maxlat"] = maxlat
    if minlon is not None:
        params["minlon"] = minlon
    if maxlon is not None:
        params["maxlon"] = maxlon
    if minmag is not None:
        params["minmag"] = minmag
    if maxmag is not None:
        params["maxmag"] = maxmag
    if mindepth is not None:
        params["mindepth"] = mindepth
    if maxdepth is not None:
        params["maxdepth"] = maxdepth

    # API İsteği
    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print(f"Hata: API'den veri alınamadı. Durum Kodu: {response.status_code}")
        return

    data = response.json()

    if not data:
        print("Belirtilen kriterlere uygun deprem verisi bulunamadı.")
        return

    df = pd.DataFrame(data)

    # Veri tiplerini dönüştür
    df["latitude"] = pd.to_numeric(df["latitude"])
    df["longitude"] = pd.to_numeric(df["longitude"])
    df["magnitude"] = pd.to_numeric(df["magnitude"])
    df["depth"] = pd.to_numeric(df["depth"])

    # Harita merkezini belirle
    merkez_enlem = df["latitude"].mean()
    merkez_boylam = df["longitude"].mean()

    m = folium.Map(location=[merkez_enlem, merkez_boylam], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    # Büyüklüğe göre renk belirleme fonksiyonu
    def rengi_getir(mag):
        if mag < 3.0:
            return "green"
        elif 3.0 <= mag < 4.5:
            return "orange"
        else:
            return "red"

    # Haritaya noktaları ekleme
    for idx, row in df.iterrows():
        popup_icerik = f"""
        <b>Yer:</b> {row.get('location', 'Bilinmiyor')}<br>
        <b>Büyüklük:</b> {row['magnitude']} ({row.get('type', 'M')})<br>
        <b>Derinlik:</b> {row['depth']} km<br>
        <b>Tarih:</b> {row.get('date', '')}<br>
        <b>Enlem/Boylam:</b> {row['latitude']}, {row['longitude']}
        """

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(row["magnitude"] * 2.5, 3),  # Büyüklüğe göre halka boyutu
            popup=folium.Popup(popup_icerik, max_width=250),
            color=rengi_getir(row["magnitude"]),
            fill=True,
            fill_color=rengi_getir(row["magnitude"]),
            fill_opacity=0.6,
        ).add_to(marker_cluster)

    m.save(cikti_dosyasi)
    print(
        f"Toplam {len(df)} deprem listelendi. Harita '{cikti_dosyasi}' olarak kaydedildi."
    )


# Kullanım Örneği
if __name__ == "__main__":
    afad_deprem_haritasi(
        start="2024-01-01 00:00:00",
        end="2024-12-31 23:59:59",
        minlat=39.0,
        maxlat=41.0,
        minlon=32.0,
        maxlon=34.0,
        minmag=2.5,
        maxmag=7.0,
        mindepth=0.0,
        maxdepth=50.0,
        cikti_dosyasi="ankara_cevre_depremleri.html",
    )