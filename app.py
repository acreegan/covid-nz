import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('https://data.humdata.org/hxlproxy/data/download/time_series_covid19_confirmed_global_narrow.csv?dest=data_edit&filter01=explode&explode-header-att01=date&explode-value-att01=value&filter02=rename&rename-oldtag02=%23affected%2Bdate&rename-newtag02=%23date&rename-header02=Date&filter03=rename&rename-oldtag03=%23affected%2Bvalue&rename-newtag03=%23affected%2Binfected%2Bvalue%2Bnum&rename-header03=Value&filter04=clean&clean-date-tags04=%23date&filter05=sort&sort-tags05=%23date&sort-reverse05=on&filter06=sort&sort-tags06=%23country%2Bname%2C%23adm1%2Bname&tagger-match-all=on&tagger-default-tag=%23affected%2Blabel&tagger-01-header=province%2Fstate&tagger-01-tag=%23adm1%2Bname&tagger-02-header=country%2Fregion&tagger-02-tag=%23country%2Bname&tagger-03-header=lat&tagger-03-tag=%23geo%2Blat&tagger-04-header=long&tagger-04-tag=%23geo%2Blon&header-row=1&url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv')
df = df[df['Country/Region']=='New Zealand']
df.Date = pd.to_datetime(df.Date)

app.layout = html.Div([
    dcc.Graph(
        id='covid_graph',
        figure={
            'data': [
                dict(
                    x=df[df['Country/Region'] == i]['Date'],
                    y=df[df['Country/Region'] == i]['Value'],
                    #text=df[df['continent'] == i]['country'],
                    # mode='markers',
                    # opacity=0.7,
                    # marker={
                    #     'size': 15,
                    #     'line': {'width': 0.5, 'color': 'white'}
                    # },
                    # name=i
                ) for i in df['Country/Region'].unique()
            ],
            'layout': dict(
                xaxis={'title': 'Time'},
                yaxis={'title': 'Confirmed Cases'},
                margin={'l': 40, 'b': 40, 't': 30, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                title="Confirmed Cases of Covid19 in New Zealand"
            )
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)