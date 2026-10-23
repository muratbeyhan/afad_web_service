import streamlit as st
import pandas as pd
import plotly.express as px
import math
import requests
import traceback
import os
from datetime import datetime, time
import folium
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

st.set_page_config(page_title="Turkey Earthquakes - AFAD Live", layout="wide")

# ---------------------------------------------------------
# 1. STATE INITIALIZATION
# ---------------------------------------------------------
if "deprem_df" not in st.session_state:
    st.session_state["deprem_df"] = None
if "map_center" not in st.session_state:
    st.session_state["map_center"] = [39.0, 35.0]
if "map_zoom" not in st.session_state:
    st.session_state["map_zoom"] = 6
if "live_bounds" not in st.session_state:
    st.session_state["live_bounds"] = {
        "min_lat": 35.0,
        "max_lat": 43.0,
        "min_lon": 25.0,
        "max_lon": 45.0,
    }

def get_mapbox_key():
    try:
        if os.path.exists(os.path.expanduser("~/.streamlit/secrets.toml")) or os.path.exists(".streamlit/secrets.toml"):
            return st.secrets.get("MAPBOX_API_KEY", None)
    except Exception:
        pass
    return os.getenv("MAPBOX_API_KEY", None)

def fmt_num(val):
    f_val = float(val)
    if f_val.is_integer():
        return str(int(f_val))
    return str(round(f_val, 2))

def fmt_num1(val):
    # Eğer değer string formatında ve içinde virgül varsa noktaya çevir
    if isinstance(val, str):
        val = val.replace(',', '.')
    
    f_val = float(val)
    
    # Python float-to-string dönüşümleri her zaman nokta (.) kullanır
    if f_val.is_integer():
        return str(int(f_val))
    
    # Ondalıklı sayılarda gereksiz sıfırları temizleyerek nokta formatında döndürür
    return f"{f_val:.2f}".rstrip('0').rstrip('.')

def afad_verilerini_getir(params):
    base_url = "https://deprem.afad.gov.tr/apiv2/event/filter"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        
        # --- GEÇİCİ DEBUG BİLGİSİ ---
        st.write(f"🔍 API Durum Kodu: {response.status_code}")
        st.write(f"🔍 Gelen Ham Yanıt Uzunluğu: {len(response.text)}")
        if len(response.text) < 200:
            st.write(f"🔍 Gelen Yanıt İçeriği: {response.text}")
        # ---------------------------

        if response.status_code == 200:
            res_data = response.json()
            if isinstance(res_data, list):
                return res_data, None, None
            return [], "API beklenmeyen bir format döndürdü.", str(res_data)
        else:
            return None, f"HTTP Hata Kodu: {response.status_code}", response.text
    except Exception as e:
        return None, f"Bağlantı/İstek Hatası: {str(e)}", traceback.format_exc()

def afad_verilerini_getir1(params):
    base_url = "https://deprem.afad.gov.tr/apiv2/event/filter"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            if isinstance(res_data, list):
                return res_data, None, None
            return [], "API beklenmeyen bir format döndürdü (liste değil).", str(res_data)
        else:
            return None, f"HTTP Hata Kodu: {response.status_code}", response.text
    except Exception as e:
        return None, f"Bağlantı/İstek Hatası: {str(e)}", traceback.format_exc()

# ---------------------------------------------------------
# 2. SIDEBAR PARAMETERS & API TRIGGER
# ---------------------------------------------------------
with st.sidebar:
    st.subheader('🗺️ Map Appearance')
    mapbox_key = get_mapbox_key()
    available_layers = ["OpenStreetMap", "Satellite"]
    if mapbox_key:
        available_layers.append("Mapbox Streets")
    selected_base_layer = st.selectbox("Base Map Style", options=available_layers, index=0)

    st.subheader('🔍 Filter Parameters')
    
    area_selection_mode = st.radio(
        "📍 Spatial Bounds Source",
        options=["Map Canvas (Interactive Zoom)", "Manual Coordinate Input"],
        index=0,
    )

    st.subheader('📅 Time Range')
    col_d1, col_d2 = st.columns(2)
    start_date = col_d1.date_input('Start Date', datetime(2026, 1, 1), min_value=datetime(1900, 1, 1))
    end_date = col_d2.date_input('End Date', datetime.now().date())
    
    col_t1, col_t2 = st.columns(2)
    start_time = col_t1.time_input('Start Time', time(0, 0))
    end_time = col_t2.time_input('End Time', time(23, 59))

    start_str = f"{start_date.strftime('%Y-%m-%d')} {start_time.strftime('%H:%M:%S')}"
    end_str = f"{end_date.strftime('%Y-%m-%d')} {end_time.strftime('%H:%M:%S')}"
    
    if area_selection_mode == "Manual Coordinate Input":
        st.subheader('📍 Latitude & Longitude')
        col_lat1, col_lat2 = st.columns(2)
        min_lat = col_lat1.number_input('Min Latitude', value=36.0, min_value=33.0, max_value=44.0, step=0.01)
        max_lat = col_lat2.number_input('Max Latitude', value=42.0, min_value=33.0, max_value=44.0, step=0.01)

        col_lon1, col_lon2 = st.columns(2)
        min_lon = col_lon1.number_input('Min Longitude', value=26.0, min_value=23.0, max_value=46.0, step=0.01)
        max_lon = col_lon2.number_input('Max Longitude', value=45.0, min_value=23.0, max_value=46.0, step=0.01)

    st.subheader('📊 Magnitude & Depth')
    min_mag = st.number_input('Minimum Magnitude', min_value=0.0, max_value=10.0, value=3.0, step=0.1)
    max_mag = st.number_input('Maximum Magnitude', min_value=0.0, max_value=10.0, value=9.0, step=0.1)
    min_depth, max_depth = st.slider('Depth (km)', min_value=0.0, max_value=100.0, value=(0.0, 50.0), step=0.1)

    if st.button('Fetch Earthquakes from AFAD', type='primary'):
        if area_selection_mode == "Manual Coordinate Input":
            calc_min_lat, calc_max_lat = float(min_lat), float(max_lat)
            calc_min_lon, calc_max_lon = float(min_lon), float(max_lon)
            st.session_state["map_center"] = [(calc_min_lat + calc_max_lat) / 2.0, (calc_min_lon + calc_max_lon) / 2.0]
        else:
            bounds_dict = st.session_state["live_bounds"]
            calc_min_lat = bounds_dict["min_lat"]
            calc_max_lat = bounds_dict["max_lat"]
            calc_min_lon = bounds_dict["min_lon"]
            calc_max_lon = bounds_dict["max_lon"]

        params = {
            "start": start_str,
            "end": end_str,
            "minlat": fmt_num(calc_min_lat),
            "maxlat": fmt_num(calc_max_lat),
            "minlon": fmt_num(calc_min_lon),
            "maxlon": fmt_num(calc_max_lon),
            "minmag": fmt_num(min_mag),
            "maxmag": fmt_num(max_mag),
            "mindepth": fmt_num(min_depth),
            "maxdepth": fmt_num(max_depth),
        }
        
        with st.spinner(f"Fetching data from AFAD Web Service... ({area_selection_mode})"):
            raw_data, error_summary, error_details = afad_verilerini_getir(params)
            
        if error_summary:
            st.error(f"❌ {error_summary}")
            if error_details:
                st.code(error_details)
            st.session_state["deprem_df"] = None
        elif raw_data is not None:
            if len(raw_data) == 0:
                st.warning("⚠️ No earthquakes found for the selected criteria.")
                st.session_state["deprem_df"] = None
            else:
                df_fetched = pd.DataFrame(raw_data)
                if "date" in df_fetched.columns:
                    df_fetched['Date'] = df_fetched['date']
                for col in ["latitude", "longitude", "magnitude", "depth"]:
                    if col in df_fetched.columns:
                        df_fetched[col] = pd.to_numeric(df_fetched[col], errors='coerce')
                
                df_fetched = df_fetched.dropna(subset=["latitude", "longitude"])
                df_fetched['DateOnly'] = df_fetched['Date'].str.split('T').str[0]
                df_fetched['DateOnly'] = pd.to_datetime(df_fetched['DateOnly'], errors='coerce')
                
                st.session_state["deprem_df"] = df_fetched
                st.success(f"✅ {len(df_fetched)} earthquakes fetched successfully!")

# Main UI Title
st.title('🌋 AFAD Earthquake Data Search and Mapping')

df = st.session_state["deprem_df"]

if df is not None and not df.empty:
    filtered_df = df.copy()

    # --- METRICS FRAME (Üst Özet Bilgi Kartları) ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Earthquakes", len(filtered_df))
    
    max_m = filtered_df['magnitude'].max() if 'magnitude' in filtered_df.columns else 0.0
    c2.metric("Maximum Magnitude", f"{max_m:.1f} M")
    
    avg_d = filtered_df['depth'].mean() if 'depth' in filtered_df.columns else 0.0
    c3.metric("Average Depth", f"{avg_d:.1f} km")
    
    st.markdown("---")

    earthquake_count = filtered_df.groupby('DateOnly').size()
    deprem_df = pd.DataFrame({'DateOnly': earthquake_count.index, 'count_eq': earthquake_count.values})

    tab1, tab_mag, tab2, tab3, tab4 = st.tabs([
        "Map", 
        "📊 Mag Stats", 
        "🗃 Num. of EQs", 
        "🗃 Filtered Data", 
        "📈 Chart"
    ])

    mag_ranges = [
        ("0.0-2.9", 0.0, 3.0, "#a0aec0"),
        ("3.0-3.9", 3.0, 4.0, "#ecc94b"),
        ("4.0-4.9", 4.0, 5.0, "#ed8936"),
        ("5.0-5.9", 5.0, 6.0, "#dd6b20"),
        ("6.0-6.9", 6.0, 7.0, "#e53e3e"),
        ("7.0-7.9", 7.0, 8.0, "#805ad5"),
        ("8.0-8.9", 8.0, 9.0, "#742a2a"),
        ("9.0<", 9.0, float('inf'), "#1a202c")
    ]

    # --- TAB 1: FOLIUM MAP ONLY ---
    with tab1:
        st.subheader("Earthquake Map")
        
        m = folium.Map(
            location=st.session_state["map_center"],
            zoom_start=st.session_state["map_zoom"],
            tiles=None,
        )

        if selected_base_layer == "OpenStreetMap":
            folium.TileLayer(tiles="OpenStreetMap", name="OpenStreetMap", control=False).add_to(m)
        elif selected_base_layer == "Satellite":
            folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr='Tiles &copy; Esri | Sources: Esri, Maxar, Earthstar Geographics',
                name="Satellite",
                control=False,
                max_zoom=19,
            ).add_to(m)
        elif selected_base_layer == "Mapbox Streets" and mapbox_key:
            folium.TileLayer(
                tiles=f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_key}",
                attr="Mapbox © OpenStreetMap",
                name="Mapbox Streets",
                control=False,
            ).add_to(m)

        for label, min_val, max_val, color in mag_ranges:
            subset = filtered_df[(filtered_df['magnitude'] >= min_val) & (filtered_df['magnitude'] < max_val)]
            if not subset.empty:
                fg = folium.FeatureGroup(name=f"Magnitude: {label} ({len(subset)})")
                for _, row in subset.iterrows():
                    popup_html = f"""
                    <b>Location:</b> {row.get('location', 'Unknown')}<br>
                    <b>Magnitude:</b> {row.get('magnitude', '-')}<br>
                    <b>Depth:</b> {row.get('depth', '-')} km<br>
                    <b>Date:</b> {row.get('date', '')}
                    """
                    
                    mag_val = row.get('magnitude', 3.0)
                    if pd.isnull(mag_val):
                        mag_val = 3.0
                    marker_radius = max(float(mag_val) * 1.8, 2.0)

                    folium.CircleMarker(
                        location=[row["latitude"], row["longitude"]],
                        radius=marker_radius,
                        popup=folium.Popup(popup_html, max_width=200),
                        tooltip=f"M {row.get('magnitude', '-')}",
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.75,
                    ).add_to(fg)
                fg.add_to(m)

        folium.LayerControl(collapsed=False).add_to(m)

        legend_html = """
        {% macro html(this, kwargs) %}
        <div style="position: fixed; bottom: 20px; right: 20px; z-index:9999; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 6px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2); color: #111;">
            <h5 style="margin:0 0 6px 0">Magnitude (M)</h5>
            <div style="font-size:11px; line-height:18px;">
                <div><i style="background:#a0aec0; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i>0.0 - 2.9</div>
                <div><i style="background:#ecc94b; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i>3.0 - 3.9</div>
                <div><i style="background:#ed8936; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i>4.0 - 4.9</div>
                <div><i style="background:#dd6b20; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i>5.0 - 5.9</div>
                <div><i style="background:#e53e3e; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i>6.0 - 6.9</div>
                <div><i style="background:#805ad5; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i>7.0 - 7.9</div>
                <div><i style="background:#742a2a; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i>8.0 - 8.9</div>
                <div><i style="background:#1a202c; width:14px; height:14px; display:inline-block; margin-right:8px; vertical-align:middle;"></i>9.0&lt; </div>
            </div>
        </div>
        {% endmacro %}
        """
        macro = MacroElement()
        macro._template = Template(legend_html)
        m.get_root().add_child(macro)

        map_data = st_folium(
            m,
            width="100%",
            height=650,
            returned_objects=["bounds", "center", "zoom"],
        )

        if map_data and isinstance(map_data, dict):
            b = map_data.get("bounds")
            if b and isinstance(b, dict):
                sw = b.get("_southWest", {})
                ne = b.get("_northEast", {})
                if sw.get("lat") is not None and ne.get("lat") is not None:
                    st.session_state["live_bounds"] = {
                        "min_lat": float(sw["lat"]),
                        "max_lat": float(ne["lat"]),
                        "min_lon": float(sw["lng"]),
                        "max_lon": float(ne["lng"]),
                    }
            if map_data.get("center") and isinstance(map_data["center"], dict):
                c_lat = map_data["center"].get("lat")
                c_lng = map_data["center"].get("lng")
                if c_lat is not None and c_lng is not None:
                    st.session_state["map_center"] = [float(c_lat), float(c_lng)]
            if map_data.get("zoom") is not None:
                st.session_state["map_zoom"] = map_data["zoom"]

    # --- TAB MAG: MAGNITUDE DISTRIBUTION CHART ---
    with tab_mag:
        st.subheader("Earthquake Count by Magnitude Range")
        
        min_round = math.ceil(min_mag)
        max_round = math.floor(max_mag)
        magnitude_ranges = []
        
        if min_round >= max_round + 1 or max_mag < min_round:
            magnitude_ranges.append((min_mag, max_mag))
        else:
            current_mag = math.ceil(min_mag)  
            next_mag = min(current_mag + 1, math.floor(max_mag))  
            if min_mag < min_round:
                magnitude_ranges.append((min_mag, min_round))
            magnitude_ranges.append((current_mag, next_mag))
            while next_mag < math.floor(max_mag):  
                current_mag = next_mag
                next_mag = min(current_mag + 1, math.floor(max_mag))
                magnitude_ranges.append((current_mag, next_mag))
            magnitude_ranges.append((math.floor(max_mag), max_mag))

        chart_data_list = []
        color_discrete_map = {}

        for mn, mx in magnitude_ranges:
            range_label = f"{mn:.1f}<=Mag<{mx:.1f}"
            count_val = filtered_df[(filtered_df['magnitude'] >= mn) & (filtered_df['magnitude'] < mx)].shape[0]
            
            mid_val = (mn + mx) / 2
            if mid_val < 3.0:
                c = "#a0aec0"
            elif mid_val < 4.0:
                c = "#ecc94b"
            elif mid_val < 5.0:
                c = "#ed8936"
            elif mid_val < 6.0:
                c = "#dd6b20"
            elif mid_val < 7.0:
                c = "#e53e3e"
            elif mid_val < 8.0:
                c = "#805ad5"
            elif mid_val < 9.0:
                c = "#742a2a"
            else:
                c = "#1a202c"

            chart_data_list.append({"Magnitude Range": range_label, "Count": count_val})
            color_discrete_map[range_label] = c

        magnitude_df = pd.DataFrame(chart_data_list)

        fig_bar = px.bar(
            magnitude_df, 
            x='Magnitude Range', 
            y='Count', 
            text='Count', 
            color='Magnitude Range',
            color_discrete_map=color_discrete_map,
            height=550
        )
        fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
        fig_bar.update_layout(xaxis_tickangle=0, showlegend=False)
        fig_bar.update_yaxes(type="log")

        st.plotly_chart(fig_bar, use_container_width=True)

    # --- TAB 2: NUMBER OF EARTHQUAKES ---
    with tab2:
        st.subheader("Number of Earthquake")
        st.write(deprem_df)

    # --- TAB 3: FILTERED DATA ---
    with tab3:
        st.subheader("Filtered Data")
        st.write(filtered_df)

    # --- TAB 4: CHART ---
    with tab4:
        st.subheader("Chart")
        st.bar_chart(deprem_df.set_index('DateOnly'))

else:
    st.info("👈 Use the sidebar filters and click 'Fetch Earthquakes from AFAD' to load live data into the dashboard.")