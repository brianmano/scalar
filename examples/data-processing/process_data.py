import mdf_iter
import canedge_browser

import time
import pandas as pd
from datetime import datetime, timezone
from utils import setup_fs, load_dbc_files, restructure_data, add_custom_sig, ProcessData, test_signal_threshold

start_time = time.time()

# specify devices to process (from local/S3), DBC files, start time and optionally passwords
devices = ["LOG\958D2219"]

dbc_paths = ["dbc_files\can1-honda_civic_hatchback_ex_2017_can_generated.dbc"]

start = datetime(year=2020, month=1, day=1, hour=0, tzinfo=timezone.utc)
stop = datetime(year=2030, month=1, day=1, hour=0, tzinfo=timezone.utc)

pw = {"default": "password"}

# setup filesystem (local/S3), load DBC files and list log files for processing

fs = setup_fs(s3=False, key="", secret="", endpoint="", region="", passwords=pw)
db_list = load_dbc_files(dbc_paths)
print(db_list)
#db list is the dbc (dictionary) values that you need to translate the log with
print("ok")
log_files = canedge_browser.get_log_files(fs, devices, start_date=start, stop_date=stop, passwords=pw)
# log files are based on what device types you chose, log of that device (from a certain time period)
print(log_files)
print(f"Found a total of {len(log_files)} log files")

# --------------------------------------------
# perform data processing of each log file (e.g. evaluation of signal stats vs. thresholds)
proc = ProcessData(fs, db_list, signals=[])
df_phys_all = []

#grabs a combination of both log_files, ending at 198, need to check car to see what kinda files we can pull in 
for log_file in log_files:
    df_raw, device_id = proc.get_raw_data(log_file, passwords=pw)
    df_phys = proc.extract_phys(df_raw)
    proc.print_log_summary(device_id, log_file, df_phys)

    df_phys_all.append(df_phys)

df_phys_all = pd.concat(df_phys_all,ignore_index=False).sort_index()

df_phys_join = restructure_data(df_phys=df_phys_all, res="1S")
df_phys_join.to_csv("output_joined.csv")
# print("\nConcatenated DBC decoded data:\n", df_phys_join)

# print("--- %s seconds ---" % (time.time() - start_time))
