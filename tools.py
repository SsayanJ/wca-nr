import pandas as pd
import os

def load_data(folder_path):
    ranks_avg = pd.read_csv(os.path.join(folder_path,"WCA_export_RanksAverage.tsv"), sep="\t")
    ranks_single = pd.read_csv(os.path.join(folder_path,"WCA_export_RanksAverage.tsv"), sep="\t")
    persons = pd.read_csv(os.path.join(folder_path,"WCA_export_Persons.tsv"), sep="\t")
    return ranks_avg, ranks_single, persons

def decode_mbd_time(input_time):
    str_input = str(input_time)
    # The 0 at the beginning may not be stored so it may need to be adapted.
    # No multi blind data in the database so I cannot confirm
    if str_input[0] == "0":
        difference = 99-int(str_input[1:3])
        time_in_s = int(str_input[3:8])
        hours = time_in_s // 3600
        minutes = time_in_s % 3600 // 60
        seconds = time_in_s % 3600 % 60
        missed = int(str_input[8:])
        solved = difference + missed
        attempted = solved + missed
    return attempted, solved, time_in_s, hours, minutes, seconds

def wca_statistics_time_format(time_input, event, time_type='single'):
    
    if time_input == -1:
        return "DNF"
    elif time_input == -2:
        return "DNS"
    # this may happen on big cubes where there are no mean value or no value4 or value5
    # should not happen on this application
    elif time_input == 0:
        return 'no_value'
    elif event == '333fm' & time_type == 'single':
        return time_input
    elif event == '333mbf':
        return decode_mbd_time(time_input)
    else:
        return time_input/100