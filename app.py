import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import pandas as pd
import locale
import data_processing
import json

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

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

default_country = "New Zealand"


def createLayout():
    global cases, casesText, casesNew, deaths, deathsText, deathsNew, \
           recovered, recoveredText, recoveredNew, active, activeText, activeNew, population

    cases, casesText, casesNew, deaths, deathsText, deathsNew, \
        recovered, recoveredText, recoveredNew, active, activeText, activeNew, population = data_processing.getData()

    return html.Div(
        id="mainContainer",
        className="mainContainer",
        children=[
            html.Div(id="header_accumulator_cases", style={"display":"none"}),
            html.Div(id="header_accumulator_active", style={"display":"none"}),
            html.Div(id="header_accumulator_recovered", style={"display":"none"}),
            html.Div(id="header_accumulator_deaths", style={"display":"none"}),

            # empty Div to trigger javascript file for autocomplete off
            html.Div(id="output-clientside"),

            html.Div(
                className="flex-display",
                children=[
                    html.H3(id="header", style={"flex": "1", "marginTop": "0", "textAlign": "center"}),
                ],
            ),

            dcc.Tabs(
                id='tab_selector',
                value='cases',
                className="tab_container",
                # Style needs to be here not in style.css or it doesn't work
                style={"display": "flex", "flexFlow": "row nowrap"},
                children=[
                    dcc.Tab(label='Total cases', value='cases', className="tab", selected_className="tab--selected"),
                    dcc.Tab(label='Active cases', value='active', className="tab", selected_className="tab--selected"),
                    dcc.Tab(label='Recovered', value='recovered', className="tab", selected_className="tab--selected"),
                    dcc.Tab(label='Deaths', value='deaths', className="tab", selected_className="tab--selected"),
                    dcc.Tab(label='New cases vs total cases', value='newVsTotal', className="tab", selected_className="tab--selected"),
                ]
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
                    dcc.Markdown(children=dataSourceText, style={"textAlign": "center", "margin": "2rem", "flex": "1"}),
                ]
            ),
        ])


app.layout = createLayout


@app.callback(Output('main_row', 'children'), [Input('tab_selector', 'value')])
def create_tab_content(tab_value):
    dropdown_columns = cases.columns if (tab_value != "active" and tab_value != "recovered") else active.columns #Active columns are different becasuse there is no active data for US

    if tab_value == 'cases' or tab_value == 'active' or tab_value == 'recovered' or tab_value == 'deaths':
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
                    html.P("New or Total Cases:"),
                    dcc.RadioItems(
                        id=tab_value + '_new_v_total',
                        options=[
                            {'label': 'Total', 'value': 'total'},
                            {'label': 'New', 'value': 'new'},
                        ],
                        value='total',
                        persistence=True,
                    ),
                    html.P(""),
                    html.P("Graph Scale: "),
                    dcc.RadioItems(
                        id=tab_value + '_scale',
                        options=[
                            {'label': 'Linear', 'value': 'linear'},
                            {'label': 'Log', 'value': 'log'},
                            {'label': 'Per 10,000 population', 'value': 'per_capita'},
                        ],
                        value='linear',
                        persistence=True,
                    ),
                    html.P(""),
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
                        value=[default_country],  # Value is list since multi=True
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
                            } for i in dropdown_columns],
                    ),

                ]
            )]

    elif tab_value == 'newVsTotal':
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
                        value=["New Zealand"],
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


# The accumulators are a workaround to enable us to use dynamically generated elements as inputs.
# Dash requires all inputs of a callback to exist at the time the callback is run (And only one callback to output to
# each element). This is not possible with dynamically generated tabs, so we feed their values into the accumulators
# to act as intermediaries
@app.callback(
    Output("header", "children"),
    [Input("header_accumulator_cases", "children"),
     Input("header_accumulator_active", "children"),
     Input("header_accumulator_recovered", "children"),
     Input("header_accumulator_deaths", "children")],
)
def update_header(value_cases, value_active, value_recovered, value_deaths):
    ctx = dash.callback_context
    values = json.loads(ctx.triggered[0]["value"])
    if len(values["dropdown"])>0:
        country = values["dropdown"][0]
    else:
        return dash.no_update

    newvtotal = values["newvtotal"]

    if ctx.triggered[0]["prop_id"] == "header_accumulator_cases.children":
        if newvtotal == "total":
            return locale.format_string(
                "As of %s, there have been %d cases in total of COVID-19 in %s",
                (cases[country].dropna().index[-1].strftime("%d %B %Y"),
                 cases[country].dropna().iloc[-1],
                 country),
                grouping=True)
        else:
            number = casesNew[country].dropna().iloc[-1]
            return locale.format_string(
                "On %s, there were %d new cases of COVID-19 in %s",
                (cases[country].dropna().index[-1].strftime("%d %B %Y"),
                 number,
                 country),
                grouping=True)
    elif ctx.triggered[0]["prop_id"] == "header_accumulator_active.children":
        if newvtotal == "total":
            return locale.format_string(
                "As of %s, there are %d active cases of COVID-19 in %s",
                (active[country].dropna().index[-1].strftime("%d %B %Y"),
                 active[country].dropna().iloc[-1],
                 country),
                grouping=True)
        else:
            number = activeNew[country].dropna().iloc[-1]
            return locale.format_string(
                "On %s, the number of active cases of COVID-19 in %s " + ("increased" if number>=0 else "decreased") + " by %d",
                (active[country].dropna().index[-1].strftime("%d %B %Y"),
                 country,
                 abs(number)),
                grouping=True)
    elif ctx.triggered[0]["prop_id"] == "header_accumulator_recovered.children":
        if newvtotal == "total":
            return locale.format_string(
                "As of %s, there are %d recovered cases of COVID-19 in %s",
                (recovered[country].dropna().index[-1].strftime("%d %B %Y"),
                 recovered[country].dropna().iloc[-1],
                 country),
                grouping=True)
        else:
            number = recoveredNew[country].dropna().iloc[-1]
            return locale.format_string(
                "On %s, there were %d new recovered cases of COVID-19 in %s",
                (recovered[country].dropna().index[-1].strftime("%d %B %Y"),
                 abs(number),
                 country),
                grouping=True)
    elif ctx.triggered[0]["prop_id"] == "header_accumulator_deaths.children":
        if newvtotal == "total":
            return locale.format_string(
                "As of %s, there have been %d deaths from COVID-19 in %s",
                (deaths[country].dropna().index[-1].strftime("%d %B %Y"),
                 deaths[country].dropna().iloc[-1],
                 country),
                grouping=True)
        else:
            number = deathsNew[country].dropna().iloc[-1]
            return locale.format_string(
                "On %s, there were %d new deaths from COVID-19 in %s ",
                (deaths[country].dropna().index[-1].strftime("%d %B %Y"),
                 number,
                 country),
                grouping=True)
    else:
        return dash.no_update


@app.callback(
    Output("cases_dropdown", "value"),
    [Input("cases_select_all", "n_clicks"),
     Input("cases_select_none", "n_clicks")],
    [State('cases_dropdown', "options")]
)
def update_dropdown_cases(all_n_clicks, none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return [default_country]
    else:
        if ctx.triggered[0]["prop_id"] == "cases_select_all" + ".n_clicks":
            return list(i.get("value") for i in options)
        else:
            return []


@app.callback(
    Output("active_dropdown", "value"),
    [Input("active_select_all", "n_clicks"),
     Input("active_select_none", "n_clicks")],
    [State('active_dropdown', "options")]
)
def update_dropdown_active(all_n_clicks, none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return [default_country]
    elif ctx.triggered[0]["prop_id"] == "active_select_all" + ".n_clicks":
        return list(i.get("value") for i in options)
    else:  # prop_id = select_none
        return []


@app.callback(
    Output("recovered_dropdown", "value"),
    [Input("recovered_select_all", "n_clicks"),
     Input("recovered_select_none", "n_clicks")],
    [State('recovered_dropdown', "options")]
)
def update_dropdown_recovered(all_n_clicks, none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return [default_country]
    elif ctx.triggered[0]["prop_id"] == "recovered_select_all" + ".n_clicks":
        return list(i.get("value") for i in options)
    else:  # prop_id = select_none
        return []


@app.callback(
    Output("deaths_dropdown", "value"),
    [Input("deaths_select_all", "n_clicks"),
     Input("deaths_select_none", "n_clicks")],
    [State('deaths_dropdown', "options")]
)
def update_dropdown_deaths(all_n_clicks, none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return [default_country]
    elif ctx.triggered[0]["prop_id"] == "deaths_select_all" + ".n_clicks":
        return list(i.get("value") for i in options)
    else:  # prop_id = select_none
        return []


@app.callback(
    Output("newVsTotal_dropdown", "value"),
    [Input("newVsTotal_select_all", "n_clicks"),
     Input("newVsTotal_select_none", "n_clicks")],
    [State('newVsTotal_dropdown', "options")]
)
def update_dropdown_newVsTotal(all_n_clicks, none_n_clicks, options):
    ctx = dash.callback_context

    if ctx.triggered[0]["value"] is None:
        return [default_country]
    elif ctx.triggered[0]["prop_id"] == "newVsTotal_select_all" + ".n_clicks":
        return list(i.get("value") for i in options)
    else:  # prop_id = select_none
        return []


@app.callback(
    Output('cases_scale', "options"),
    [Input('cases_new_v_total', "value")],
    [State('cases_scale', 'options')]
)
def update_scale_options_cases(value, options):
    if value == "new":
        for item in options:
            if item["value"] != "linear":
                item["disabled"] = True
        return options
    else:
        for item in options:
            item["disabled"] = False
        return options


@app.callback(
    Output('active_scale', "options"),
    [Input('active_new_v_total', "value")],
    [State('active_scale', 'options')]
)
def update_scale_options_active(value, options):
    if value == "new":
        for item in options:
            if item["value"] != "linear":
                item["disabled"] = True
        return options
    else:
        for item in options:
            item["disabled"] = False
        return options


@app.callback(
    Output('recovered_scale', "options"),
    [Input('recovered_new_v_total', "value")],
    [State('recovered_scale', 'options')]
)
def update_scale_options_recovered(value, options):
    if value == "new":
        for item in options:
            if item["value"] != "linear":
                item["disabled"] = True
        return options
    else:
        for item in options:
            item["disabled"] = False
        return options


@app.callback(
    Output('deaths_scale', "options"),
    [Input('deaths_new_v_total', "value")],
    [State('deaths_scale', 'options')]
)
def update_scale_options_deaths(value, options):
    if value == "new":
        for item in options:
            if item["value"] != "linear":
                item["disabled"] = True
        return options
    else:
        for item in options:
            item["disabled"] = False
        return options


@app.callback(
    Output('cases_graph', "figure"),
    [Input('cases_dropdown', "value"),
     Input('cases_new_v_total', "value"),
     Input('cases_scale', "value")]
)
def update_graph_cases(dropdown_value, newvtotal_value, scale_value):
    # So we can copy paste these callbacks and only update values at top.
    totalTitle = "Total cases of COVID-19<br> over time"
    newTitle = "New cases of COVID-19<br> over time"
    yLabel = "Confirmed cases"
    perCapitaYLabel = 'Confirmed cases per 10,000 population'
    data = cases if newvtotal_value == "total" else casesNew
    dataText = casesText

    if dropdown_value is None or len(dropdown_value) == 0:
        return dash.no_update
    else:
        countryList = dropdown_value

    if newvtotal_value == "total":
        graphData = [dict(
                    x=data.index if scale_value != "log" else data.index[data[i] > 50],
                    y=data[i] if scale_value == "linear" else data[i].loc[data.index[data[i] > 50]] if scale_value == "log" else 10000*data[i]/population.loc["Population", i],
                    name=i,
                    text=dataText[i].dropna() if scale_value != "log" else dataText[i].dropna().loc[data.index[data[i] > 50]],
                    mode="lines+text",
                    textposition="top left"
                ) for i in data[countryList].columns]

        layout = dict(
                    xaxis={'title': 'Time'},
                    yaxis={'title': yLabel if scale_value != "per_capita" else perCapitaYLabel,
                           "type": "linear" if scale_value != "log" else "log"},
                    margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
                    hovermode='closest',
                    title=totalTitle,
                    showlegend=False,
                )
    else:  # newvtotal_value = new
        graphData = [dict(
            x=data.index,
            y=data[i],
            name=i,
            type="bar",
            textposition="top left"
        ) for i in data[countryList[0]].to_frame().columns]

        layout = dict(
            xaxis={'title': 'Time'},
            yaxis={'title': yLabel,
                   "type": "linear"},
            margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
            hovermode='closest',
            title=newTitle,
            showlegend=False,)

    return {'data': graphData,
            'layout': layout}


@app.callback(
    Output('active_graph', "figure"),
    [Input('active_dropdown', "value"),
     Input('active_new_v_total', "value"),
     Input('active_scale', "value")]
)
def update_graph_active(dropdown_value, newvtotal_value, scale_value):
    # So we can copy paste these callbacks and only update values at top.
    totalTitle = "Active cases of COVID-19<br> over time"
    newTitle = "Change in active cases of COVID-19<br> over time"
    yLabel = "Active cases"
    perCapitaYLabel = 'Active cases per 10,000 population'
    data = active if newvtotal_value == "total" else activeNew
    dataText = activeText

    if dropdown_value is None or len(dropdown_value) == 0:
        return dash.no_update
    else:
        countryList = dropdown_value

    if newvtotal_value == "total":
        graphData = [dict(
                    x=data.index if scale_value != "log" else data.index[data[i] > 50],
                    y=data[i] if scale_value == "linear" else data[i].loc[data.index[data[i] > 50]] if scale_value == "log" else 10000*data[i]/population.loc["Population", i],
                    name=i,
                    text=dataText[i].dropna() if scale_value != "log" else dataText[i].dropna().loc[data.index[data[i] > 50]],
                    mode="lines+text",
                    textposition="top left"
                ) for i in data[countryList].columns]

        layout = dict(
                    xaxis={'title': 'Time'},
                    yaxis={'title': yLabel if scale_value != "per_capita" else perCapitaYLabel,
                           "type": "linear" if scale_value != "log" else "log"},
                    margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
                    hovermode='closest',
                    title=totalTitle,
                    showlegend=False,
                )
    else:  # newvtotal_value = new
        graphData = [dict(
            x=data.index,
            y=data[i],
            name=i,
            type="bar",
            textposition="top left"
        ) for i in data[countryList[0]].to_frame().columns]

        layout = dict(
            xaxis={'title': 'Time'},
            yaxis={'title': yLabel,
                   "type": "linear"},
            margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
            hovermode='closest',
            title=newTitle,
            showlegend=False,)

    return {'data': graphData,
            'layout': layout}


@app.callback(
    Output('recovered_graph', "figure"),
    [Input('recovered_dropdown', "value"),
     Input('recovered_new_v_total', "value"),
     Input('recovered_scale', "value")]
)
def update_graph_recovered(dropdown_value, newvtotal_value, scale_value):
    # So we can copy paste these callbacks and only update values at top.
    totalTitle = "Recovered cases of COVID-19<br> over time"
    newTitle = "Change in recovered cases of COVID-19<br> over time"
    yLabel = "Recovered cases"
    perCapitaYLabel = 'Recovered cases per 10,000 population'
    data = recovered if newvtotal_value == "total" else recoveredNew
    dataText = recoveredText

    if dropdown_value is None or len(dropdown_value) == 0:
        return dash.no_update
    else:
        countryList = dropdown_value

    if newvtotal_value == "total":
        graphData = [dict(
            x=data.index if scale_value != "log" else data.index[data[i] > 50],
            y=data[i] if scale_value == "linear" else data[i].loc[
                data.index[data[i] > 50]] if scale_value == "log" else 10000 * data[i] / population.loc[
                "Population", i],
            name=i,
            text=dataText[i].dropna() if scale_value != "log" else dataText[i].dropna().loc[data.index[data[i] > 50]],
            mode="lines+text",
            textposition="top left"
        ) for i in data[countryList].columns]

        layout = dict(
            xaxis={'title': 'Time'},
            yaxis={'title': yLabel if scale_value != "per_capita" else perCapitaYLabel,
                   "type": "linear" if scale_value != "log" else "log"},
            margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
            hovermode='closest',
            title=totalTitle,
            showlegend=False,
        )
    else:  # newvtotal_value = new
        graphData = [dict(
            x=data.index,
            y=data[i],
            name=i,
            type="bar",
            textposition="top left"
        ) for i in data[countryList[0]].to_frame().columns]

        layout = dict(
            xaxis={'title': 'Time'},
            yaxis={'title': yLabel,
                   "type": "linear"},
            margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
            hovermode='closest',
            title=newTitle,
            showlegend=False, )

    return {'data': graphData,
            'layout': layout}


@app.callback(
    Output('deaths_graph', "figure"),
    [Input('deaths_dropdown', "value"),
     Input('deaths_new_v_total', "value"),
     Input('deaths_scale', "value")]
)
def update_graph_deaths(dropdown_value, newvtotal_value, scale_value):
    # So we can copy paste these callbacks and only update values at top.
    totalTitle = "Deaths from COVID-19<br> over time"
    newTitle = "Change in deaths from COVID-19<br> over time"
    yLabel = "Deaths"
    perCapitaYLabel = 'Deaths per 10,000 population'
    data = deaths if newvtotal_value == "total" else deathsNew
    dataText = deathsText

    if dropdown_value is None or len(dropdown_value) == 0:
        return dash.no_update
    else:
        countryList = dropdown_value

    if newvtotal_value == "total":
        graphData = [dict(
            x=data.index if scale_value != "log" else data.index[data[i] > 50],
            y=data[i] if scale_value == "linear" else data[i].loc[
                data.index[data[i] > 50]] if scale_value == "log" else 10000 * data[i] / population.loc[
                "Population", i],
            name=i,
            text=dataText[i].dropna() if scale_value != "log" else dataText[i].dropna().loc[data.index[data[i] > 50]],
            mode="lines+text",
            textposition="top left"
        ) for i in data[countryList].columns]

        layout = dict(
            xaxis={'title': 'Time'},
            yaxis={'title': yLabel if scale_value != "per_capita" else perCapitaYLabel,
                   "type": "linear" if scale_value != "log" else "log"},
            margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
            hovermode='closest',
            title=totalTitle,
            showlegend=False,
        )
    else:  # newvtotal_value = new
        graphData = [dict(
            x=data.index,
            y=data[i],
            name=i,
            type="bar",
            textposition="top left"
        ) for i in data[countryList[0]].to_frame().columns]

        layout = dict(
            xaxis={'title': 'Time'},
            yaxis={'title': yLabel,
                   "type": "linear"},
            margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
            hovermode='closest',
            title=newTitle,
            showlegend=False, )

    return {'data': graphData,
            'layout': layout}


@app.callback(
    Output('newVsTotal_graph', "figure"),
    [Input('newVsTotal_dropdown', "value")]
)
def update_graph_newVsTotal(value):

    if value is None or len(value) == 0:
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
                           "type": "log"},
                    yaxis={'title': 'New cases in past 7 days',
                           "type": "log"},
                    margin={'l': 50, 'b': 40, 't': 40, 'r': 20},
                    hovermode='closest',
                    title="New cases of COVID-19<br> vs total cases",
                    showlegend=False,
                )
            }

@app.callback(
    Output('header_accumulator_cases', 'children'),
    [Input('cases_dropdown', "value"),
     Input('cases_new_v_total', "value")]
)
def update_header_accumulator_cases(dropdown, newvtotal):
    return json.dumps(dict(
        dropdown=dropdown,
        newvtotal=newvtotal
    ))

@app.callback(
    Output('header_accumulator_active', 'children'),
    [Input('active_dropdown', "value"),
     Input('active_new_v_total', "value")]
)
def update_header_accumulator_active(dropdown, newvtotal):
    return json.dumps(dict(
        dropdown=dropdown,
        newvtotal=newvtotal
    ))

@app.callback(
    Output('header_accumulator_deaths', 'children'),
    [Input('deaths_dropdown', "value"),
     Input('deaths_new_v_total', "value")]
)
def update_header_accumulator_deaths(dropdown, newvtotal):
    return json.dumps(dict(
        dropdown=dropdown,
        newvtotal=newvtotal
    ))

@app.callback(
    Output('header_accumulator_recovered', 'children'),
    [Input('recovered_dropdown', "value"),
     Input('recovered_new_v_total', "value")]
)
def update_header_accumulator_cases(dropdown, newvtotal):
    return json.dumps(dict(
        dropdown=dropdown,
        newvtotal=newvtotal
    ))



app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="autocomplete_off"),
    Output("output-clientside", "children"),
    [Input('tab_selector', 'value')],
)

if __name__ == '__main__':
    app.run_server(debug=True, port=8085, host="0.0.0.0")
