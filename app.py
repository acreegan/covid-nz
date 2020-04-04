import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
import numpy as np
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

johnsURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
mohURL = "https://www.health.govt.nz/our-work/diseases-and-conditions/covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases"

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "COVID-19 Cases NZ"

server = app.server

def getData():
    # Get Johns Hopkins Data
    try:
        df = pd.read_csv(johnsURL)
        df = df.T
        df.columns = df.loc["Country/Region"].values
        df = df.drop(df.index[0:4])
        df = df.groupby(df.columns,axis=1).sum()
        df.index = pd.to_datetime(df.index)
    except Exception as e:
        print("Error getting data from Johns Hopkins Github:", e)

    # Check Ministry of Health website for latest number
    try:
        mohHTML = urlopen(mohURL).read().decode('utf-8')
        soup = BeautifulSoup(mohHTML,'html.parser')
        if soup.find("table", class_="table-style-two").find_all("td")[6].string == 'Number of confirmed and probable cases':
            numCases = np.int64(soup.find("table", class_="table-style-two").find_all("td")[7].string)
            dateString = soup.find("p", class_="page_updated").find("span", class_="date").string
            mohDate = pd.to_datetime(datetime.strptime(dateString, "%d %B %Y").replace(hour=0, minute=0, second=0, microsecond=0))
            if mohDate>df.index[-1]:
                latest = pd.DataFrame(columns=df.columns, index=[mohDate])
                latest["New Zealand"].iloc[-1] = numCases
                df = pd.concat([df, latest])
    except Exception as e:
        print("Error geting data from MOH website:", e)

    return df

dataSourceText = "Data sources: [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19), " \
                 "[NZ Ministry of Health](https://www.health.govt.nz/our-work/diseases-and-conditions/" \
                 "covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases)"




def createLayout():
    df = getData()

    return html.Div(children=[

        html.H1(children="As of %s there are %d confirmed cases of COVID-19 in New Zealand" %
                         (df.index[-1].strftime("%d %B %Y"),df["New Zealand"].iloc[-1]),
                style={'textAlign': 'center'}),

        dcc.Graph(
            id='covid_graph'
        ),

        dcc.Checklist(
            id="show_all_checkbox",
            options=[
                {"label":"Show All Countries", "value":"All"}
            ]
        ),

        dcc.Markdown(children=dataSourceText, style={"textAlign":"center"}),

        html.Div(id='data_store', style={'display': 'none'}, children=[df.to_json()])
    ])


app.layout = createLayout

@app.callback(
    Output("covid_graph","figure"),
    [Input("show_all_checkbox","value"), Input("data_store", "children")]
)
def update_graph(value, children):
    df = pd.read_json(children[0])
    countryList = ["New Zealand"]
    if value is not None and len(value)>0 and value[0] == "All":
        countryList = df.columns.values

    return {
                'data': [
                    dict(
                        x=df.index,
                        y=df[i],
                        name=i
                    ) for i in df[countryList].columns
                ],
                'layout': dict(
                    xaxis={'title': 'Time'},
                    yaxis={'title': 'Confirmed cases'},
                    margin={'l': 100, 'b': 100, 't': 30, 'r': 100},
                    hovermode='closest',
                    title="Confirmed cases of COVID-19 in New Zealand over time"
                )
            }



if __name__ == '__main__':
    app.run_server(debug=True)