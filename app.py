import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
import numpy as np
import locale
import time
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
            dateString = soup.find("p", class_="georgia-italic").string
            mohDate = pd.to_datetime(datetime.strptime(dateString, "Last updated %h:%mm, %d %B %Y.").replace(hour=0, minute=0, second=0, microsecond=0))
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


    return df,dfText

dataSourceText = "Data sources: [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19), " \
                 "[NZ Ministry of Health](https://www.health.govt.nz/our-work/diseases-and-conditions/" \
                 "covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases)"




def createLayout():
    df,dfText = getData()

    return html.Div(
        id="mainContainer",
        style={"display": "flex", "flexDirection": "column"},
        children=[
            html.Div(id='data_store', style={'display': 'none'}, children=[df.to_json(),dfText.to_json()]),

            html.Div(
                id="header",
                className="row flex-display",
                children = [
                    html.H3(
                        children=locale.format_string(
                            "As of %s there are %d confirmed cases of COVID-19 in New Zealand",
                            (df.index[-1].strftime("%d %B %Y"), df["New Zealand"].iloc[-1]), grouping=True),
                        className="twelve columns",
                        style={"textAlign": "center", "marginTop":"0"}),

                ],
            ),

            html.Div(
                className="row flex-display",
                style={"height":"75vh"},
                children=[
                    html.Div(
                        id="graph_container",
                        className="pretty_container nine columns",
                        children=[
                            dcc.Graph(id="covid_graph", className="graph", config={"displayModeBar":False})
                        ]
                    ),
                    html.Div(
                        className="pretty_container three columns",
                        style={
                            "display":"flex",
                            "flexFlow":"column",
                            "minHeight":"60vh"

                        },
                        children=[
                            html.P("Select Countries", className="control_label"),
                            html.Div(
                                style={
                                    "display":"flex",
                                    "flexFlow":"row wrap",
                                    "justifyContent":"center",
                                    "alignItems":"center"
                                },
                                children=[
                                    html.Button("Select All",
                                                id="select_all",
                                                style={"flex":"1","margin":".5rem"}
                                                ),
                                    html.Button("Select None",
                                                id="select_none",
                                                style={"flex":"1","margin":".5rem"}
                                                ),
                                ]
                            ),
                            dcc.Dropdown(
                                id="countries",
                                style={
                                    "flex":"1",
                                    "overflow":"auto"
                                },
                                options=[{
                                    "label": i,
                                    "value": i
                                } for i in df.columns]
                                ,
                                multi=True,
                                className="dcc_control"
                            ),

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
    Output("header","children"),
    [Input("countries","value")],
    [State("data_store","children")]
)
def update_header(value, children):
    df = pd.read_json(children[0])

    if value is None or len(value)==0:
        return html.H3(
            children="None Selected",
            className="twelve columns",
            style={"textAlign": "center", "marginTop": "0"}
        ),
    else:
        country = value[0]
        return html.H3(
                    children=locale.format_string(
                        "As of %s, there have been %d cases in total of COVID-19 confirmed in %s",
                        (df[country].dropna().index[-1].strftime("%d %B %Y"),
                         df[country].dropna().iloc[-1],
                         country),
                        grouping=True),
                    className="twelve columns",
                    style={"textAlign": "center", "marginTop":"0"}
        ),


@app.callback(
    Output("countries","value"),
    [Input("select_all","n_clicks"),
     Input("select_none","n_clicks")],
    [State("countries","options")]
)
def select_all(all_n_clicks,none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return ["New Zealand"]

    else:
        if ctx.triggered[0]["prop_id"] == "select_all.n_clicks":
            return list(i.get("value") for i in options)
        else :
            return []



@app.callback(
    Output("graph_container","children"),
    [Input("countries","value")],
    [State("graph_container","children")]
)
def update_gc_children(f,c):
    time.sleep(.0001)
    return c

@app.callback(
    Output("covid_graph","figure"),
    [Input("data_store", "children"),
     Input("countries","value")]
)
def update_graph(children, value):
    df = pd.read_json(children[0])
    dfText = pd.read_json(children[1])
    countryList=[]
    if value is not None and len(value)>0 :
        countryList = value
    return {
                'data': [
                    dict(
                        x=df.index,
                        y=df[i],
                        name=i,
                        text= dfText[i].dropna() if len(countryList)>1 else "",
                        mode="lines+text",
                        textposition="top left"
                    ) for i in df[countryList].columns
                ],
                'layout': dict(
                    xaxis={'title': 'Time'},
                    yaxis={'title': 'Confirmed cases',
                           "type" : "linear"},
                    margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
                    hovermode='closest',
                    title="Confirmed cases of COVID-19<br> over time",
                    showlegend=False,
                )
            }





if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=True, port=8085, host="192.168.1.64")




