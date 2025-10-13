"""
Streamlit page to display a single DataFrame and map from the database.
"""

import pandas as pd
import geopandas as gpd
import streamlit as st
import pydeck as pdk
import json
import lib

# Initialize session state
if 'selected_rows' not in st.session_state:
    st.session_state['selected_rows'] = []

st.title("DataFrame and Map")

# Define geometry processing function (before using it)
@st.cache_data(hash_funcs={pd.DataFrame: lambda df: hash(tuple(df.values.tobytes()))})
def process_geometry(data: pd.DataFrame) -> gpd.GeoDataFrame:
    """Convert GeoJSON features to GeoDataFrame and add row data as JSON."""
    try:
        # Extract all features from geometry column and associate with row data
        features = []
        row_data_list = []
        
        for idx, row in data.iterrows():
            if row['geometry']:
                feature_collection = row['geometry']
                if isinstance(feature_collection, dict):
                    geom_features = feature_collection.get('features', [])
                    features.extend(geom_features)
                    
                    # Create row data dict (exclude geometry column)
                    row_dict = row.drop('geometry').to_dict()
                    # Add this row data for each feature in the geometry
                    row_data_list.extend([row_dict] * len(geom_features))
        
        # Create GeoDataFrame from features
        gdf = gpd.GeoDataFrame.from_features(features, crs=27700)
        gdf = gdf.to_crs(4326)
        
        # Add row_data as JSON string column
        if row_data_list:
            gdf['row_data'] = [json.dumps(data, indent=2) for data in row_data_list]
        
        return gdf
    except Exception as e:
        st.error(f"Error processing geometry: {e}")
        return gpd.GeoDataFrame()

# Load data
table = lib.load_data("select * from public.test_geom limit 1000")

# Check for valid data
if table.empty or "geometry" not in table.columns:
    st.warning("No data available or geometry column missing.")
    st.stop()

# Dataframe with selection (always show full table)
st.subheader("Data Table")
event = st.dataframe(
    table,
    key='table',
    on_select="rerun",
    selection_mode="multi-row",
    use_container_width=True
)

# Update session state from selection
if event.selection and event.selection.get('rows'):
    st.session_state['selected_rows'] = event.selection['rows']
else:
    st.session_state['selected_rows'] = []

# Refresh button
if st.button("Refresh data"):
    lib.load_data.clear()
    process_geometry.clear()  # Clear geometry cache too
    st.session_state['selected_rows'] = []
    st.rerun()


# --- Pydeck Map Section ---
st.subheader("Map View")

# Process geometry
gdf = process_geometry(table)

if not gdf.empty:
    # Calculate map center
    centroid = gdf.geometry.centroid.union_all().centroid
    lat, lon = centroid.y, centroid.x
    
    # Create layers
    layers = []
    
    # Base layer - all data (faded if selection exists)
    base_alpha = 100 if st.session_state['selected_rows'] else 255
    all_geojson = json.loads(gdf.to_json())
    
    base_layer = pdk.Layer(
        "GeoJsonLayer",
        all_geojson,
        pickable=True,
        stroked=True,
        filled=True,
        get_fill_color=f"[200, 30, 0, {base_alpha}]",
        get_line_color=f"[0, 0, 0, {base_alpha}]",
        line_width_min_pixels=1,
    )
    layers.append(base_layer)
    
    # Highlight layer - selected rows only
    if st.session_state['selected_rows']:
        selected_table = table.iloc[st.session_state['selected_rows']]
        selected_gdf = process_geometry(selected_table)
        
        if not selected_gdf.empty:
            selected_geojson = json.loads(selected_gdf.to_json())
            
            highlight_layer = pdk.Layer(
                "GeoJsonLayer",
                selected_geojson,
                pickable=True,
                stroked=True,
                filled=True,
                get_fill_color="[255, 215, 0, 255]",  # Gold highlight
                get_line_color="[255, 0, 0, 255]",      # Red border
                line_width_min_pixels=3,
            )
            layers.append(highlight_layer)
    
    # Render map
    view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=15, pitch=0)
    
    deck = pdk.Deck(
        map_style=None,
        layers=layers,
        initial_view_state=view_state,
        tooltip={"html": "<b>Row Data:</b><br/><pre>{row_data}</pre>", "style": {"backgroundColor": "steelblue", "color": "white"}}
    )
    
    st.pydeck_chart(deck, use_container_width=True)
else:
    st.error("Could not process geometry data.")