import mdf_iter
import canedge_browser

import pandas as pd
from datetime import datetime, timezone
from utils import setup_fs, load_dbc_files, restructure_data, add_custom_sig, ProcessData, test_signal_threshold

# specify devices to process (from local/S3), DBC files, start time and optionally passwords
#devices = ["LOG/958D2219"]

dbc_paths = ["dbc_files\honda_civic_hatchback_ex_2017_can_generated.dbc"]
#dbc_paths = ["dbc_files\CSS-Electronics-SAE-J1939-DEMO.dbc"]

start = datetime(year=2020, month=1, day=1, hour=0, tzinfo=timezone.utc)
stop = datetime(year=2030, month=1, day=1, hour=0, tzinfo=timezone.utc)

pw = {"default": "password"} #what is this

# setup filesystem (local/S3), load DBC files and list log files for processing

fs = setup_fs(s3=True, key="AKIAZQ3DN62NOBB44GP3", secret="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", endpoint="http://s3.us-east-2.amazonaws.com", region="us-east-2", passwords=pw)
print(fs)
db_list = load_dbc_files(dbc_paths)
print(db_list)
#db list is the dbc (dictionary) values that you need to translate the log with
print("ok")
log_files = canedge_browser.get_log_files(fs, "honda-civic-bucket/B535198E", start_date=start, stop_date=stop, passwords=pw)
# log files are based on what device types you chose, log of that device (from a certain time period)
print(log_files)
print(f"Found a total of {len(log_files)} log files")

# --------------------------------------------
# perform data processing of each log file (e.g. evaluation of signal stats vs. thresholds)
proc = ProcessData(fs, db_list, signals=[])
#print(proc)
df_phys_all = []

#grabs a combination of both log_files, ending at 198, need to check car to see what kinda files we can pull in 
for log_file in log_files:
    df_raw, device_id = proc.get_raw_data(log_file, passwords=pw)
    df_phys = proc.extract_phys(df_raw)
    proc.print_log_summary(device_id, log_file, df_phys)

    # test_signal_threshold(df_phys=df_phys, signal="EngineSpeed", threshold=800)

    df_phys_all.append(df_phys)

df_phys_all = pd.concat(df_phys_all,ignore_index=False).sort_index()


print("done")

# --------------------------------------------
# example: Add a custom signal
# def ratio(s1, s2):
#     return s2 / s1 if s1 else np.nan

# df_phys_all = add_custom_sig(df_phys_all, "WheelBasedVehicleSpeed", "EngineSpeed", ratio, "RatioRpmSpeed")

# --------------------------------------------
# example: resample and restructure data (parameters in columns)

#grabs average of each second to put into .csv file (i calculated it to double check)
#everything is correct except the time is off, think its just a time zone difference
df_phys_join = restructure_data(df_phys=df_phys_all, res="1S")
df_phys_join.to_csv("output_joined.csv")
print("\nConcatenated DBC decoded data:\n", df_phys_join)
