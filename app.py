import streamlit as st
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import os

# Initialize Geolocator
geolocator = Nominatim(user_agent="event_mapper")

# Function to geocode addresses
def get_coordinates(address):
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return pd.Series([location.latitude, location.longitude])
        return pd.Series([None, None])
    except GeocoderTimedOut:
        return pd.Series([None, None])

# Streamlit Interface
st.title("Event Locations on Map")

# Example DataFrame (you can load this from a CSV or database)
data = {
    'Event Name': ['Event 1', 'Event 2', 'Event 3'],
    'Street': ['123 Main St', '456 Queen St', '789 King St'],
    'City': ['Toronto', 'Toronto', 'Toronto']
}
df = pd.DataFrame(data)

# Apply geocoding to get latitude and longitude
df[['Latitude', 'Longitude']] = df.apply(
    lambda row: get_coordinates(f"{row['Street']}, {row['City']}"), axis=1)

# Filter out rows with missing geolocation data
df_cleaned = df.dropna(subset=['Latitude', 'Longitude'])

# Create a Folium map centered around Toronto
event_map = folium.Map(location=[43.7, -79.4], zoom_start=12)

# Plot each event on the map
for _, row in df_cleaned.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"{row['Event Name']}<br>{row['Street']}, {row['City']}",
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(event_map)

# Save the map to an HTML file
map_path = "/tmp/events_map.html"  # Using /tmp as it's writable in Streamlit Cloud
event_map.save(map_path)

# Display the map in Streamlit
st.write("Here is a map showing the event locations:")
st.markdown(f'<iframe src="{map_path}" width="100%" height="600px"></iframe>', unsafe_allow_html=True)
