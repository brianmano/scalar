import mdf_iter
import canedge_browser

import pandas as pd
from datetime import datetime, timezone
from utils import setup_fs, load_dbc_files, restructure_data, add_custom_sig, ProcessData, test_signal_threshold, list_mf4_files
from pytz import timezone
import time
import botocore
import boto3

dbc_paths = ["dbc_files\can1-honda_civic_hatchback_ex_2017_can_generated.dbc"]

eastern = timezone('US/Eastern')

start = datetime(year=2024, month=1, day=1, hour=0, tzinfo=eastern)
stop = datetime(year=2024, month=6, day=1, hour=0, tzinfo=eastern)

pw = {"default": "password"} #what is this

key = 'AKIAZQ3DN62NOBB44GP3'
secretkey = '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'
endpoint = 'http://s3.us-east-2.amazonaws.com'
region = 'us-east-2'
bucket_name = 'honda-civic-bucket'

# Maintain a list of processed log files
processed_files = set()

loop_start_time = time.time()

db_list = load_dbc_files(dbc_paths)
print(db_list)
fs = setup_fs(key=key, secret=secretkey, endpoint=endpoint, region=region)

loop_end_time = time.time()  
loop_duration = loop_end_time - loop_start_time
print(f"Time taken for initialization: {loop_duration} seconds")

while True:
    loop_start_time = time.time()  # Record the start time of the loop

    log_files = list_mf4_files(key, secretkey, endpoint, region, bucket_name)

    # Filter out already processed files
    new_files = [log_file for log_file in log_files if log_file not in processed_files]

    if new_files:
        print("New log files found:", new_files)

        proc = ProcessData(fs, db_list, signals=[])

        df_phys_all = []
        for log_file in new_files:
            loop_end_time = time.time()  
            loop_duration = loop_end_time - loop_start_time
            print(f"Time taken for 1.75: {loop_duration} seconds")

            df_raw, device_id = proc.get_raw_data(log_file) #1.4 / 2.73 seconds

            loop_end_time = time.time()  
            loop_duration = loop_end_time - loop_start_time  
            print(f"Time taken for 1.8: {loop_duration} seconds")

            df_phys = proc.extract_phys(df_raw) #0.8 / 2.73 seconds

            loop_end_time = time.time()
            loop_duration = loop_end_time - loop_start_time  
            print(f"Time taken for 1.9: {loop_duration} seconds")
            df_phys_all.append(df_phys)

        df_phys_all = pd.concat(df_phys_all, ignore_index=False).sort_index()

        df_phys_join = restructure_data(df_phys=df_phys_all, res="1S")
        df_phys_join.to_csv("output_joined.csv")
        # print("\nConcatenated DBC decoded data:\n", df_phys_join)

        # Update the set of processed files
        processed_files.update(new_files)
    else:
        print("No new log files found.")
        # print("\nConcatenated DBC decoded data:\n", df_phys_join)

    loop_end_time = time.time()  
    loop_duration = loop_end_time - loop_start_time  
    print(f"Time taken for whole thing: {loop_duration} seconds")

