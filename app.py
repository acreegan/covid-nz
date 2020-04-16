import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import pandas as pd
import locale
import data_processing
locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True, external_stylesheets=external_stylesheets
)
app.title = "COVID-19 Cases NZ"
server = app.server


dataSourceText = "Data sources: [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19), " \
                 "[NZ Ministry of Health](https://www.health.govt.nz/our-work/diseases-and-conditions/" \
                 "covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases)"\
                 "   |   Site source code: [GitHub](https://github.com/acreegan/covid-nz)"


default_country="New Zealand"

def createLayout():
    global cases, casesText, casesNew, deaths, deathsText, deathsNew
    cases, casesText, casesNew, deaths, deathsText, deathsNew = data_processing.getData()

    return html.Div(
        id="mainContainer",
        className="mainContainer",
        children=[
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),

            html.Div(
                className="flex-display",
                children = [
                    html.H3(id="header", style={"flex":"1","marginTop":"0","textAlign":"center"}),
                ],
            ),

            dcc.Tabs(
                id='tab_selector',
                value='cases',
                className="tab_container",
                # Style needs to be here not in style.css or it doesn't work
                style={"display":"flex","flexFlow":"row nowrap"},
                children=[
                    dcc.Tab(label='Total cases over time', value='cases', className="tab", selected_className="tab--selected"),
                    dcc.Tab(label='New cases over time', value='newCases',className="tab", selected_className="tab--selected"),
                    dcc.Tab(label='New cases vs total cases', value='newVsTotal',className="tab", selected_className="tab--selected"),
                    dcc.Tab(label='Total deaths over time', value='deaths',className="tab", selected_className="tab--selected"),
                    dcc.Tab(label='New deaths over time', value='newDeaths',className="tab", selected_className="tab--selected")]
            ),
            html.Div(
                id="main_row",
                className="main_row pretty_container",
                style={
                    "marginTop": "0"
                },
                # Tab content goes here
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
              [Input('tab_selector', 'value')])
def create_tab_content(tab_value):
    if tab_value=='cases' or tab_value=='deaths':
        return [
            html.Div(
                id=tab_value + '_graph_container',
                className="graph_container",
                children=[
                    dcc.Graph(
                        id=tab_value + '_graph',
                        className="graph",
                        config={
                            "displayModeBar": False,
                            "responsive": True},
                    )
                ]
            ),
            html.Div(
                className="separator",
            ),
            html.Div(
                className="control_container",
                children=[
                    html.P("Select Countries"),
                    html.Div(
                        className="button_container",
                        children=[
                            html.Button("Select All",
                                        id=tab_value + '_select_all',
                                        style={"flex": "1", "margin": ".5rem"}
                                        ),
                            html.Button("Select None",
                                        id=tab_value + '_select_none',
                                        style={"flex": "1", "margin": ".5rem"}
                                        ),
                        ]
                    ),
                    dcc.Dropdown(
                        id=tab_value + '_dropdown',
                        className="dropdown",
                        value=[default_country], # Value is list since multi=True
                        persistence_type="memory",
                        persistence=True,
                        multi=True,
                        # Style needs to be here not in style.css or it doesn't work
                        style={
                            "flex": "1 1 0",
                            "overflow": "auto"
                        },
                        options=[
                            {
                                "label": i,
                                "value": i
                            } for i in cases.columns],
                    ),

                ]
            )]


    elif tab_value=='newCases' or tab_value=='newDeaths':
        return [
            html.Div(
                id= tab_value + '_graph_container',
                className="graph_container",
                children=[
                    dcc.Graph(
                        id=tab_value + '_graph',
                        className="graph",
                        config={
                            "displayModeBar": False,
                            "responsive": True},
                    )
                ]
            ),
            html.Div(
                className="separator",
            ),
            html.Div(
                className="control_container",
                children=[
                    html.P("Select Country"),
                    dcc.Dropdown(
                        id=tab_value + '_dropdown',
                        className="dropdown",
                        value="New Zealand",
                        persistence_type="memory",
                        persistence=True,
                        multi=False,
                        options=[
                            {
                                "label": i,
                                "value": i
                            } for i in cases.columns],
                    ),

                ]
            )]
    elif tab_value=='newVsTotal': #Currently same as first case, but may diverge soon
        return [
            html.Div(
                id=tab_value + '_graph_container',
                className="graph_container",
                children=[
                    dcc.Graph(
                        id=tab_value + '_graph',
                        className="graph",
                        config={
                            "displayModeBar": False,
                            "responsive": True},
                    )
                ]
            ),
            html.Div(
                className="separator",
            ),
            html.Div(
                className="control_container",
                children=[
                    html.P("Select Countries"),
                    html.Div(
                        className="button_container",
                        children=[
                            html.Button("Select All",
                                        id=tab_value + '_select_all',
                                        style={"flex": "1", "margin": ".5rem"}
                                        ),
                            html.Button("Select None",
                                        id=tab_value +'_select_none',
                                        style={"flex": "1", "margin": ".5rem"}
                                        ),
                        ]
                    ),
                    dcc.Dropdown(
                        id=tab_value + '_dropdown',
                        className="dropdown",
                        value=["New Zealand"],
                        persistence_type="memory",
                        persistence=True,
                        multi=True,
                        # Style needs to be here not in style.css or it doesn't work
                        style={
                            "flex": "1 1 0",
                            "overflow": "auto"
                        },
                        options=[
                            {
                                "label": i,
                                "value": i
                            } for i in cases.columns],
                    ),

                ]
            )]


@app.callback(
    Output("header","children"),
    [Input("cases_dropdown","value")]
)
def update_header(value):

    if value is None or len(value)==0:
        return dash.no_update
    else:
        country = value[0]
        return \
            locale.format_string(
                "As of %s, there have been %d cases in total of COVID-19 confirmed in %s",
                (cases[country].dropna().index[-1].strftime("%d %B %Y"),
                 cases[country].dropna().iloc[-1],
                 country),
                grouping=True)


@app.callback(
    Output("cases_dropdown","value"),
    [Input("cases_select_all","n_clicks"),
     Input("cases_select_none","n_clicks")],
    [State('cases_dropdown',"options")]
)
def update_dropdown_cases(all_n_clicks, none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return [default_country]

    else:
        if ctx.triggered[0]["prop_id"] == "cases_select_all" + ".n_clicks":
            return list(i.get("value") for i in options)
        else :
            return []


@app.callback(
    Output("newVsTotal_dropdown","value"),
    [Input("newVsTotal_select_all","n_clicks"),
     Input("newVsTotal_select_none","n_clicks")],
    [State('newVsTotal_dropdown',"options")]
)
def update_dropdown_newVsTotal(all_n_clicks, none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return [default_country]
    elif ctx.triggered[0]["prop_id"] == "newVsTotal_select_all" + ".n_clicks":
        return list(i.get("value") for i in options)
    else : #prop_id = select_none
        return []

@app.callback(
    Output("deaths_dropdown","value"),
    [Input("deaths_select_all","n_clicks"),
     Input("deaths_select_none","n_clicks")],
    [State('deaths_dropdown',"options")]
)
def update_dropdown_deaths(all_n_clicks, none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return [default_country]
    elif ctx.triggered[0]["prop_id"] == "deaths_select_all" + ".n_clicks":
        return list(i.get("value") for i in options)
    else : #prop_id = select_none
        return []



@app.callback(
    Output('cases_graph',"figure"),
    [Input('cases_dropdown',"value")]
)
def update_graph_cases(value):

    if value is None or len(value)==0:
        return dash.no_update
    else:
        countryList = value


    newData = [dict(
                x=cases.index,
                y=cases[i],
                name=i,
                text=casesText[i].dropna(),
                mode="lines+text",
                textposition="top left"
            ) for i in cases[countryList].columns]
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
    Output('newCases_graph',"figure"),
    [Input('newCases_dropdown',"value")]
)
def update_graph_newCases(value):

    if value is None or len(value)==0:
        return dash.no_update
    else:
        country= value

    newData = [dict(
                x=casesNew.index,
                y=casesNew[country],
                name=country,
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
                    title="New cases of COVID-19<br> over time",
                    showlegend=False,
                )
            }

@app.callback(
    Output('newVsTotal_graph',"figure"),
    [Input('newVsTotal_dropdown',"value")]
)
def update_graph_newVsTotal(value):

    if value is None or len(value)==0:
        return dash.no_update
    else:
        countryList = value


    newData = [dict(
                # Starting at the point where total cases > 50 (different times and lengths for each country)
                x=cases[i].loc[cases.index[cases[i] > 50]],
                y=casesNew[i].rolling(pd.to_timedelta("7days")).sum().loc[cases.index[cases[i] > 50]],
                name=i,
                text=casesText[i].dropna().loc[cases.index[cases[i] > 50]],
                mode="lines+text",
                textposition="top left"
            ) for i in cases[countryList].columns]
    return {
                'data': newData,
                'layout': dict(
                    xaxis={'title': 'Total cases',
                           "type":"log"},
                    yaxis={'title': 'New cases in past 7 days',
                           "type" : "log"},
                    margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
                    hovermode='closest',
                    title="New cases of COVID-19<br> vs total cases",
                    showlegend=False,
                )
            }

@app.callback(
    Output('deaths_graph',"figure"),
    [Input('deaths_dropdown',"value")]
)
def update_graph_deaths(value):
    global deaths, deathsText

    if value is None or len(value)==0:
        return dash.no_update
    else:
        countryList = value


    newData = [dict(
                x=deaths.index,
                y=deaths[i],
                name=i,
                text= casesText[i].dropna(),
                mode="lines+text",
                textposition="top left"
            ) for i in deaths[countryList].columns]
    return {
                'data': newData,
                'layout': dict(
                    xaxis={'title': 'Time'},
                    yaxis={'title': 'Confirmed deaths',
                           "type" : "linear"},
                    margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
                    hovermode='closest',
                    title="Total deaths from COVID-19<br> over time",
                    showlegend=False,
                )
            }

@app.callback(
    Output('newDeaths_graph',"figure"),
    [Input('newDeaths_dropdown',"value")]
)
def update_graph_newDeaths(value):

    if value is None or len(value)==0:
        return dash.no_update
    else:
        country= value

    newData = [dict(
                x=deathsNew.index,
                y=deathsNew[country],
                name=country,
                type="bar",
                textposition="top left"
            ) ]
    return {
                'data': newData,
                'layout': dict(
                    xaxis={'title': 'Time'},
                    yaxis={'title': 'New confirmed deaths',
                           "type" : "linear"
                           },
                    margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
                    hovermode='closest',
                    title="New deaths from COVID-19<br> over time",
                    showlegend=False,
                )
            }

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="autocomplete_off"),
    Output("output-clientside", "children"),
    [Input('tab_selector', 'value')],
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8085, host="0.0.0.0")




