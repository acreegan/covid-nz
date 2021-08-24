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

johnsURLTotalUS = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
johnsURLDeathsUS = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"

mohURL = "https://www.health.govt.nz/our-work/diseases-and-conditions/covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases"


def getData():
    # Get Johns Hopkins Data
    cases = readJohnsData(johnsURLTotal, "Country/Region", {"US":"USA"})
    deaths = readJohnsData(johnsURLDeaths, "Country/Region", {"US":"USA"})

    casesUS = readJohnsData(johnsURLTotalUS, "Province_State").add_suffix(", USA")
    deathsUS = readJohnsData(johnsURLDeathsUS, "Province_State").add_suffix(", USA")


    # There is no recovered data for US, therefore US data is added after calculating active so US states do not appear in active
    cases = pd.concat([cases, casesUS],axis=1)
    deaths = pd.concat([deaths, deathsUS], axis=1)

    #
    #   Turning this off for now as we are running into inconsistencies due to time zones
    #
    # # Check Ministry of Health website for latest total and concat with df.
    # try:
    #     mohHTML = urlopen(mohURL).read().decode('utf-8')
    #     soup = BeautifulSoup(mohHTML,'html.parser')
    #     if soup.find("table", class_="table-style-two").find_all("tr")[3].find("th").string == 'Number of confirmed and probable cases':
    #         numCases = np.int64(locale.atoi(soup.find("table", class_="table-style-two").find_all("tr")[3].find_all("td")[0].string))
    #         dateString = soup.find("p", class_="georgia-italic").string
    #         mohDate = pd.to_datetime(datetime.strptime(dateString, "Last updated %I.%M %p, %d %B %Y.").replace(hour=0, minute=0, second=0, microsecond=0))
    #         if mohDate>cases.index[-1]:
    #             latest = pd.DataFrame(columns=cases.columns, index=[mohDate])
    #             latest.loc[mohDate,"New Zealand"] = numCases
    #             cases = pd.concat([cases, latest])
    # except Exception as e:
    #     print("Error geting data from MOH website:", e)



    population = pd.read_csv("data/population_data.csv", header=4)
    population = population.T
    population.columns = population.loc["Country Name"].values
    population.drop(population.index[0])

    us_pop = pd.read_csv("data/us_states_population.csv", header=1)
    us_pop = us_pop.T
    us_pop.columns = us_pop.loc["NAME"].values
    us_pop.drop(us_pop.index[0])
    us_pop = us_pop.add_suffix(", USA")

    population = pd.concat([population,us_pop],axis=1)


    # Create text for graph. Name of country at the end, the rest blank
    # Also Create text for other dataframes (can be different as we don't get extra data for NZ deaths yet)
    casesText = createTextForGraph(cases)
    deathsText = createTextForGraph(deaths)


    # Calculate daily new
    casesNew = cases - cases.shift()
    deathsNew = deaths - deaths.shift()


    return cases,casesText,casesNew,deaths, deathsText, deathsNew, population


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


def readJohnsData(url, grouping_column, replacement_columns=None):
    try:
        df = pd.read_csv(url)
    except Exception as e:
        print("Error getting data from Johns Hopkins Github:", e)
        exit(1)

    df = df.T
    df.columns = df.loc[grouping_column].values
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df.loc[df.index.dropna()]
    df = df.groupby(df.columns, axis=1).sum()

    if replacement_columns is not None:
        df.rename(columns=replacement_columns,inplace=True)

    return df
