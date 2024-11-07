import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import urllib.parse

# URL for the image
image_url = "https://static.wixstatic.com/media/5384c5_466ad5c2c19e47a58e1cfc3a444c1b4f~mv2.jpeg/v1/fill/w_750,h_519,al_c,q_85/JesusFilm.jpeg"

# Function to load and cache the cropped image
@st.cache_resource
def load_cropped_image():
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    width, height = img.size
    crop_top, crop_bottom = int(height * 0.1), int(height * 0.9)
    cropped_img = img.crop((0, crop_top, width, crop_bottom))
    return cropped_img

# Optimized function to fetch data based on search filters
def fetch_data_filtered(language=None, country=None):
    conn = sqlite3.connect('metadata.db')
    query = "SELECT Language, Artist, Title, Target_Country, World_Speakers, Blob_URL FROM metadata WHERE 1=1"
    params = []

    # Filter by language if provided
    if language:
        query += " AND Language LIKE ?"
        params.append(f"%{language}%")
    
    # Filter by country if provided
    if country:
        query += " AND Target_Country LIKE ?"
        params.append(f"%{country}%")

    # Read only the filtered data into a DataFrame
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Streamlit app layout
st.title("The JESUS Film Audio - Recording Database")

# Display the cropped image
cropped_img = load_cropped_image()
st.image(cropped_img, use_container_width=True)

# Initialize session state
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = set()
if 'search_results' not in st.session_state:
    st.session_state.search_results = pd.DataFrame()

# Function to search data by language and country
def search_data(language=None, country=None):
    df = fetch_data_filtered(language, country)
    return df

# Search by language and country inputs
language = st.text_input("Search by Language (partial words allowed)", key="language_input")
country = st.text_input("Search by Country (partial words allowed)", key="country_input")

# Perform search if either field is not empty
if language or country:
    st.session_state.search_results = search_data(language, country)

# Display search results if available
if not st.session_state.search_results.empty:
    st.write(f"Found {len(st.session_state.search_results)} record(s): Select files to download:")
    for i, row in st.session_state.search_results.iterrows():
        file_url = row['Blob_URL']
        encoded_url = urllib.parse.quote(file_url, safe=':/')
        checkbox_label = f"{row['Title']} ({row['Language']}, {row['Target_Country']})"
        if st.checkbox(checkbox_label, key=encoded_url, value=encoded_url in st.session_state.selected_files):
            st.session_state.selected_files.add(encoded_url)
        else:
            st.session_state.selected_files.discard(encoded_url)

    if st.session_state.selected_files:
        st.write("Selected files:")
        for url in st.session_state.selected_files:
            st.write(url)
        if st.button("Download Selected Files"):
            for file_url in st.session_state.selected_files:
                st.write(f"[Download {file_url.split('/')[-1]}]({file_url})")
            st.success("Download links ready!")
    else:
        st.write("No files selected for download.")
else:
    st.write("Enter search terms above to display data.")
