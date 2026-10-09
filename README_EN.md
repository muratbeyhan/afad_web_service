# AFAD Web Service — Earthquake Data Dashboard

This repository contains a Streamlit application designed to fetch, visualize, and analyze earthquake data via web service endpoints provided by AFAD (Disaster and Emergency Management Authority of Turkey).

The application uses AFAD's public API (`https://deprem.afad.gov.tr/apiv2/event/filter`) to perform dynamic earthquake searches based on time, depth, magnitude, and spatial parameters.

## 🚀 Key Features

- **Dual Spatial Bounds Source:**
  - **Map Canvas (Interactive Zoom):** Automatically detects the live viewport bounds of the map as you zoom or pan, fetching earthquakes strictly within the currently displayed area.
  - **Manual Coordinate Input:** Allows users to manually specify latitude (`Min/Max Lat`) and longitude (`Min/Max Lon`) ranges from the sidebar.
- **AFAD API & .NET Compatibility:** Formats numeric values (`fmt_num`) and timestamps (`YYYY-MM-DD HH:MM:SS`) to adhere strictly to AFAD's `.NET` backend requirements, preventing `HTTP 500 Internal Server Error` and `FormatException` issues.
- **State & Viewport Persistence:** Powered by `st_folium` and Streamlit session state (`st.session_state`), ensuring that map zoom levels and pan centers do not reset unexpectedly upon button clicks or user interaction.
- **Interactive Folium Map:** Custom `CircleMarker` elements color-coded and scaled according to earthquake magnitudes, featuring pop-up detail cards (location, magnitude, depth, date/time).
- **Multi-Layer Base Maps:** OpenStreetMap and Esri World Imagery (Satellite) are included by default. Mapbox Streets layer is dynamically enabled if a valid `MAPBOX_API_KEY` is provided.
- **Comprehensive Error Logging:** Surface API errors, connectivity issues, or unexpected data payloads directly in the Streamlit UI with `st.error`/`st.warning` boxes and collapsible debug technical panels.
- **Charts and Analytics:** Built-in summary metrics (Total Earthquakes, Max Magnitude, Average Depth), an Altair magnitude distribution bar chart, and an expandable raw data table.

## 🛠️ How It Works / Architecture

1. **Spatial Mode Selection:** The user selects the spatial query mode ("Map Canvas" or "Manual Coordinate Input").
2. **Filtering Parameters:** Date/time intervals, magnitude, and depth ranges are configured in the sidebar.
3. **Data Retrieval:** Clicking the "Get Earthquakes" button formats the parameters and dispatches a GET request to the AFAD API endpoint.
4. **Data Processing:** The returned JSON array is converted into a pandas DataFrame, parsed into numeric datatypes (`pd.to_numeric`), cleaned of invalid coordinates, and stored in `st.session_state["deprem_df"]`.
5. **Visualization:** Earthquake events are rendered on the Folium map alongside metric tiles, an Altair chart, and a pandas DataFrame view.

## Mapbox API key (optional)

Mapbox support is optional. To enable Mapbox Streets as a base layer, provide `MAPBOX_API_KEY` either as:

- a Streamlit secret named `MAPBOX_API_KEY`, or
- an environment variable: `export MAPBOX_API_KEY=your_key_here`

If no key is provided, the app falls back to OpenStreetMap and Satellite layers without Mapbox.

## Running locally

1. Create and activate a Python environment (Conda or venv), then install dependencies from `requirements.txt`.

```bash
conda create -n geo python=3.10 -y
conda activate geo
pip install -r requirements.txt
```

2. Run the app:

```bash
streamlit run app.py
```

3. Open your browser at `http://localhost:8501`.

## Deployment

This project can be deployed on Streamlit Community Cloud. If using Mapbox, add `MAPBOX_API_KEY` to the app's Secrets in the Streamlit dashboard.

## Repository structure

- `app.py` — main Streamlit app
- `README.md` — Turkish description
- `README_EN.md` — English description (this file)
- `requirements.txt` — runtime dependencies (Streamlit, folium, pandas, requests, altair, streamlit-folium, branca)

## Contributing

Contributions are welcome. Please open an issue for feature requests or bug reports, and submit pull requests for changes.

## License

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

## Disclaimer

AFAD provides the underlying data and this application visualizes those public datasets. This project is for data exploration and visualization only and is not intended for operational decision-making in emergency situations.
