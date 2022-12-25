def give_records(event_id, person_time, records_table):
    records = records_table[(records_table['eventId']==event_id) & (records_table["best"]>person_time)]
    records = records.sort_values("best", inplace=False)
    return records