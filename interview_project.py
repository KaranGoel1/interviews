import os
import pandas as pd
import requests
import numpy
from dotenv import load_dotenv, find_dotenv

#To make the program, I searched up various things on google and the pandas documentation, however I did not directly
#copy any code from anywhere. I looked at a few examples here and there to see how certain methods are used, and
#appropriately implemented it into my own code. I have put links next to code based on online examples, otherwise my
#only resource was the pandas documentation.

def req(series: str):
    payload = {'series_id': series} #loading in the id from which the data is to be collected
    path_to_dotenv = find_dotenv(filename=".bash_profile") #found on dotenv documentation
    #environment variables are in a bash_profile file so navigating to the file to pull api key
    load_dotenv(path_to_dotenv) #loading the variable into the code
    apikey = os.environ.get("FRED_api_key", None) #getting the api key from the variable
    payload["api_key"] = apikey #preparing the API request by loading the key into the request
    payload["file_type"] = "json" #making sure a json format of data is given
    r = requests.get("https://api.stlouisfed.org/fred/series/observations?", params=payload)
    #requesting data using the loaded features
    return r.json() #returning the response as a json formatted data structure


def create_df(series: str): #function converts json into a normalised df structure for use later
    df = pd.json_normalize(req(series), record_path="observations")
    #examples from: https://towardsdatascience.com/all-pandas-json-normalize-you-should-know-for-flattening-json-13eae1dfb7dd
    #dataframe created by converting the observations list of dictionaries into a dataframe
    df.drop(["realtime_start", "realtime_end"], axis=1, inplace=True) #drop the columns which show when the data was requested
    df.set_index("date", inplace=True) #sets the index of the dataframe to the dates so plots and merging is easier down the road
    df.index = pd.to_datetime(df.index) #converting the date index to datetime to access year month date
    df = df.loc[df.index.year > 1999] #screening for data 2000 onwards
    df = df.loc[df.index.year < 2021] #screening for data before 2021
    df = df.loc[df.index.month % 3 == 1] #adjusting all the months to match the quarterly data
    df = df.loc[df.index.day == 1] #adjusting dates so that daily data matches up with the others
    df.value = df.value.astype(numpy.float64) #making sure the values of the columns are numeric
    return df

#loading in data into respective dataframes below
nonfarm_employment_df = create_df('PAYEMS')
real_gdp_df = create_df('GDPC1')
cpi_df = create_df('CPIAUCSL')


temp_df = pd.merge(nonfarm_employment_df, real_gdp_df, on="date") #merging the first 2 dfs
all_data_df = pd.merge(temp_df, cpi_df, on="date") #adding the third df

all_data_df.columns = ['nonfarm_emp', 'real_gdp', 'cpi'] #renaming the columns to represent the data

#all_data_df.to_csv('FRED_interview_data.csv') loading df into csv file
all_data_df.plot(kind='line') #creating a line plot of all the data
#plt.savefig('all_data_plot.png')
#saving as pngsavefig() method was found at https://chartio.com/resources/tutorials/how-to-save-a-plot-to-a-file-using-matplotlib/

#creating scatter plot of nonfarm employment and real GDP and saving as png
all_data_df.plot(kind='scatter', x='nonfarm_emp', y='real_gdp')
#plt.savefig('nonfarmemployment_realgdp_plot.png')

#create histogram of CPI and saved as png
all_data_df['cpi'].plot.hist()
#plt.savefig('cpi_hist_plot.png')

#loading data of interest rates into df and renaming column appropriately
interest_rate_df = create_df('DFF')
interest_rate_df.columns = ['interest_rate']

#loading unemployment rate data into df and renaming the column
unemployment_rate_df = create_df('UNRATE')
unemployment_rate_df.columns = ['unemployment_rate']

#merging the two dfs so the scatterplot can be made
rates_df = pd.merge(unemployment_rate_df, interest_rate_df, on="date")

#scatterplot of the rates created and saved as png
rates_df.plot(kind='scatter', x='unemployment_rate', y='interest_rate')
#plt.savefig('rates_plot.png')