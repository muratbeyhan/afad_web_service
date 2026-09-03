import os
from datetime import datetime, time
import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium
from branca.element import Template, MacroElement
import altair as alt

st.set_page_config(page_title="AFAD Earthquake Analysis Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        color: #e5e7eb;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    h1 {
        color: #f8fafc !important;
        font-size: 2.2rem !important;
        margin-bottom: 0.7rem !important;
    }
    [data-testid="stSidebar"] {
        background: #0b1120;
        border-right: 1px solid rgba(148, 163, 184, 0.2);
    }
    .stSidebar .stSelectbox, .stSidebar .stDateInput, .stSidebar .stNumberInput, .stSidebar .stSlider, .stSidebar .stTimeInput {
        background: rgba(15, 23, 42, 0.65);
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        color: #f8fafc !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 12px;
        padding: 0.9rem 1rem;
    }
    .stExpander {
        background: rgba(15, 23, 42, 0.72);
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.2);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.25);
    }
    .stButton > button {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.2rem;
        font-weight: 700;
        box-shadow: 0 10px 24px rgba(239, 68, 68, 0.25);
    }
    .stButton > button:hover {
        filter: brightness(1.05);
    }
    .stDataFrame {
        background: rgba(15, 23, 42, 0.7);
        border-radius: 12px;
    }
    iframe {
        border-radius: 14px !important;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌋 AFAD Earthquake Data Search and Mapping")

if "deprem_df" not in st.session_state:
    st.session_state["deprem_df"] = None


def get_mapbox_key():
    try:
        key = st.secrets.get("MAPBOX_API_KEY")
    except Exception:
        key = None
    if not key:
        key = os.getenv("MAPBOX_API_KEY")
    return key


# --- SIDEBAR (FILTERS) ---
st.sidebar.header("🔍 Filter Parameters")

st.sidebar.subheader("📅 Time Range")
col_d1, col_d2 = st.sidebar.columns(2)
start_date = col_d1.date_input("Start Date", datetime(2024, 1, 1))
end_date = col_d2.date_input("End Date", datetime.now().date())

col_t1, col_t2 = st.sidebar.columns(2)
start_time = col_t1.time_input("Start Time", time(0, 0))
end_time = col_t2.time_input("End Time", time(23, 59))

start_str = (
    f"{start_date.strftime('%Y-%m-%d')} {start_time.strftime('%H:%M:%S')}"
)
end_str = f"{end_date.strftime('%Y-%m-%d')} {end_time.strftime('%H:%M:%S')}"

st.sidebar.subheader("📍 Latitude & Longitude")
col_lat1, col_lat2 = st.sidebar.columns(2)
min_lat = col_lat1.number_input(
    "Min Latitude", value=34.0, min_value=33.0, max_value=44.0, step=0.01
)
max_lat = col_lat2.number_input(
    "Max Latitude", value=42.0, min_value=33.0, max_value=44.0, step=0.01
)

col_lon1, col_lon2 = st.sidebar.columns(2)
min_lon = col_lon1.number_input(
    "Min Longitude", value=24.0, min_value=23.0, max_value=46.0, step=0.01
)
max_lon = col_lon2.number_input(
    "Max Longitude", value=45.0, min_value=23.0, max_value=46.0, step=0.01
)

st.sidebar.subheader("📊 Magnitude & Depth")
min_mag, max_mag = st.sidebar.slider(
    "Magnitude (M)",
    min_value=0.0,
    max_value=9.0,
    value=(5.0, 8.0),
    step=0.1,
)
min_depth, max_depth = st.sidebar.slider(
    "Depth (km)",
    min_value=0.0,
    max_value=100.0,
    value=(0.0, 50.0),
    step=0.1,
)


def afad_verilerini_getir(params):
    base_url = "https://deprem.afad.gov.tr/apiv2/event/filter"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ),
        "Accept": "application/json",
    }
    try:
        response = requests.get(
            base_url, params=params, headers=headers, timeout=15
        )
        if response.status_code == 200:
            res_data = response.json()
            if isinstance(res_data, list):
                return res_data, None
            return [], "API returned an unexpected format."
        else:
            return (
                None,
                f"HTTP Error Code: {response.status_code} - Response: {response.text}",
            )
    except Exception as e:
        return None, f"Connection error: {str(e)}"


if st.sidebar.button("Get Earthquakes", type="primary"):
    params = {
        "start": start_str,
        "end": end_str,
        "minlat": str(int(min_lat) if min_lat.is_integer() else min_lat),
        "maxlat": str(int(max_lat) if max_lat.is_integer() else max_lat),
        "minlon": str(int(min_lon) if min_lon.is_integer() else min_lon),
        "maxlon": str(int(max_lon) if max_lon.is_integer() else max_lon),
        "minmag": str(int(min_mag) if min_mag.is_integer() else min_mag),
        "maxmag": str(int(max_mag) if max_mag.is_integer() else max_mag),
        "mindepth": str(int(min_depth) if min_depth.is_integer() else min_depth),
        "maxdepth": str(int(max_depth) if max_depth.is_integer() else max_depth),
    }

    with st.spinner("Fetching earthquake data from AFAD API..."):
        raw_data, error_msg = afad_verilerini_getir(params)

    if error_msg:
        st.error(f"Data retrieval error: {error_msg}")
        st.session_state["deprem_df"] = None
    elif raw_data and len(raw_data) > 0:
        df = pd.DataFrame(raw_data)
        for col in ["latitude", "longitude", "magnitude", "depth"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["latitude", "longitude"])
        st.session_state["deprem_df"] = df
    else:
        st.warning(
            "No earthquake data was found for the selected criteria."
        )
        st.session_state["deprem_df"] = None

df = st.session_state["deprem_df"]

if df is not None and not df.empty:
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Earthquakes", len(df))
    c2.metric("Maximum Magnitude", f"{df['magnitude'].max():.1f} M")
    c3.metric("Average Depth", f"{df['depth'].mean():.1f} km")

    st.markdown("<hr style='border: 1px solid rgba(148,163,184,0.25); margin: 0.8rem 0 1.2rem 0;'>", unsafe_allow_html=True)

    mapbox_key = get_mapbox_key()
    # Initialize map without a default tile to avoid duplicate OpenStreetMap layers
    m = folium.Map(
        location=[df["latitude"].mean(), df["longitude"].mean()],
        zoom_start=6,
        tiles=None,
    )

    # Base layer definitions (no CartoDB entries that require keys)
    base_layers = {
        "OpenStreetMap": folium.TileLayer(
            tiles="OpenStreetMap",
            name="OpenStreetMap",
            control=True,
            show=True,  # default visible layer
        ),
        "Terrain": folium.TileLayer(
            tiles="https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
            attr=(
                'Map tiles by <a href="https://stamen.com">Stamen Design</a>, '
                'under <a href="https://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> | '
                'Map data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            ),
            name="Terrain",
            control=True,
            subdomains="abcd",
            max_zoom=18,
            show=False,
        ),
        "Satellite": folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr=(
                'Tiles &copy; Esri | Sources: Esri, Maxar, Earthstar Geographics, '
                'and the GIS User Community'
            ),
            name="Satellite",
            control=True,
            max_zoom=19,
            show=False,
        ),
    }

    # Optional Mapbox (only added if key present)
    if mapbox_key:
        base_layers["Mapbox Streets"] = folium.TileLayer(
            tiles=(
                "https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}"
                f"?access_token={mapbox_key}"
            ),
            attr="Mapbox © OpenStreetMap",
            name="Mapbox Streets",
            control=True,
            show=False,
        )

    # Add layers to map
    for layer in base_layers.values():
        layer.add_to(m)

    folium.LayerControl(position="topleft").add_to(m)

    def rengi_getir(mag):
        if mag < 3.0:
            return "yellow"
        elif 3.0 <= mag < 4.0:
            return "orange"
        elif 4.0 <= mag < 5.0:  
            return "green"
        elif 5.0 <= mag < 6.0:
            return "blue"
        elif 6.0 <= mag < 7.0:
            return "purple"
        else:
            return "red"

    # DOĞRUDAN HARİTAYA (m) EKLENİYOR
    for _, row in df.iterrows():
        popup_html = f"""
        <b>Location:</b> {row.get('location', 'Unknown')}<br>
        <b>Magnitude:</b> {row.get('magnitude', '-')}<br>
        <b>Depth:</b> {row.get('depth', '-')} km<br>
        <b>Date:</b> {row.get('date', '')}
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(
                (row["magnitude"] if pd.notnull(row["magnitude"]) else 2) * 1.5, 3
            ),
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=str(row.get("magnitude", "-")),
            color=rengi_getir(
                row["magnitude"] if pd.notnull(row["magnitude"]) else 0
            ),
            fill=True,
            fill_color=rengi_getir(
                row["magnitude"] if pd.notnull(row["magnitude"]) else 0
            ),
            fill_opacity=0.7,
        ).add_to(m)
    # Lejant (legend) - Haritanın sağ alt köşesine sabit HTML kutusu ekler (tek seferlik)
    legend_html = """
    {% macro html(this, kwargs) %}
    <div style="position: fixed; bottom: 20px; right: 20px; z-index:9999; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 6px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2); color: #111;">
        <h4 style="margin:0 0 6px 0">Magnitude (M)</h4>
        <div style="font-size:13px; line-height:18px;">
            <div><i style="background:yellow; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i><span style="margin-left:6px;color:#111">&lt; 3.0</span></div>
            <div><i style="background:orange; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i><span style="margin-left:6px;color:#111">3.0 - 3.9</span></div>
            <div><i style="background:green; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i><span style="margin-left:6px;color:#111">4.0 - 4.9</span></div>
            <div><i style="background:blue; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i><span style="margin-left:6px;color:#111">5.0 - 5.9</span></div>
            <div><i style="background:purple; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i><span style="margin-left:6px;color:#111">6.0 - 6.9</span></div>
            <div><i style="background:red; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i><span style="margin-left:6px;color:#111">≥ 7.0</span></div>
        </div>
    </div>
    {% endmacro %}
    """

    macro = MacroElement()
    macro._template = Template(legend_html)
    m.get_root().add_child(macro)

    # Haritayı bir kez render et
    st_folium(m, width="100%", height=500, returned_objects=[])

    with st.expander("📄 Data Table"):
        st.dataframe(df)

    # --- STATISTICAL GRAPH: total number of earthquakes by magnitude range
    mag_bins = [0, 3.0, 4.0, 5.0, 6.0, 7.0, 10.0]
    mag_labels = ["< 3.0", "3.0 - 3.9", "4.0 - 4.9", "5.0 - 5.9", "6.0 - 6.9", "≥ 7.0"]
    mag_series = df['magnitude'].dropna()
    if not mag_series.empty:
        mag_cat = pd.cut(mag_series, bins=mag_bins, labels=mag_labels, right=False)
        counts = mag_cat.value_counts().reindex(mag_labels, fill_value=0)
        counts_df = pd.DataFrame({'range': counts.index.astype(str), 'count': counts.values})

        base = alt.Chart(counts_df).encode(
            x=alt.X('range:N', sort=mag_labels, title='Magnitude Range'),
            y=alt.Y('count:Q', title='Earthquake Count'),
            color=alt.Color('range:N', legend=None)
        )
        bars = base.mark_bar().properties(title='Earthquake Counts by Magnitude Range', width='container', height=300)
        labels = base.mark_text(dy=-10, color='black').encode(text=alt.Text('count:Q'))
        chart = (bars + labels)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info('Not enough magnitude data available for the chart.')
else:
    if st.session_state["deprem_df"] is None:
        st.info("Select a date and region from the left panel and click the button.")