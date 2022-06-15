import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import json
import requests
import csv
import pandas as pd
from datetime import datetime as dt
import flask

# Import and sort data from Folkhälsomyndigheten
df1 = pd.read_excel(
    "https://www.arcgis.com/sharing/rest/content/items/b5e7488e117749c19881cce45db13f7e/data",
    sheet_name="Veckodata Region",
    header=0,
    engine="openpyxl",
    keep_default_na=False,
)

df1["day"] = 1  # display Monday date for each week

df1["date"] = df1.apply(
    lambda row: dt.fromisocalendar(row["år"], row["veckonummer"], row["day"]), axis=1
)

df1 = df1.drop(df1[(df1.år == 2020) & (df1.veckonummer < 9)].index) # remove weeks before week 9 of 2020 because there is no data for those

# For the cases plot
df1_fall = df1[["date", "Region", "Antal_fall_vecka"]]
dfc_swe = df1_fall.groupby(["date"]).sum().reset_index()
dfc_swe.insert(loc=1, column="Region", value="Sweden")
df1_fall = pd.concat([df1_fall, dfc_swe])

# for the ICU plot
df1_intense = df1[["date", "Region", "Antal_intensivvårdade_vecka"]]
dfi_swe = df1_intense.groupby(["date"]).sum().reset_index()
dfi_swe.insert(loc=1, column="Region", value="Sweden")
df1_intense = pd.concat([df1_intense, dfi_swe])

# for the deaths plot
df1_deaths = df1[["date", "Region", "Antal_avlidna_vecka"]]
dfd_swe = df1_deaths.groupby(["date"]).sum().reset_index()
dfd_swe.insert(loc=1, column="Region", value="Sweden")
df1_deaths = pd.concat([df1_deaths, dfd_swe])

server = flask.Flask(__name__)

# Dash app

app = dash.Dash(
    __name__,
    server=server,
    title="COVID-19 in Sweden: Cases, ICU Admissions, Deaths",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

tabDataSource_content = dbc.CardBody(
    [
        html.Div(
            [
                dbc.Row(
                    dbc.Col(
                        html.Div([
                            html.P(["The visualizations in this dashboard are based on openly shared data by the Public Health Agency of Sweden (",html.A("Folkhälsomyndigheten", href="https://www.folkhalsomyndigheten.se/"),"). The data ", html.A("can be downloaded here", href="https://www.folkhalsomyndigheten.se/smittskydd-beredskap/utbrott/aktuella-utbrott/covid-19/statistik-och-analyser/bekraftade-fall-i-sverige/"), ". As of February 2022, these numbers are updated once a week, on Thursdays at 14:00; at this point information from the previous week is added."]),
                            html.P(["The ", html.I("Confirmed Cases"), " plot is based on data from the SmiNet reporting system, published as ", html.I("Antal_fall_vecka"), ". The ", html.I("Intensive Care Admissions"), " plot is based on data from the Swedish Intensive Care Register's (Svenska Intensivvårdsregistret) reporting system, published as ", html.I("Antal_intensivvårdade_vecka"), ". The ", html.I("Deaths"), " plot is based on data from the SmiNet reporting system, published as ", html.I("Antal_avlidna_vecka"), ". Here, the people with laboratory-confirmed COVID-19 which died are included, regardless of the cause of death."])
                            ]),
                    )
                ),
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            html.P(["If you have questions regarding the dashboard, get in touch with us on ", html.A("GitHub", href="https://github.com/ScilifelabDataCentre/dash-covid-in-sweden"), "."])
                        ),
                    )
                ),
            ],
        ),
    ],
)

tabPublicHealth_content = dbc.CardBody(
    [
        html.P(
            "This dashboard visualizes the timeline of the spread of COVID-19 in Sweden: number of confirmed cases, number of people admitted to ICU units, as well as deaths with ongoing or recent confirmed COVID-19. Information displayed here is based on most recently available weekly open data shared by the Swedish Public Health Agency (Folkhälsomyndigheten). Please see the 'Data sources' tab for more information.",
            className="card-text",
        ),
        html.P(
            "You can select an area of interest (either Sweden as a whole, or individual counties) and focus on a specific timeframe. The 'Date' menu below can be used to select a particular timeframe to focus on, but otherwise information is shown from February 2020 (earliest available data) until the most recent update. Similarly, the 'Select County' dropdown menu can be used to focus in on a particular Swedish county (region), or Sweden as a whole (the latter is shown by default).",
            className="card-text",
        ),
        html.P(
            "The dates below indicate the first day of the week for which the numbers are shown. For example, Feb 24 2020 stands for the week between February 24 and March 1 2020.",
            className="card-text",
        ),
        dbc.Row(
            dbc.Col(
                    html.Div(
                        [
                            dbc.Row([
                                html.Div([
                                    dbc.Row(
                                        dbc.Col("Select date range", className="font-weight-bold"),
                                        ),
                                    dbc.Row(
                                        dbc.Col(
                                            dcc.DatePickerRange(
                                            id="my-date-picker-range",  # ID to be used for callback
                                            calendar_orientation="horizontal",  # vertical or horizontal
                                            day_size=39,  # size of calendar image. Default is 39
                                            end_date_placeholder_text="Return",  # text that appears when no end date chosen
                                            with_portal=False,  # if True calendar will open in a full screen overlay portal
                                            first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
                                            reopen_calendar_on_clear=True,
                                            is_RTL=False,  # True or False for direction of calendar
                                            clearable=True,  # whether or not the user can clear the dropdown
                                            number_of_months_shown=1,  # number of months shown when calendar is open
                                            min_date_allowed=df1_intense["date"].iloc[
                                            0
                                            ],  # minimum date allowed on the DatePickerRange component
                                            max_date_allowed=df1_intense["date"].iloc[
                                            -1
                                            ],
                                            initial_visible_month=df1_intense[
                                            "date"
                                            ].iloc[-1],
                                            start_date=df1_intense["date"].iloc[0],
                                            end_date=df1_intense["date"].iloc[-1],
                                            display_format="DD MMM YY",  # how selected dates are displayed in the DatePickerRange component.
                                            month_format="MMMM, YYYY",  # how calendar headers are displayed when the calendar is opened.
                                            minimum_nights=1,  # minimum number of days between start and end date
                                            persistence=True,
                                            persisted_props=["start_date"],
                                            persistence_type="session",  # session, local, or memory. Default is 'local'
                                            updatemode="singledate",  # singledate or bothdates. Determines when callback is triggered
                                            )
                                        )
                                    ),
                                ], className="col-md-6 mt-2"
                                ),
                                html.Div([
                                    dbc.Row(
                                        dbc.Col("Select county (whole of Sweden shown by default)", className="font-weight-bold"),
                                        ),
                                    dbc.Row(
                                        dbc.Col(
                                            dcc.Dropdown(
                                            id="county-dropdown",
                                            clearable=False,
                                            persistence=True,
                                            persistence_type="session",
                                            options=[
                                            {"label": x, "value": x}
                                            for x in sorted(
                                            df1_intense["Region"].unique()
                                            )
                                            ],
                                            value="Sweden",
                                            )
                                        ),
                                    ),
                                ], className="col-md-6 mt-2"
                                ),
                        ]),
                        dcc.Graph(id="cases_graph"),
                        dcc.Graph(id="intensive_graph"),
                        dcc.Graph(id="deaths_graph")
                    ],
                )
            ),
        ),
        html.P(html.I(
            "Please keep in mind that the range of Y axes is different in each of these graphs."),
            className="card-text mt-3",
        )
    ],
)


app.layout = html.Div(
    [
        dbc.Row(
            [
                html.Div(
                    html.Div([
                        html.H1("COVID-19 in Sweden: Cases, ICU Admissions, Deaths")
                    ],
                    ), className="col-md-auto",
                )
            ],
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(label="Graphs", tab_id="tabPublicHealth"),
                                dbc.Tab(label="Data sources", tab_id="tabDataSource")
                            ],
                            id="tabs",
                            active_tab="tabPublicHealth"                        ),
                        html.Div(id="content"),
                    ], className="mt-3",
                ),
            ),
        ),
        html.Div([
            html.Hr(),
            dbc.Row(
                dbc.Col([
                    html.P(["This dashboard was created using ", html.A("Dash framework", href="https://github.com/plotly/dash"), " (v.1.20). The source code for the current version of the dashboard is ", html.A("available on GitHub", href="https://github.com/ScilifelabDataCentre/dash-covid-in-sweden"), "."],
                    className="text-muted")
                    ], className="mt-4"
                ),
            ),
        ],
        ),
], className="container-lg",
)


@app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
def switch_tab(at):
    if at == "tabPublicHealth":
        return tabPublicHealth_content
    elif at == "tabDataSource":
        return tabDataSource_content

@app.callback(
    Output("cases_graph", "figure"),
    [
        Input("county-dropdown", "value"),
        Input("my-date-picker-range", "start_date"),
        Input("my-date-picker-range", "end_date"),
    ],
)
def update_cases_graph(value, start_date, end_date):
    mask = (df1_fall["date"] > start_date) & (df1_fall["date"] <= end_date)
    df1 = df1_fall.loc[mask]
    df = df1[(df1["Region"] == value)]
    trace1 = go.Bar(
        x=df["date"],
        y=df["Antal_fall_vecka"],
        name="Case number",
        marker_color="#648fff",
        hovertemplate="<b>Number of confirmed cases</b>" + "<br>Week: %{x}" + "<br>Confirmed Cases: %{y}<extra></extra>",
    )

    # figure layout
    fig = go.Figure(data=trace1)
    fig.update_layout(
        plot_bgcolor="white", font=dict(size=13), margin=dict(l=0, r=0, t=50, b=50)
    )
    # modify x-axis
    fig.update_xaxes(
        title="<b>Date</b>",
        showgrid=True,
        linecolor="black",
        # set start point of x-axis
        tick0="2020-02-17",
    )
    # modify y-axis
    fig.update_yaxes(
        title="<b>Confirmed Cases</b>",
        showgrid=True,
        gridcolor="lightgrey",
        linecolor="black",
        # change range to envelope the appropriate range
        range=[0, max(df["Antal_fall_vecka"] + 50)],
    )

    return fig


@app.callback(
    Output("intensive_graph", "figure"),
    [
        Input("county-dropdown", "value"),
        Input("my-date-picker-range", "start_date"),
        Input("my-date-picker-range", "end_date"),
    ],
)
def update_intensive_graph(value, start_date, end_date):
    mask1 = (df1_intense["date"] > start_date) & (df1_intense["date"] <= end_date)
    ddf1 = df1_intense.loc[mask1]
    ddf = ddf1[(ddf1["Region"] == value)]
    trace2 = go.Bar(
        x=ddf["date"],
        y=ddf["Antal_intensivvårdade_vecka"],
        name="ICU admissions",
        marker_color="#dc267f",
        hovertemplate="<b>Number of ICU adminissions</b>" + "<br>Week: %{x}" + "<br>Admissions: %{y}<extra></extra>",
    )

    # figure layout
    fig = go.Figure(data=trace2)
    fig.update_layout(
        plot_bgcolor="white", font=dict(size=13), margin=dict(l=0, r=0, t=50, b=50)
    )
    # modify x-axis
    fig.update_xaxes(
        title="<b>Date</b>",
        showgrid=True,
        linecolor="black",
        # set start point of x-axis
        tick0="2020-02-17",
    )
    # modify y-axis
    fig.update_yaxes(
        title="<b>Intensive Care Admissions</b>",
        showgrid=True,
        gridcolor="lightgrey",
        linecolor="black",
        # change range to envelope the appropriate range
        range=[0, max(ddf["Antal_intensivvårdade_vecka"] + 10)],
    )

    return fig

@app.callback(
    Output("deaths_graph", "figure"),
    [
        Input("county-dropdown", "value"),
        Input("my-date-picker-range", "start_date"),
        Input("my-date-picker-range", "end_date"),
    ],
)
def update_deaths_graph(value, start_date, end_date):
    mask1 = (df1_deaths["date"] > start_date) & (df1_deaths["date"] <= end_date)
    ddf1 = df1_deaths.loc[mask1]
    ddf = ddf1[(ddf1["Region"] == value)]
    trace2 = go.Bar(
        x=ddf["date"],
        y=ddf["Antal_avlidna_vecka"],
        name="Deaths",
        marker_color="#785ef0",
        hovertemplate="<b>Number of deaths</b>"+ "<br>Week: %{x}" + "<br>Deaths: %{y}<extra></extra>",
    )

    # figure layout
    fig = go.Figure(data=trace2)
    fig.update_layout(
        plot_bgcolor="white", font=dict(size=13), margin=dict(l=0, r=0, t=50, b=50)
    )
    # modify x-axis
    fig.update_xaxes(
        title="<b>Date</b>",
        showgrid=True,
        linecolor="black",
        # set start point of x-axis
        tick0="2020-02-17",
    )
    # modify y-axis
    fig.update_yaxes(
        title="<b>Deaths</b>",
        showgrid=True,
        gridcolor="lightgrey",
        linecolor="black",
        # change range to envelope the appropriate range
        range=[0, max(ddf["Antal_avlidna_vecka"] + 10)],
    )

    return fig

# Server clause

if __name__ == "__main__":
    app.run_server(debug=False)
