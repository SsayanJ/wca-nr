import streamlit as st
import pandas as pd
import requests


def potential_nr_from_profile(person_id):
    # response = requests.post(f"http://127.0.0.1:8000/personal_perf?person_id={person_id}").json()
    response = requests.post(f"https://wca-nr-api-jhaooholda-ue.a.run.app/personal_perf?person_id={person_id}").json()
    if "error" in response:
        return "error", response["error"]
    return response["database_date"], response["potential_nr_list"]


st.set_page_config("WCA Profile", page_icon="images/rubik.png")
st.sidebar.markdown("Use WCA Profile")
st.title("Use your WCA profile")

person_id = st.text_input("Enter your WCA profile ID (ie: Max Park - 2012PARK03)")

if st.button("Launch"):
    database_date, potential_nr_list = potential_nr_from_profile(person_id)
    if database_date == "error":
        st.write(f"### {potential_nr_list}")
    else:
        st.write(f"### Latest update from WCA database: {database_date}")
        for event in potential_nr_list:
            if isinstance(event["potential_nrs"], str):
                st.write(event["potential_nrs"])
            # check that the result is not empty
            elif event["potential_nrs"]:
                result_df = pd.DataFrame.from_dict(event["potential_nrs"])[
                    ["personId", "name", "gender", "best", "countryId", "eventId"]
                ].set_index("personId")
                st.write(
                    f"With your best official {event['time_type']} in"
                    f" {event['event']} ({event['personal_best']/100 if event['event']!='333fm' else event['personal_best']}{'s' if event['event']!='333fm' else ' moves'}),"
                    " you could get a NR in the following countries:"
                )
                st.dataframe(result_df, width=800, height=170)
            else:
                st.write(
                    f"With your best official {event['time_type']} in"
                    f" {event['event']} ({event['personal_best']/100 if event['event']!='333fm' else event['personal_best']}{'s' if event['event']!='333fm' else ' moves'}),"
                    "you cannot beat any existing National Records but you may try a country where the record wasn't set yet"
                )
