import mdf_iter
import canedge_browser

import pandas as pd
from datetime import datetime, timezone
from utils import setup_fs, load_dbc_files, restructure_data, add_custom_sig, ProcessData, test_signal_threshold
from pytz import timezone
import time
import botocore
import boto3

dbc_paths = ["dbc_files\honda_civic_hatchback_ex_2017_can_generated.dbc"]

eastern = timezone('US/Eastern')

start = datetime(year=2020, month=1, day=1, hour=0, tzinfo=eastern)
stop = datetime(year=2030, month=1, day=1, hour=0, tzinfo=eastern)

pw = {"default": "password"} #what is this

key = 'AKIAZQ3DN62NOBB44GP3'
secretkey = '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'
endpoint = 'http://s3.us-east-2.amazonaws.com'
region = 'us-east-2'
bucket_name = 'honda-civic-bucket'

def list_mf4_files(key, secretkey, endpoint, region, bucket_name):
    # Initialize the S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=key,
        aws_secret_access_key=secretkey,
        endpoint_url=endpoint,
        region_name=region
    )

    # List all objects in the bucket
    response = s3.list_objects_v2(Bucket=bucket_name)

    # Extract the file names of all MF4 files
    mf4_files = []
    for obj in response.get('Contents', []):
        if obj['Key'].endswith('.MF4'):
            mf4_files.append(bucket_name + '/' + obj['Key'])

    return mf4_files


db_list = load_dbc_files(dbc_paths)
fs = setup_fs(s3=True, key=key, secret=secretkey, endpoint=endpoint, region=region, passwords=pw)

while True:

    #log_files = canedge_browser.get_log_files(fs, "honda-civic-bucket/B535198E", start_date=start, stop_date=stop, passwords=pw)

    log_files = list_mf4_files(key, secretkey, endpoint, region, bucket_name)

    print(log_files)

    # for file in log_files:
    #     print(file)
    # print(f"Found a total of {len(log_files)} log files")

    proc = ProcessData(fs, db_list, signals=[])
    df_phys_all = []
    for log_file in log_files:
        df_raw, device_id = proc.get_raw_data(log_file, passwords=pw)
        df_phys = proc.extract_phys(df_raw)
        #proc.print_log_summary(device_id, log_file, df_phys)
        df_phys_all.append(df_phys)

    df_phys_all = pd.concat(df_phys_all, ignore_index=False).sort_index()

    df_phys_join = restructure_data(df_phys=df_phys_all, res="1S")
    df_phys_join.to_csv("output_joined.csv")
    print("\nConcatenated DBC decoded data:\n", df_phys_join)
        
    time.sleep(1)

