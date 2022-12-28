"""
To run the app
$ streamlit run front.py
"""

import streamlit as st
import requests, json
import pandas as pd


def get_records(record_type, record_time, event):
    data_request = {"event": event, "record_time": str(record_time), "record_type": record_type}
    response = requests.post(
        "https://wca-nr-api-jhaooholda-ue.a.run.app/get_nr_countries", data=json.dumps(data_request)
    ).json()
    # response = requests.post("http://127.0.0.1:8000/get_nr_countries", data=json.dumps(data_request)).json()
    if response["result"]:
        result_df = pd.DataFrame.from_dict(response["result"])[
            ["personId", "name", "gender", "best", "countryId", "eventId"]
        ]
    else:
        result_df = (
            f"Sorry, with this time you cannot beat any existing National Records in {event} but you may try a country"
            " where the record wasn't set yet"
        )
    return response["database_date"], result_df


EVENT_LIST = [
    "222",
    "333",
    "333bf",
    "333fm",
    "333ft",
    "333oh",
    "444",
    "444bf",
    "555",
    "555bf",
    "666",
    "777",
    "clock",
    "magic",
    "minx",
    "mmagic",
    "pyram",
    "skewb",
    "sq1",
]

st.set_page_config("WCA NR", page_icon="images/rubik.png")
st.sidebar.markdown("Enter a time for a specific event")
st.title("WCA NR")
record_type = st.radio("Single or Average?", ("Single", "Average"))
record_time = int(
    st.number_input(
        label="What is your record (format in seconds x100, ex: 4.86s -> 486, except FM just put the number of moves)?",
        min_value=0,
        max_value=100_000,
        step=1,
        value=1000,
    )
)
event = st.selectbox("Select the event", EVENT_LIST)

if st.button("Launch"):
    database_date, result_df = get_records(record_type, record_time, event)
    st.write(f"### Latest update from WCA database: {database_date}")
    if isinstance(result_df, str):
        st.write(result_df)
    else:
        st.dataframe(result_df, width=800, height=210)
