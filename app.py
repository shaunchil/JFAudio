import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import urllib.parse

# Function to fetch all data from the database
def fetch_all_data():
    conn = sqlite3.connect('metadata.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Language, Artist, Title, Target_Country, World_Speakers, Blob_URL FROM metadata")
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=["Language", "Artist", "Title", "Target Country", "World Speakers", "Blob URL"])
    return df

# Function to filter data by partial matches in language and country
def search_data(language=None, country=None):
    df = fetch_all_data()

    # Apply case-insensitive partial matching for language
    if language:
        language = language.strip()
        df = df[df['Language'].str.contains(language, case=False, na=False, regex=True)]

    # Apply case-insensitive partial matching for country
    if country:
        country = country.strip()
        df = df[df['Target Country'].str.contains(country, case=False, na=False, regex=True)]

    return df

# Streamlit app layout
st.title("The JESUS Film Audio - Recording Database")

# Load and crop the image
image_url = "https://static.wixstatic.com/media/5384c5_466ad5c2c19e47a58e1cfc3a444c1b4f~mv2.jpeg/v1/fill/w_750,h_519,al_c,q_85/JesusFilm.jpeg"
response = requests.get(image_url)
img = Image.open(BytesIO(response.content))
width, height = img.size
crop_top, crop_bottom = int(height * 0.1), int(height * 0.9)
cropped_img = img.crop((0, crop_top, width, crop_bottom))
st.image(cropped_img, use_column_width=True)

# Initialize session state
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = set()
if 'search_results' not in st.session_state:
    st.session_state.search_results = pd.DataFrame()

###Streamlit App
# Search by language and country inputs, trigger search on Enter
language = st.text_input("Search by Language (partial words allowed)", key="language_input")
country = st.text_input("Search by Country (partial words allowed)", key="country_input")

# Perform search if either field is not empty
if language or country:
    st.session_state.search_results = search_data(language, country)

# Display search results if available
if not st.session_state.search_results.empty:
    st.write(f"Found {len(st.session_state.search_results)} record(s): Select files to download:")
    for i, row in st.session_state.search_results.iterrows():
        file_url = row['Blob URL']
        encoded_url = urllib.parse.quote(file_url, safe=':/')
        checkbox_label = f"{row['Title']} ({row['Language']}, {row['Target Country']})"
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

# Message to prompt search
else:
    st.write("Enter search terms above to display data.")
