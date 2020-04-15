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
        cases = pd.read_csv(johnsURLTotal)
        cases = cases.T
        cases.columns = cases.loc["Country/Region"].values
        cases = cases.drop(cases.index[0:4])
        cases = cases.groupby(cases.columns,axis=1).sum()
        cases.index = pd.to_datetime(cases.index)

        deaths = pd.read_csv(johnsURLDeaths)
        deaths = deaths.T
        deaths.columns = deaths.loc["Country/Region"].values
        deaths = deaths.drop(deaths.index[0:4])
        deaths = deaths.groupby(deaths.columns, axis=1).sum()
        deaths.index = pd.to_datetime(deaths.index)

        recovered = pd.read_csv(johnsURLRecovered)
        recovered = recovered.T
        recovered.columns = recovered.loc["Country/Region"].values
        recovered = recovered.drop(recovered.index[0:4])
        recovered = recovered.groupby(recovered.columns,axis=1).sum()
        recovered.index = pd.to_datetime(recovered.index)

    except Exception as e:
        print("Error getting data from Johns Hopkins Github:", e)

    # Check Ministry of Health website for latest total and concat with df.
    try:
        mohHTML = urlopen(mohURL).read().decode('utf-8')
        soup = BeautifulSoup(mohHTML,'html.parser')
        if soup.find("table", class_="table-style-two").find_all("tr")[3].find("th").string == 'Number of confirmed and probable cases':
            numCases = np.int64(locale.atoi(soup.find("table", class_="table-style-two").find_all("tr")[3].find_all("td")[0].string))
            dateString = soup.find("p", class_="georgia-italic").string
            mohDate = pd.to_datetime(datetime.strptime(dateString, "Last updated %I.%M %p, %d %B %Y.").replace(hour=0, minute=0, second=0, microsecond=0))
            if mohDate>cases.index[-1]:
                latest = pd.DataFrame(columns=cases.columns, index=[mohDate])
                latest["New Zealand"].iloc[-1] = numCases
                cases = pd.concat([cases, latest])
    except Exception as e:
        print("Error geting data from MOH website:", e)


    # Create text for graph. Name of country at the end, the rest blank
    casesText = createTextForGraph(cases)

    # Create text for deaths (can be different as we don't get extra data for NZ deaths yet)
    deathsText = createTextForGraph(deaths)

    # Calculate daily new
    casesNew = cases - cases.shift()
    deathsNew = deaths - deaths.shift()

    return cases,casesText,casesNew,deaths, deathsText, deathsNew


# Create text for graph. Name of country at the end, the rest blank
def createTextForGraph(df):
    dfText = df.copy()
    nacols = dfText.columns[dfText.iloc[-1].isna()]
    notnacols = dfText.columns[dfText.iloc[-1].notna()]

    dfText.loc[dfText.index[-1], notnacols] = notnacols
    dfText.loc[dfText.index[:-1], notnacols] = ""

    dfText.loc[dfText.index[-2], nacols] = nacols
    dfText.loc[dfText.index[:-2], nacols] = ""

    return dfText