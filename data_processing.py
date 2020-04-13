import pandas as pd
from datetime import datetime
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen
import locale
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

johnsURLTotal = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
johnsURLDeaths = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
johnsURLRecovered = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
mohURL = "https://www.health.govt.nz/our-work/diseases-and-conditions/covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases"


def getData():
    # Get Johns Hopkins Data
    try:
        df = pd.read_csv(johnsURLTotal)
        df = df.T
        df.columns = df.loc["Country/Region"].values
        df = df.drop(df.index[0:4])
        df = df.groupby(df.columns,axis=1).sum()
        df.index = pd.to_datetime(df.index)

        dfDeaths = pd.read_csv(johnsURLDeaths)
        dfDeaths = dfDeaths.T
        dfDeaths.columns = dfDeaths.loc["Country/Region"].values
        dfDeaths = dfDeaths.drop(dfDeaths.index[0:4])
        dfDeaths = dfDeaths.groupby(dfDeaths.columns, axis=1).sum()
        dfDeaths.index = pd.to_datetime(dfDeaths.index)

        dfRecovered = pd.read_csv(johnsURLRecovered)
        dfRecovered = dfRecovered.T
        dfRecovered.columns = dfRecovered.loc["Country/Region"].values
        dfRecovered = dfRecovered.drop(dfRecovered.index[0:4])
        dfRecovered = dfRecovered.groupby(dfRecovered.columns,axis=1).sum()
        dfRecovered.index = pd.to_datetime(dfRecovered.index)

    except Exception as e:
        print("Error getting data from Johns Hopkins Github:", e)

    # Check Ministry of Health website for latest number
    try:
        mohHTML = urlopen(mohURL).read().decode('utf-8')
        soup = BeautifulSoup(mohHTML,'html.parser')
        if soup.find("table", class_="table-style-two").find_all("tr")[3].find("th").string == 'Number of confirmed and probable cases':
            numCases = np.int64(locale.atoi(soup.find("table", class_="table-style-two").find_all("tr")[3].find_all("td")[0].string))
            dateString = soup.find("p", class_="georgia-italic").string
            mohDate = pd.to_datetime(datetime.strptime(dateString, "Last updated %I.%M %p, %d %B %Y.").replace(hour=0, minute=0, second=0, microsecond=0))
            if mohDate>df.index[-1]:
                latest = pd.DataFrame(columns=df.columns, index=[mohDate])
                latest["New Zealand"].iloc[-1] = numCases
                df = pd.concat([df, latest])
    except Exception as e:
        print("Error geting data from MOH website:", e)



    dfText = df.copy()
    nacols = dfText.columns[dfText.iloc[-1].isna()]
    notnacols = dfText.columns[dfText.iloc[-1].notna()]

    dfText.loc[dfText.index[-1],notnacols] =notnacols
    dfText.loc[dfText.index[:-1], notnacols] = ""

    dfText.loc[dfText.index[-2],nacols] =nacols
    dfText.loc[dfText.index[:-2], nacols] = ""

    dfNew = df - df.shift()


    return df,dfText,dfNew