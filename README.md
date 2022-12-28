# WCA National Records checker
Checks in which country you could have a National Record (NR) in speedcubing
# Architecture
This application is split into 2:
- an fastAPI that can either return the potential NR for a specific time in a given event or give you all the potential NR based on your current official times using a WCA profile ID
- a simple front-end based on streamlit that calls the above API and displays the result for each options

Everything is hosted on Google Cloud has such:
- ***Google Could Run:*** hosts the API and the front end as serverless. Each program is deployed in its own Docker. 
- ***Google Cloud Storage:*** the information required for the API is hosted on a specific bucket
- ***Google Functions:*** A lambda function that checks if the database on the WCA website was updated and if yes, downloads the new version and process it to store the needed information for the API on Cloud Storage bucket
- ***Google Scheduler:*** A cron job executed every 2 days that triggers the above Lambda function.

# API
The API can be found at this address: https://wca-nr-api-jhaooholda-ue.a.run.app/docs

The API is coded in Python using fastAPI package.
It has 2 endpoints:
- `/get_nr_countries`: It takes an input in the following format:   
```python
{
  "event": str, # from the list of events in the DB ["222", "333", "333bf", "333fm", "333ft", "333oh", "444", "444bf", "555", "555bf", "666", "777", "clock", "magic", "minx", "mmagic", "pyram", "skewb", "sq1"]
  "record_time": int, # time in ms
  "record_type": str # "single" or "average"
}
```

It returns the information in the following format:
```python
dict: {"database_date": str, "result": List[Dict()] } 
    # In "result", each dict is a record from a country you would beat with the given time, with the below format.
    # The list is sorted from lowest to highest "best" time.
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
```
- `/personal_perf?person_id={person_id}`: it takes a WCA profile ID as an input (str) and returns the result in the following format:
```python
dict: {"database_date": str, "result": List[Dict()] } 
    # In "result", each dictionary represents an event with the personal record of the person from WCA DB
    # It also includes a field "potential_nrs" which is the list of countries in which the person's best would
    # grant him a NR (in the format described above in the previous endpoint)
{
                    "event": event,
                    "time_type": "average",
                    "personal_best": result["average"]["best"],
                    "potential_nrs": List[Dict()]
                }
```
# Front end
The front end can be found here: https://wca-nr-front-jhaooholda-ue.a.run.app/  
It features 2 pages, one for each way of calling the API.

# Potential new features
- [ ] The same features but for Continental Records
- [ ] Document and refactor the code
- [ ] Replace the DB currently stored as CSV file by an actual DB (hosted on Google Cloud) based on the amount of data it should not have a visible impact on performance though


# WCA database from World Cubing association  
All the Data used for this project comes from the WCA database.  

## Some information on the Database structure and data
https://www.worldcubeassociation.org/results/misc/export.html
## API url to get latest update and download link
https://www.worldcubeassociation.org/api/v0/export/public
