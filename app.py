import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
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



johnsURLTotal = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
johnsURLDeaths = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
johnsURLRecovered = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
mohURL = "https://www.health.govt.nz/our-work/diseases-and-conditions/covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases"

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True
)


app.title = "COVID-19 Cases NZ"

server = app.server



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
            mohDate = pd.to_datetime(datetime.strptime(dateString, "Last updated %I:%M %p, %d %B %Y.").replace(hour=0, minute=0, second=0, microsecond=0))
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

    dfIncreaseInTotal = df - df.shift()

    return df,dfText,dfIncreaseInTotal

dataSourceText = "Data sources: [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19), " \
                 "[NZ Ministry of Health](https://www.health.govt.nz/our-work/diseases-and-conditions/" \
                 "covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases)"\
                 "   |   Site source code: [GitHub](https://github.com/acreegan/covid-nz)"



def createLayout():
    df,dfText, dfIncreaseInTotal = getData()

    return html.Div(
        id="mainContainer",
        className="mainContainer",
        children=[
            html.Div(id='data_store', style={'display': 'none'}, children=[df.to_json(),dfText.to_json(),dfIncreaseInTotal.to_json()]),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),

            html.Div(
                id="header",
                className="flex-display",
                children = [
                    html.H3(
                        children=locale.format_string(
                            "As of %s, there have been %d cases in total of COVID-19 confirmed in New Zealand",
                            (df.index[-1].strftime("%d %B %Y"), df["New Zealand"].iloc[-1]), grouping=True),
                        style={"flex":"1","marginTop":"0","textAlign":"center"}),

                ],
            ),

            dcc.Tabs(
                id='tab_selector',
                value='tab-1',
                style={
                    "width":"calc(100% - 20px)",
                    "boxSizing":"border-box",
                    "marginBottom":"0",
                    "marginLeft":"auto",
                    "marginRight":"auto",
                    "backgroundColor":"#f9f9f9",
                    "display":"flex",
                    "flexFlow":"row nowrap"

                },
                children=[
                    dcc.Tab(label='Total cases over time', value='tab-1', selected_style={"backgroundColor":"#f9f9f9"}),
                    dcc.Tab(label='Daily increase in total', value='tab-2',selected_style={"backgroundColor":"#f9f9f9"})]
            ),
            html.Div(
                id="main_row",
                className="main_row pretty_container",
                style={
                    "marginTop": "0"
                },

                children=[

                ]
            ),


            html.Div(
                className="flex-display",
                children=[
                    dcc.Markdown(children=dataSourceText, style={"textAlign": "center","margin":"2rem", "flex":"1"}),

                ]
            ),
        ])


app.layout = createLayout

@app.callback(Output('main_row', 'children'),
              [Input('tab_selector', 'value')],
              [State("data_store","children")])
def render_content(tab,children):
    df = pd.read_json(children[0])
    if tab=="tab-1":
        return \
            [ html.Div(
                    id="graph_container",
                    # className="pretty_container",
                    style={
                        "flex": "1 0 auto",
                        "display": "flex",
                        "overflow": "hidden",
                        "minWidth": "60vw",
                        "minHeight": "30rem"
                    },
                    children=[
                        dcc.Graph(
                            id="covid_graph",
                            className="graph",
                            config={
                                "displayModeBar": False,
                                "responsive": True},
                            style={
                                "flex": "1 1 auto",
                            },
                        )
                    ]
                ),
            html.Div(
                className="separator",
                style={
                    "width": "2px",
                    "height": "90%",
                    "margin": "10px",
                    "flex": "0 0 auto",
                    "background": "lightgrey",
                    "marginTop": "auto",
                    "marginBottom": "auto",
                }
            ),
            html.Div(
                className="control_container",
                style={
                    "flex": "1 1 auto",
                    "display": "flex",
                    "flexFlow": "column",

                },
                children=[
                    html.P("Select Countries", className="control_label"),
                    html.Div(
                        style={
                            "display": "flex",
                            "flexFlow": "row wrap",
                            "justifyContent": "center",
                            "alignItems": "center"
                        },
                        children=[
                            html.Button("Select All",
                                        id="select_all",
                                        style={"flex": "1", "margin": ".5rem"}
                                        ),
                            html.Button("Select None",
                                        id="select_none",
                                        style={"flex": "1", "margin": ".5rem"}
                                        ),
                        ]
                    ),
                    dcc.Dropdown(
                        id="countries",
                        className="dcc_control",
                        value=["New Zealand"],
                        persistence_type="memory",
                        persistence=True,
                        style={
                            "flex": "1",
                            "overflow": "auto"
                        },
                        options=[{
                            "label": i,
                            "value": i
                        } for i in df.columns]
                        ,
                        multi=True,
                    ),

                ]
            ),]

    elif tab=="tab-2":
        return \
            [html.Div(
                id="graph_container2",
                # className="pretty_container",
                style={
                    "flex": "1 0 auto",
                    "display": "flex",
                    "overflow": "hidden",
                    "minWidth": "60vw",
                    "minHeight": "30rem"
                },
                children=[
                    dcc.Graph(
                        id="covid_graph2",
                        className="graph",
                        config={
                            "displayModeBar": False,
                            "responsive": True},
                        style={
                            "flex": "1 1 auto",
                        },
                    )
                ]
            ),
                html.Div(
                    className="separator",
                    style={
                        "width": "2px",
                        "height": "90%",
                        "margin": "10px",
                        "flex": "0 0 auto",
                        "background": "lightgrey",
                        "marginTop": "auto",
                        "marginBottom": "auto",
                    }
                ),
                html.Div(
                    className="control_container",
                    style={
                        "flex": "1 1 auto",
                        "display": "flex",
                        "flexFlow": "column",

                    },
                    children=[
                        html.P("Select Country", className="control_label"),
                        dcc.Dropdown(
                            id="countries2",
                            className="dcc_control",
                            value="New Zealand",
                            persistence_type="memory",
                            persistence=True,
                            style={
                                "flex": "1",
                                "overflow": "auto"
                            },
                            options=[{
                                "label": i,
                                "value": i
                            } for i in df.columns]
                            ,
                            multi=False,
                        ),

                    ]
                ), ]


@app.callback(
    Output("header","children"),
    [Input("countries","value"),
     ],
    [State("data_store","children")]
)
def update_header(value,children):

    df = pd.read_json(children[0])

    if value is None or len(value)==0:
        return html.H3(
            children="None Selected",
            style={"flex":"1","marginTop":"0","textAlign":"center"}
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
                    style={"flex":"1","marginTop":"0","textAlign":"center"}
        ),


@app.callback(
    Output("countries","value"),
    [Input("select_all","n_clicks"),
     Input("select_none","n_clicks")],
    [State("countries","options")]
)
def update_dropdown(all_n_clicks, none_n_clicks, options):
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
def update_gc_children(v,c):

    if v is None:
        return dash.no_update

    if len(v) ==2:
        time.sleep(.0001)
        return c
    else:
        return dash.no_update

@app.callback(
    Output("covid_graph","figure"),
    [Input("countries","value")],
    [State("data_store","children")]
)
def update_graph(value, children):
    df = pd.read_json(children[0])
    dfText = pd.read_json(children[1])
    countryList=[]
    if value is not None and len(value)>0 :
        countryList = value


    newData = [dict(
                x=df.index,
                y=df[i],
                name=i,
                text= dfText[i].dropna() if len(countryList)>1 else "",
                mode="lines+text",
                textposition="top left"
            ) for i in df[countryList].columns]
    return {
                'data': newData,
                'layout': dict(
                    xaxis={'title': 'Time'},
                    yaxis={'title': 'Confirmed cases',
                           "type" : "linear"},
                    margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
                    hovermode='closest',
                    title="Total cases of COVID-19<br> over time",
                    showlegend=False,
                )
            }




@app.callback(
    Output("covid_graph2","figure"),
    [Input("countries2","value")],
    [State("data_store","children")]
)
def update_graph2(value, children):
    dfIncrease = pd.read_json(children[2])
    dfText = pd.read_json(children[1])
    country=""
    if value is not None and len(value)>0 :
        country = value


    newData = [dict(
                x=dfIncrease.index,
                y=dfIncrease[country],
                name=country,
                # text= dfText[i].dropna() if len(countryList)>1 else "",
                # mode="lines+text",
                type="bar",
                textposition="top left"
            ) ]
    return {
                'data': newData,
                'layout': dict(
                    xaxis={'title': 'Time'},
                    yaxis={'title': 'Confirmed cases',
                           "type" : "linear"
                           },
                    margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
                    hovermode='closest',
                    title="Increase in total number of<br> confirmed cases of COVID-19<br> over time",
                    showlegend=False,
                )
            }



app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="autocomplete_off"),
    Output("output-clientside", "children"),
    [Input('tab_selector', 'value')],
)

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=True, port=8085, host="192.168.1.64")




