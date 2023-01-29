def extract_mdf_start_stop_time(mdf):
    from datetime import timedelta

    # function to identify start/stop timestamp of concatenated log file
    session_start = mdf.header.start_time
    df_raw_asam = mdf.to_dataframe()    
    delta_seconds_start = df_raw_asam.index[0]
    delta_seconds_stop = df_raw_asam.index[-1]
    mdf_start = session_start + timedelta(seconds=delta_seconds_start)
    mdf_stop = session_start + timedelta(seconds=delta_seconds_stop)

    return mdf_start, mdf_stop

def hour_rounder(t):
    from datetime import timedelta

    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))
