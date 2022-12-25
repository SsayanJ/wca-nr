"""
Note: you need to run the app from the root folder otherwise the data will not be found
- To run the app
$ uvicorn wca_nr_api:app --reload
  -Inputs: dict?
  -Outputs: List[Dict()]: each dict is a record from a country you would beat with the given time, with this format:
            # TODO simplify the output by removing duplicates and useless info
            {
                "id": "2015HARR01",
                "subid": 1,
                "name": "Ryan Pin Harry",
                "countryId": "Mauritius",
                "gender": "m",
                "personId": "2015HARR01",
                "eventId": "333",
                "best": 1019,
                "worldRank": 3640,
                "continentRank": 19,
                "countryRank": 1
            },
"""

from tools import create_record_table, load_data
import pandas as pd
from pydantic import BaseModel
from wca_nr import give_records
from fastapi import FastAPI

app = FastAPI()

class RecordInput(BaseModel):
    event: str
    record_time: float
    record_type: str

# TODO replace this by a check if the data exists and load the file already processed
ranks_avg, ranks_single, persons = load_data("WCA_export") 
records_table_single = create_record_table(ranks_single, persons)
records_table_avg = create_record_table(ranks_avg, persons)

@app.get('/')
async def root():
    return {"message": "FastAPI to know in which country you could have a WCA National Record"}

@app.post('/get_nr_countries')
async def get_nr_countries(record_input: RecordInput):
    record_input = record_input.dict()
    if record_input["record_type"].lower() == "single":
        result_table = give_records(record_input["event"], record_input["record_time"], records_table=records_table_single)
        return result_table.to_dict("records")
    elif record_input["record_type"].lower() == "average":
        result_table = give_records(record_input["event"], record_input["record_time"], records_table=records_table_avg)
        return result_table.to_dict("records")
    return {"Error": "The type of record must be single or average"}