import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


# df = pd.read_csv('https://data.humdata.org/hxlproxy/data/download/time_series_covid19_confirmed_global_narrow.csv?dest=data_edit&filter01=explode&explode-header-att01=date&explode-value-att01=value&filter02=rename&rename-oldtag02=%23affected%2Bdate&rename-newtag02=%23date&rename-header02=Date&filter03=rename&rename-oldtag03=%23affected%2Bvalue&rename-newtag03=%23affected%2Binfected%2Bvalue%2Bnum&rename-header03=Value&filter04=clean&clean-date-tags04=%23date&filter05=sort&sort-tags05=%23date&sort-reverse05=on&filter06=sort&sort-tags06=%23country%2Bname%2C%23adm1%2Bname&tagger-match-all=on&tagger-default-tag=%23affected%2Blabel&tagger-01-header=province%2Fstate&tagger-01-tag=%23adm1%2Bname&tagger-02-header=country%2Fregion&tagger-02-tag=%23country%2Bname&tagger-03-header=lat&tagger-03-tag=%23geo%2Blat&tagger-04-header=long&tagger-04-tag=%23geo%2Blon&header-row=1&url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_confirmed_global.csv')
# df = df[df['Country/Region']=='New Zealand']





df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
df = pd.melt(df.loc[df["Country/Region"]=="New Zealand"],"Country/Region",df.columns[4:],"Date","Value")
df.Date = pd.to_datetime(df.Date)

myhtml = urlopen("https://www.health.govt.nz/our-work/diseases-and-conditions/covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases").read().decode('utf-8')
soup = BeautifulSoup(myhtml,'html.parser')
if soup.find("table", class_="table-style-two").find_all("td")[0].string == 'Number of confirmed cases in New Zealand':
    b = soup.find("table", class_="table-style-two").find_all("td")[1].string

d = soup.find("table", class_="table-style-two").find("caption").string
time = datetime.strptime(d,"As at %I.%M %p, %d %B %Y")
latest = pd.DataFrame({"Country/Region":"New Zealand", "Date":pd.to_datetime(time),"Value":np.int64(b),},index=[0])
df = pd.concat([df,latest])


dataSourceText = '''Data sources: [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19), [NZ Ministry of Health](https://www.health.govt.nz/our-work/diseases-and-conditions/covid-19-novel-coronavirus/covid-19-current-situation/covid-19-current-cases) '''

app.layout = html.Div(children=[

    html.H1(children="As of %s there are %s confirmed cases of Covid19 in New Zealand" % (df["Date"].iloc[-1].strftime("%d %B %Y"),df.Value.iloc[-1]), style={
        'textAlign': 'center'
    }),

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
                yaxis={'title': 'Confirmed cases'},
                margin={'l': 100, 'b': 100, 't': 30, 'r': 100},
                legend={'x': 0, 'y': 1},
                hovermode='closest',
                title="Confirmed cases of Covid19 in New Zealand over time"
            )
        }
    ),

    dcc.Markdown(children=dataSourceText, style={"textAlign":"center"})
])

if __name__ == '__main__':
    app.run_server(debug=True)