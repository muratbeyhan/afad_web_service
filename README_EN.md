# AFAD Web Service — Earthquake Data Dashboard

This repository contains a Streamlit dashboard application developed to fetch and visualize earthquake event data provided by AFAD (Disaster and Emergency Management Authority of Turkey). The app retrieves data from AFAD's public API and offers users an interactive interface for filtering, mapping, and exploring earthquake events.

## Key features

- Fetch earthquake events from AFAD's API for a specified date/time and geographic bounding box
- Filter by latitude/longitude, date/time range, magnitude, and depth
- Interactive Folium map with one `CircleMarker` per earthquake, scaled by magnitude
- Base-layer selector: OpenStreetMap and Satellite (Esri World Imagery). Optional Mapbox support if you provide a Mapbox API key
- Magnitude legend on the map
- Altair charts showing magnitude distribution and a data table for details
- English UI with a dark, polished theme

## How it works / Architecture

1. The user selects a date/time range, geographic bounding box (min/max lat/lon), magnitude range, and depth range in the left sidebar.
2. Clicking the "Get Earthquakes" button calls AFAD's filter endpoint: `https://deprem.afad.gov.tr/apiv2/event/filter` with the selected parameters.
3. Returned JSON is converted to a pandas DataFrame; numeric columns are coerced and invalid rows are dropped.
4. Each earthquake is plotted on a Folium map with a popup showing location, magnitude, depth, and date.
5. The user can switch the map base layer between OpenStreetMap and Satellite. If a `MAPBOX_API_KEY` is provided via environment variable or Streamlit secrets, Mapbox Streets appears as an additional option.

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

This repository does not include a license file by default. If you plan to open-source it, consider adding an MIT or other permissive license.

## Disclaimer

AFAD provides the underlying data and this application visualizes those public datasets. This project is for data exploration and visualization only and is not intended for operational decision-making in emergency situations.
