import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import pandas as pd
import locale
import time
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


# Create ids for elements in tabs. Created here so they can be used to create callbacks
tab_ids = dict(
    tab_1=dict(
        graph_container="graph_container_tab_1",
        graph="graph_tab_1",
        select_all="select_all_tab_1",
        select_none="select_none_tab_1",
        dropdown="dropdown_tab_1",
    ),
    tab_2=dict(
        graph_container="graph_container_tab_2",
        graph="graph_tab_2",
        dropdown="dropdown_tab_2",
    ),
    tab_3 = dict(
        graph_container="graph_container_tab_3",
        graph="graph_tab_3",
        select_all="select_all_tab_3",
        select_none="select_none_tab_3",
        dropdown="dropdown_tab_3",
    )
)

df = pd.DataFrame()
dfText = pd.DataFrame()
dfNew = pd.DataFrame()


def createLayout():
    global df,dfText, dfNew
    df, dfText, dfNew = data_processing.getData()

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
                value='tab_1',
                className="tab_container",
                # Style needs to be here not in style.css or it doesn't work
                style={"display":"flex","flexFlow":"row nowrap"},
                children=[
                    dcc.Tab(label='Total cases over time', value='tab_1', className="tab", selected_className="tab--selected"),
                    dcc.Tab(label='New cases over time', value='tab_2',className="tab", selected_className="tab--selected"),
                    dcc.Tab(label='New cases vs total cases', value='tab_3',className="tab", selected_className="tab--selected")]
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
    global df
    id_dict = tab_ids[tab_value]
    if tab_value=='tab_1':
        return [
            html.Div(
                id=id_dict['graph_container'],
                className="graph_container",
                children=[
                    dcc.Graph(
                        id=id_dict['graph'],
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
                                        id=tab_ids[tab_value]['select_all'],
                                        style={"flex": "1", "margin": ".5rem"}
                                        ),
                            html.Button("Select None",
                                        id=tab_ids[tab_value]['select_none'],
                                        style={"flex": "1", "margin": ".5rem"}
                                        ),
                        ]
                    ),
                    dcc.Dropdown(
                        id=id_dict['dropdown'],
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
                            } for i in df.columns],
                    ),

                ]
            )]


    elif tab_value=='tab_2':
        return [
            html.Div(
                id=id_dict['graph_container'],
                className="graph_container",
                children=[
                    dcc.Graph(
                        id=id_dict['graph'],
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
                        id=id_dict['dropdown'],
                        className="dropdown",
                        value="New Zealand",
                        persistence_type="memory",
                        persistence=True,
                        multi=False,
                        options=[
                            {
                                "label": i,
                                "value": i
                            } for i in df.columns],
                    ),

                ]
            )]
    elif tab_value=='tab_3':
        return [
            html.Div(
                id=id_dict['graph_container'],
                className="graph_container",
                children=[
                    dcc.Graph(
                        id=id_dict['graph'],
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
                                        id=tab_ids[tab_value]['select_all'],
                                        style={"flex": "1", "margin": ".5rem"}
                                        ),
                            html.Button("Select None",
                                        id=tab_ids[tab_value]['select_none'],
                                        style={"flex": "1", "margin": ".5rem"}
                                        ),
                        ]
                    ),
                    dcc.Dropdown(
                        id=id_dict['dropdown'],
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
                            } for i in df.columns],
                    ),

                ]
            )]


@app.callback(
    Output("header","children"),
    [Input(tab_ids['tab_1']['dropdown'],"value")]
)
def update_header(value):
    global df

    if value is None or len(value)==0:
        return "None Selected"
    else:
        country = value[0]
        return \
            locale.format_string(
                "As of %s, there have been %d cases in total of COVID-19 confirmed in %s",
                (df[country].dropna().index[-1].strftime("%d %B %Y"),
                 df[country].dropna().iloc[-1],
                 country),
                grouping=True)


@app.callback(
    Output(tab_ids['tab_1']['dropdown'],"value"),
    [Input(tab_ids['tab_1']["select_all"],"n_clicks"),
     Input(tab_ids['tab_1']["select_none"],"n_clicks")],
    [State(tab_ids['tab_1']['dropdown'],"options")]
)
def update_dropdown_tab_1(all_n_clicks, none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return ["New Zealand"]

    else:
        if ctx.triggered[0]["prop_id"] == tab_ids['tab_1']["select_all"] + ".n_clicks":
            return list(i.get("value") for i in options)
        else :
            return []


@app.callback(
    Output(tab_ids['tab_3']['dropdown'],"value"),
    [Input(tab_ids['tab_3']["select_all"],"n_clicks"),
     Input(tab_ids['tab_3']["select_none"],"n_clicks")],
    [State(tab_ids['tab_3']['dropdown'],"options")]
)
def update_dropdown_tab_3(all_n_clicks, none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return ["New Zealand"]

    else:
        if ctx.triggered[0]["prop_id"] == tab_ids['tab_3']["select_all"] + ".n_clicks":
            return list(i.get("value") for i in options)
        else :
            return []






# @app.callback(
#     Output(tab_ids['tab_1']['graph_container'],"children"),
#     [Input(tab_ids['tab_1']['dropdown'],"value")],
#     [State(tab_ids['tab_1']['graph_container'],"children")]
# )
# def force_redraw_graph_tab_1(v,c):
#
#     if v is None:
#         return dash.no_update
#
#     if len(v) ==2:
#         time.sleep(1)
#         return c
#     else:
#         return dash.no_update

#
# @app.callback(
#     Output(tab_ids['tab_3']['graph_container'],"children"),
#     [Input(tab_ids['tab_3']['dropdown'],"value")],
#     [State(tab_ids['tab_3']['graph_container'],"children")]
# )
# def force_redraw_graph_tab_3(v,c):
#
#     if v is None:
#         return dash.no_update
#
#     if len(v) ==2:
#         time.sleep(.0001)
#         return c
#     else:
#         return dash.no_update


@app.callback(
    Output(tab_ids['tab_1']['graph'],"figure"),
    [Input(tab_ids['tab_1']['dropdown'],"value")]
)
def update_graph_tab_1(value):
    global df, dfText

    countryList=[]
    if value is not None and len(value)>0 :
        countryList = value


    newData = [dict(
                x=df.index,
                y=df[i],
                name=i,
                # text= dfText[i].dropna() if len(countryList)>1 else "",
                text=dfText[i].dropna(),
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
    Output(tab_ids['tab_2']['graph'],"figure"),
    [Input(tab_ids['tab_2']['dropdown'],"value")]
)
def update_graph_tab_2(value):
    global dfNew

    country=""
    if value is not None and len(value)>0 :
        country = value


    newData = [dict(
                x=dfNew.index,
                y=dfNew[country],
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
                    title="New confirmed cases of COVID-19<br> over time",
                    showlegend=False,
                )
            }

@app.callback(
    Output(tab_ids['tab_3']['graph'],"figure"),
    [Input(tab_ids['tab_3']['dropdown'],"value")]
)
def update_graph_tab_3(value):
    global df, dfNew, dfText

    countryList=[]
    if value is not None and len(value)>0 :
        countryList = value


    newData = [dict(
                # Starting at the point where total cases > 50 (different times and lengths for each country)
                x=df[i].loc[df.index[df[i]>50]],
                y=dfNew[i].rolling(pd.to_timedelta("7days")).sum().loc[df.index[df[i]>50]],
                name=i,
                # text= dfText[i].dropna().loc[df.index[df[i]>50]] if len(countryList)>1 else "",
                text=dfText[i].dropna().loc[df.index[df[i] > 50]],
                mode="lines+text",
                textposition="top left"
            ) for i in df[countryList].columns]
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

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="autocomplete_off"),
    Output("output-clientside", "children"),
    [Input('tab_selector', 'value')],
)

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=True, port=8085, host="192.168.1.64")




