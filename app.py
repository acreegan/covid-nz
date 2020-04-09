import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
import numpy as np
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


johnsURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
mohURL = "https://www.health.govt.nz/our-work/diseases-and-conditions/covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases"

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
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
        if soup.find("table", class_="table-style-two").find_all("tr")[3].find("th").string == 'Number of confirmed and probable cases':
            numCases = np.int64(locale.atoi(soup.find("table", class_="table-style-two").find_all("tr")[3].find_all("td")[0].string))
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

    return html.Div(
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
        children=[
            html.Div(id='data_store', style={'display': 'none'}, children=[df.to_json()]),

            html.Div(
                className="row flex-display",
                # style={"margin-bottom": "25px"},
                children = [
                    html.H3(
                        children=locale.format_string(
                            "As of %s there are %d confirmed cases of COVID-19 in New Zealand",
                            (df.index[-1].strftime("%d %B %Y"), df["New Zealand"].iloc[-1]), grouping=True),
                        className="twelve columns",
                        style={"text-align": "center", "margin-top":"0"}),

                ],
            ),

            html.Div(
                className="row flex-display",
                style={"height":"75vh"},
                children=[
                    html.Div(
                        className="pretty_container eight columns",
                        children=[
                            dcc.Graph(id="covid_graph", className="graph")
                        ]
                    ),
                    html.Div(
                        className="pretty_container four columns",
                        children=[
                            html.Div(
                                style={"display":"flex","justify-content":"center","align-items":"center", "flex-wrap":"wrap"},
                                children=[
                                    html.Button("Select All",
                                                id="select_all",
                                                style={"flex":"1","margin":".5rem"}
                                                ),
                                    html.Button("Deselect All",
                                                id="deselect_all",
                                                style={"flex":"1","margin":".5rem"}
                                                ),
                                ]
                            ),
                            dcc.Checklist(
                                id="countries_checklist",
                                options=[{
                                    "label": i,
                                    "value": i
                                } for i in df.columns]
                                ,
                                style={
                                    "overflow-y": "auto",
                                    "height": "80%",
                                    "margin-top": "2rem"
                                }
                            )
                        ]
                    ),
                ]
            ),
            html.Div(
                className="row flex-display",
                children=[
                    dcc.Markdown(children=dataSourceText, className="twelve columns", style={"textAlign": "center","margin":"2rem"}),

                ]
            ),
        ])


app.layout = createLayout


@app.callback(
    Output("covid_graph","figure"),
    [ Input("data_store", "children")]
)
def update_graph( children):
    df = pd.read_json(children[0])
    countryList = ["New Zealand"]
    # if value is not None and len(value)>0 and value[0] == "All":
    #     countryList = df.columns.values

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
                    yaxis={'title': 'Confirmed cases',
                           "type" : "linear"},
                    margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
                    hovermode='closest',
                    title="Confirmed cases of COVID-19 in <br>New Zealand over time"
                )
            }




if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=True, port=8085, host="192.168.1.64")




