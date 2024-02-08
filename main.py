from datetime import timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(layout="wide")

API_URL = "https://www.canada.ca/content/dam/ircc/documents/json/ee_rounds_123_en.json"

COLUMNS = {
    "drawNumber": {"rename": "draw_number", "cast": {"dtype": "str"}},
    "drawNumberURL": {"rename": "draw_number_url", "cast": {"dtype": "str"}},
    "drawDate": {"rename": "draw_date", "cast": {"dtype": "datetime"}},
    "drawName": {"rename": "draw_name", "cast": {"dtype": "str"}},
    "drawText2": {"rename": "draw_name_full", "cast": {"dtype": "str"}},
    "drawSize": {"rename": "draw_size", "cast": {"dtype": "int"}},
    "drawCRS": {"rename": "draw_crs", "cast": {"dtype": "int"}},
    "dd1": {"rename": "601_1200", "cast": {"dtype": "int"}},
    "dd2": {"rename": "501_600", "cast": {"dtype": "int"}},
    # "dd3": {"rename": "451_500", "cast": {"dtype": "int"}},
    "dd4": {"rename": "491_500", "cast": {"dtype": "int"}},
    "dd5": {"rename": "481_490", "cast": {"dtype": "int"}},
    "dd6": {"rename": "471_480", "cast": {"dtype": "int"}},
    "dd7": {"rename": "461_470", "cast": {"dtype": "int"}},
    "dd8": {"rename": "451_460", "cast": {"dtype": "int"}},
    # "dd9": {"rename": "401_450", "cast": {"dtype": "int"}},
    "dd10": {"rename": "441_450", "cast": {"dtype": "int"}},
    "dd11": {"rename": "431_440", "cast": {"dtype": "int"}},
    "dd12": {"rename": "421_430", "cast": {"dtype": "int"}},
    "dd13": {"rename": "411_420", "cast": {"dtype": "int"}},
    "dd14": {"rename": "401_410", "cast": {"dtype": "int"}},
    "dd15": {"rename": "351_400", "cast": {"dtype": "int"}},
    "dd16": {"rename": "301_350", "cast": {"dtype": "int"}},
    "dd17": {"rename": "0_300", "cast": {"dtype": "int"}},
    "dd18": {"rename": "total", "cast": {"dtype": "int"}},
}


@st.cache_data(ttl="5m")
def cache_score_api():
    return requests.get(API_URL).json()

data = cache_score_api()

# Cleaning
for draw_round in data["rounds"]:
    for column, column_detail in COLUMNS.items():
        if column_detail["cast"]["dtype"] == "int" and isinstance(draw_round[column], str):
            draw_round[column] = draw_round[column].replace(",", "")

# To pandas dataframe
df = pd.DataFrame(
    data["rounds"],
)

# Casting datatypes
df = df.astype({
    k: v["cast"]["dtype"]
    for k, v in COLUMNS.items()
    if v["cast"]["dtype"] not in ["datetime"]
})

for column, column_detail in COLUMNS.items():
    if column_detail["cast"]["dtype"] == "datetime":
        df[column] = pd.to_datetime(df[column])

# Selecting selective columns
df = df.filter(
    items=COLUMNS.keys()
).rename(
    columns={k: v["rename"] for k, v in COLUMNS.items()}
)

min_datetime = df["draw_date"].min().to_pydatetime()
max_datetime = df["draw_date"].max().to_pydatetime()

date_filter = st.slider(
    "Date filter:",
    min_value=min_datetime,
    max_value=max_datetime,
    value=(
        (min_datetime.replace(year=max_datetime.year - 3)),
        max_datetime
    ),
    format="YYYY-MM-DD"
)

fig_df = df[(df['draw_date'] >= date_filter[0]) & (df['draw_date'] <= date_filter[1])]

fig = px.line(fig_df, x="draw_date", y="draw_crs", color="draw_name")

st.plotly_chart(fig, use_container_width=True)

fig = px.line(fig_df, x="draw_date", y="draw_crs", color="draw_name_full")

st.plotly_chart(fig, use_container_width=True)
