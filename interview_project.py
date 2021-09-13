import os
import pandas as pd
import requests
import numpy
import matplotlib.pyplot as plt
from dotenv import load_dotenv, find_dotenv


def req(series: str):
    payload = {'series_id': series}
    path_to_dotenv = find_dotenv(filename=".bash_profile")
    load_dotenv(path_to_dotenv)
    apikey = os.environ.get("FRED_api_key", None)
    payload["api_key"] = apikey
    payload["file_type"] = "json"
    r = requests.get("https://api.stlouisfed.org/fred/series/observations?", params=payload)
    return r.json()


def create_df(series: str):
    df = pd.json_normalize(req(series), record_path="observations")
    df.drop(["realtime_start", "realtime_end"], axis=1, inplace=True)
    df.set_index("date", inplace=True)
    df.index = pd.to_datetime(df.index)
    df = df.loc[df.index.year > 1999]
    df = df.loc[df.index.year < 2021]
    df = df.loc[df.index.month % 3 == 1]
    df.value = df.value.astype(numpy.float64)
    return df


nonfarm_employment_df = create_df('PAYEMS')
real_gdp_df = create_df('GDPC1')
cpi_df = create_df('CPIAUCSL')


temp_df = pd.merge(nonfarm_employment_df, real_gdp_df, on="date")
all_data_df = pd.merge(temp_df, cpi_df, on="date")

all_data_df.columns = ['nonfarm_emp', 'real_gdp', 'cpi']

#all_data_df.to_csv('FRED_interview_data.csv')
all_data_df.plot(kind='line')

