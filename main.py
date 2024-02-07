import pandas as pd
import requests
import streamlit as st


API_URL = "https://www.canada.ca/content/dam/ircc/documents/json/ee_rounds_123_en.json"


@st.cache_data
def cache_score_api():
    return requests.get(API_URL).json()

df = pd.DataFrame(cache_score_api()["rounds"])

df
