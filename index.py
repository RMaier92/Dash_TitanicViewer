import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State,dash_table 
import pandas as pd
import plotly.express as px

all_data = pd.read_csv("titanic.csv")
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Stylings
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

INPUT_STYLE = {
    'marginBottom': 20, 'marginTop': 20
}

# Frontend: Default values / Value getters

# Frontend: UI control definitions ...
fig_dropdownSex = html.Div([
    html.Label("Select gender:"),
    dcc.Dropdown(
        id='fig_dropdownSex',
        options=[{'label': item, 'value': item } for item in all_data["Sex"].unique()],
        value=None,
    )], 
    style=INPUT_STYLE)

fig_dropdownPclass = html.Div([
    html.Label("Select pClass:"),
    dcc.Dropdown(
        id='fig_dropdownPclass',
        options=[{'label': x, 'value': x} for x in ['fig1', 'fig2']],
        value=None,
        disabled=True
    )],
    style=INPUT_STYLE)

fig_table = html.Div([
    dash_table.DataTable(
    id='fig_table',
    columns=[{"name": i, "id": i} for i in all_data.columns],
    data=all_data.to_dict('records'),
    style_table={'overflowX': 'auto'},
    page_size=20,    
    page_current=0, 
)
])

fig_sliderAge = html.Div([
    html.Label("Select age range:"),
     dcc.RangeSlider(1, 99, value=[1, 99],step = 1,marks=None,id="ageSlider",
                tooltip={"placement": "bottom", "always_visible": True})
                ],
    style=INPUT_STYLE)


fig_graph = html.Div([
    dcc.Graph(id= "ratioChart", figure=px.pie())

])



# Frontend: Callbacks
@app.callback(
    [Output('dbc_reset', 'style')],
    [Input('fig_dropdownSex', 'value'), Input('ageSlider', 'value')]
)
def __(value, value2):
    if(value != None or value2 != [1,99]):
        return [dict()]
    else: 
        return [dict(display='none')]


@app.callback( #
    [
        Output('fig_dropdownSex', 'value'),
        Output('ageSlider', 'value')
    ],
    Input('dbc_reset', 'n_clicks')
)
def __(__):
    return [None, [1,99]]


@app.callback(
    [
        Output('fig_table', 'data'), 
        Output('resultCount', 'children'),
        Output('resultCount_male', 'children'),
        Output('resultCount_female', 'children'),
        Output('ratioChart', 'figure'),
        Output('ratioChart', 'style')
        ],
    [
        Input('fig_dropdownSex', 'value'),
        Input('fig_dropdownPclass', 'value'),
        Input('ageSlider', 'value')
    ],
    
)
def __(sex_name, pclass, ageSlider):
    fitered_data = all_data

    if(sex_name != None):
        fitered_data = fitered_data[ fitered_data["Sex"] == sex_name]

    if(pclass != None):
        fitered_data = fitered_data[ fitered_data["Pclass"] == pclass]

    fitered_data = fitered_data[fitered_data["Age"].between(ageSlider[0], ageSlider[1])]

    figure = px.pie(fitered_data, values=fitered_data["Sex"].value_counts().values, names=fitered_data["Sex"].value_counts().index)

    return [
        fitered_data.to_dict('records'), 
        str(len(fitered_data.index)), 
        str(len(fitered_data[fitered_data["Sex"] == "male"].index)), 
        str(len(fitered_data[fitered_data["Sex"] == "female"].index)),
        figure,
        dict() if sex_name == None else dict(display='none')
    ]


@app.callback(
Output('fig_dropdownPclass', 'disabled'),
[Input('fig_dropdownSex', 'value')])
def __(fig_name):
    return True if fig_name == None else False

@app.callback(
    Output('fig_dropdownPclass', 'options'),
    [Input('fig_dropdownSex', 'value')],

)
def __(fig_name):
    return [{'label': item, 'value': item } for item in sorted(all_data[all_data["Sex"] == fig_name]["Pclass"].unique())]


@app.callback(
Output('fig_dropdownPclass', 'value'),
[Input('fig_dropdownSex', 'value')])
def __(fig_name):
    return None

# UI: Layout definition

sidebar = html.Div(
    children = [
      
        html.H2("Data viewer"),
        html.Hr(),
        html.P(
            "Select filters to show specific entries of titanic dataset", className="lead"
        ),
        fig_dropdownSex,
        fig_dropdownPclass,
        fig_sliderAge,
        dbc.Button(
            "Reset filters", outline=True, color="secondary", className="me-1", id="dbc_reset"
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(
    id="page-content", 
    children= [
        html.H1("Overview"),
html.Hr(),

dbc.Row([
    dbc.Col(
        dbc.Card(
        [
            html.H2(id="resultCount", className="card-title"),
            html.P("Search results", className="card-text"),
        ],
        body=True,
        color="light",
    ),
    
    ),
    dbc.Col(
        dbc.Card(
        [
            html.H2(id="resultCount_male", className="card-title"),
            html.P("Male search results", className="card-text"),
        ],
        body=True,
        color="dark",
        inverse=True,
    ),
    
    ),
    dbc.Col(
        dbc.Card(
        [
            html.H2(id="resultCount_female", className="card-title"),
            html.P("Female search results", className="card-text"),
        ],
        body=True,
        color="primary",
        inverse=True,
    ),
    
    )


    ]),
          
    html.Hr(),
        fig_table,
        fig_graph
    ], 
    style=CONTENT_STYLE
)

app.layout = html.Div([sidebar, content ])
app.run_server(debug=True, use_reloader=False)