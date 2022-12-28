"""
Note: you need to run the app from the root folder otherwise the data will not be found
- To run the app
$ uvicorn wca_nr_api:app --reload
  -Inputs: dict?
  -Outputs: dict:
        {"database_date": str, "result": List[Dict()] } 
        In "result", each dict is a record from a country you would beat with the given time, with the below format.
        The list is sorted from lowest to highest "best" time.
            {
                "personId": "2015HARR01",
                "name": "Ryan Pin Harry",
                "countryId": "Mauritius",
                "gender": "m",
                "eventId": "333",
                "best": 1019,
                "worldRank": 3640,
                "continentRank": 19,
                "countryRank": 1
            },
"""

from time import time
import pandas as pd
from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn, os, json, requests
from google.cloud import storage

FILES_TO_LOAD = {
    "metadata": "metadata.json",
    "records_table_single": "WCA_records_single.csv",
    "records_table_avg": "WCA_records_avg.csv",
}

RECORD_FIELDS = [
    "personId",
    "name",
    "countryId",
    "gender",
    "eventId",
    "best",
    "worldRank",
    "continentRank",
    "countryRank",
]

app = FastAPI()


class RecordInput(BaseModel):
    event: str
    record_time: float
    record_type: str


def give_records(event_id, person_time, records_table, world_rank=-1, time_type="single"):
    if world_rank == 1:
        return f"Congratulations! You hold the World Record of {event_id} {time_type}, you could get the NR anywhere."
    records = records_table[(records_table["eventId"] == event_id) & (records_table["best"] > person_time)]
    records = records.sort_values("best", inplace=False).to_dict("records")
    return records


def initialise_data(FILES_TO_LOAD):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket("wca-nr-db")
    dataset = {}
    for name, filename in FILES_TO_LOAD.items():
        if ".json" in filename:
            blob = bucket.blob(filename)
            dataset[name] = json.loads(blob.download_as_string(client=None))
        elif ".csv" in filename:
            dataset[name] = pd.read_csv("gs://wca-nr-db/" + filename)
        else:
            raise f"Format not managed to load {filename}"
    return dataset


dataset = initialise_data(FILES_TO_LOAD)


@app.get("/")
async def root():
    return {"message": "FastAPI to know in which country you could have a WCA National Record"}


@app.post("/get_nr_countries")
async def get_nr_countries(record_input: RecordInput):
    record_input = record_input.dict()
    if record_input["record_type"].lower() == "single":
        result_table = give_records(
            record_input["event"], record_input["record_time"], records_table=dataset["records_table_single"]
        )
    elif record_input["record_type"].lower() == "average":
        result_table = give_records(
            record_input["event"], record_input["record_time"], records_table=dataset["records_table_avg"]
        )
    else:
        result_table = {"Error": "The type of record must be single or average"}
    response = {"database_date": dataset["metadata"]["export_date"], "result": result_table}
    return response


@app.post("/personal_perf")
async def personal_perf(person_id):
    response = requests.get("https://www.worldcubeassociation.org/api/v0/persons/" + person_id).json()
    if "error" in response:
        return {"error": f"Could not find {person_id} in WCA Database, please check your WCA Profile ID"}
    person_perf = response["personal_records"]
    potential_nr = []
    for event, result in person_perf.items():
        potential_nr.append(
            {
                "event": event,
                "time_type": "single",
                "personal_best": result["single"]["best"],
                "potential_nrs": give_records(
                    event,
                    result["single"]["best"],
                    dataset["records_table_single"],
                    world_rank=result["single"]["world_rank"],
                    time_type="single"
                ),
            }
        )

        if "average" in result.keys():
            potential_nr.append(
                {
                    "event": event,
                    "time_type": "average",
                    "personal_best": result["average"]["best"],
                    "potential_nrs": give_records(
                        event,
                        result["average"]["best"],
                        dataset["records_table_avg"],
                        world_rank=result["average"]["world_rank"],
                        time_type="average"
                    ),
                }
            )

    return {"database_date": dataset["metadata"]["export_date"], "potential_nr_list": potential_nr}


if __name__ == "__main__":
    uvicorn.run(app, port=int(os.environ.get("PORT", 8000)), host="0.0.0.0")
