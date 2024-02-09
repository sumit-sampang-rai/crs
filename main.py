import warnings
from datetime import timedelta

warnings.simplefilter(action="ignore", category=FutureWarning)

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

with st.sidebar:
    min_datetime = df["draw_date"].min().to_pydatetime()
    max_datetime = df["draw_date"].max().to_pydatetime()

    date_filter = st.slider(
        "Date filter:",
        min_value=min_datetime,
        max_value=max_datetime,
        value=(
            (min_datetime.replace(year=max_datetime.year - 2)),
            max_datetime
        ),
        format="YYYY-MM-DD"
    )

legend = dict(
    orientation="h",
    yanchor="bottom",
    y=1,
    xanchor="right",
    x=1
)

fig_df = df.copy()

fig_df = fig_df[
    (df["draw_date"] >= date_filter[0]) &
    (df["draw_date"] <= date_filter[1])
]

backlog_tab, type_tab, type_group_tab = st.tabs([
    "Backlog",
    "Round Type",
    "Round Type Group"
])

with backlog_tab:
    backlog_df = pd.melt(
        fig_df,
        id_vars="draw_date",
        var_name="range",
        value_name="candidates",
        value_vars=[
            "0_300",
            "301_350",
            "351_400",
            "401_410",
            "411_420",
            "421_430",
            "431_440",
            "441_450",
            "451_460",
            "461_470",
            "471_480",
            "481_490",
            "491_500",
            "501_600",
            "601_1200",
        ]
    )

    fig = px.area(backlog_df, x="draw_date", y="candidates", color="range")
    fig.update_layout(legend=legend, legend_title_text=None)

    for i in range(11):
        fig.data[i].update(visible="legendonly")

    st.plotly_chart(fig, use_container_width=True)

with type_tab:
    fig = px.line(fig_df, x="draw_date", y="draw_crs", color="draw_name")
    fig.update_layout(legend=legend, legend_title_text=None)

    st.plotly_chart(fig, use_container_width=True)

    agg_draw_name_df = fig_df.copy()
    agg_draw_name_df["draw_year_month"] = agg_draw_name_df["draw_date"].dt.strftime("%Y-%b")
    agg_draw_name_df = agg_draw_name_df.groupby(
        [
            "draw_year_month",
            "draw_name",
        ],
        sort=False,
    )["draw_size"].sum().reset_index().sort_index(ascending=False).reset_index()

    fig = px.bar(agg_draw_name_df, x="draw_year_month", y="draw_size", color="draw_name")
    fig.update_layout(legend=legend, legend_title_text=None)
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, use_container_width=True)

with type_group_tab:
    fig = px.line(fig_df, x="draw_date", y="draw_crs", color="draw_name_full")
    fig.update_layout(legend=legend, legend_title_text=None)

    st.plotly_chart(fig, use_container_width=True)

    agg_draw_name_full_df = fig_df.copy()
    agg_draw_name_full_df["draw_year_month"] = agg_draw_name_full_df["draw_date"].dt.strftime("%Y-%b")
    agg_draw_name_full_df = agg_draw_name_full_df.groupby(
        [
            "draw_year_month",
            "draw_name_full",
        ],
        sort=False,
    )["draw_size"].sum().reset_index().sort_index(ascending=False).reset_index()

    fig = px.bar(agg_draw_name_full_df, x="draw_year_month", y="draw_size", color="draw_name_full")
    fig.update_layout(legend=legend, legend_title_text=None)
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, use_container_width=True)
