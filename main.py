import pandas as pd
import requests
import streamlit as st


API_URL = "https://www.canada.ca/content/dam/ircc/documents/json/ee_rounds_123_en.json"

COLUMNS = {
    "drawNumber": {"rename": "draw_number", "dtype": "str"},
    "drawNumberURL": {"rename": "draw_number_url", "dtype": "str"},
    "drawDateTime": {"rename": "draw_datetime", "dtype": "str"},
    "drawCutOff": {"rename": "draw_cut_off", "dtype": "str"},
    "drawName": {"rename": "draw_name", "dtype": "str"},
    "drawSize": {"rename": "draw_size", "dtype": "int"},
    "drawCRS": {"rename": "draw_crs", "dtype": "int"},
    "dd1": {"rename": "601_1200", "dtype": "int"},
    "dd2": {"rename": "501_600", "dtype": "int"},
    # "dd3": {"rename": "451_500", "dtype": "int"},
    "dd4": {"rename": "491_500", "dtype": "int"},
    "dd5": {"rename": "481_490", "dtype": "int"},
    "dd6": {"rename": "471_480", "dtype": "int"},
    "dd7": {"rename": "461_470", "dtype": "int"},
    "dd8": {"rename": "451_460", "dtype": "int"},
    # "dd9": {"rename": "401_450", "dtype": "int"},
    "dd10": {"rename": "441_450", "dtype": "int"},
    "dd11": {"rename": "431_440", "dtype": "int"},
    "dd12": {"rename": "421_430", "dtype": "int"},
    "dd13": {"rename": "411_420", "dtype": "int"},
    "dd14": {"rename": "401_410", "dtype": "int"},
    "dd15": {"rename": "351_400", "dtype": "int"},
    "dd16": {"rename": "301_350", "dtype": "int"},
    "dd17": {"rename": "0_300", "dtype": "int"},
    "dd18": {"rename": "total", "dtype": "int"},
}


@st.cache_data
def cache_score_api():
    return requests.get(API_URL).json()

df = pd.DataFrame(
    cache_score_api()["rounds"],
)

for column, detail in COLUMNS.items():
    if detail["dtype"] == "int":
        df[column] = df[column].replace(",", "", regex=True)

df = df.astype({k: v["dtype"] for k, v in COLUMNS.items()})

df = df.filter(
    items=COLUMNS.keys()
).rename(
    columns={k: v["rename"] for k, v in COLUMNS.items()}
)

df
