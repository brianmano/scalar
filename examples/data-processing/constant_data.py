import mdf_iter
import canedge_browser

import pandas as pd
from datetime import datetime, timezone
from utils import setup_fs, load_dbc_files, restructure_data, add_custom_sig, ProcessData, test_signal_threshold
from pytz import timezone
import time

dbc_paths = ["dbc_files\honda_civic_hatchback_ex_2017_can_generated.dbc"]

eastern = timezone('US/Eastern')

start = datetime(year=2020, month=1, day=1, hour=0, tzinfo=eastern)
stop = datetime(year=2030, month=1, day=1, hour=0, tzinfo=eastern)

pw = {"default": "password"} #what is this

fs = setup_fs(s3=True, key="AKIAZQ3DN62NOBB44GP3", secret="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", endpoint="http://s3.us-east-2.amazonaws.com", region="us-east-2", passwords=pw)
db_list = load_dbc_files(dbc_paths)

while True:
    try:
        log_files = canedge_browser.get_log_files(fs, "honda-civic-bucket/B535198E", start_date=start, stop_date=stop, passwords=pw)
        print(log_files)
        print(f"Found a total of {len(log_files)} log files")

        proc = ProcessData(fs, db_list, signals=[])
        df_phys_all = []
        for log_file in log_files:
            df_raw, device_id = proc.get_raw_data(log_file, passwords=pw)
            df_phys = proc.extract_phys(df_raw)
            proc.print_log_summary(device_id, log_file, df_phys)
            df_phys_all.append(df_phys)

        df_phys_all = pd.concat(df_phys_all, ignore_index=False).sort_index()

        df_phys_join = restructure_data(df_phys=df_phys_all, res="1S")
        df_phys_join.to_csv("output_joined.csv")
        print("\nConcatenated DBC decoded data:\n", df_phys_join)
        
        #time.sleep(1)
    except Exception as e:
        print(f"An error occurred: {e}")
