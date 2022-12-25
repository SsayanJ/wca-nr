"""
To run the app
$ streamlit run front.py
"""

import streamlit as st
import pandas as pd
import requests
import ast
import json

EVENT_LIST = ["333", "333oh", "444"]

st.title("WCA NR")
record_type = st.radio("Single or Average?", ("Single", "Average"))
record_time = int(
    st.number_input(
        label="What is your record (format in seconds x100, ex: 4.86s -> 486)?",
        min_value=0,
        max_value=100_000,
        step=1,
        value=1000,
    )
)
event = st.selectbox("Select the event", EVENT_LIST)

if st.button("Launch"):
    data_request={"event": event, "record_time": record_time, "record_type": record_type}
    records = requests.post(
        "http://127.0.0.1:8000/get_nr_countries", data=json.dumps(data_request))
    json_file = ast.literal_eval(records.text)
    result_df = pd.DataFrame.from_dict(json_file)[["personId", "name", "gender", "best", "countryId", "eventId"]]
    # result_df = result_df.rename(columns={"index": "Patient"}, errors="raise")
    st.write(result_df)

