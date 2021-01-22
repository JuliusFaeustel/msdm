from flask import Flask, request, render_template
import loader
import plotly
import json
import plotly.graph_objects as go
import re
import datetime
import statistics
import pandas as pd
from plotly.subplots import make_subplots

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()


@app.route('/snr', methods=['GET', 'POST'])
def snr():
    dataSet = ""
    if request.method == 'POST':
        text = request.form['text']
        snr = text.upper()
        dataSet = loader.findBySNR(snr)

    return render_template("snrLoader.html", content=dataSet)


@app.route('/taktzeit1')
def render_Plot_tkt1():
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Document Orientated", "Universell-Relational", "Key-Value-Store", "Proprietäre Datenstruktur"))
    data = [["C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/" +
             "AuswertungenCSV_Corn/Analyse_1_Output.csv", [1, 1]],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Paul/001.csv",
                [1, 2]],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Clem/takt1.csv",
                [2, 1]],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungenCSV_Lukas/Taktung1.csv",
                [2, 2]]
            ]
    for datapoint in data:
        rohData = txt_loader_tz1(datapoint[0])
        fig = create_Plot_Taktzeit1(fig, rohData, datapoint[1][0], datapoint[1][1])
    fig.update_yaxes(tickformat='%H:%M:%S')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("taktzeit1.html", plot=graphJSON)


def txt_loader_tz1(speicherOrt):
    df = pd.read_csv(speicherOrt, delimiter=";")
    df = df[df.MIN > 0]
    df = df[df.MAX < 3600]
    df['MIN'] = pd.to_datetime(df["MIN"], unit='s')
    df['MAX'] = pd.to_datetime(df["MAX"], unit='s')
    df['AVG'] = pd.to_datetime(df["AVG"], unit='s')
    df = df.groupby('TEIL')
    return df


def create_Plot_Taktzeit1(fig, rohData, row, col):
    if (row == 1 and col == 1):
        showlegend = True
    else:
        showlegend = False
    for teil in rohData:
        data = teil[1]
        fig.add_box(y=data.MIN, name="Min " + teil[0], col=col, row=row, legendgroup='group1',
                    showlegend=showlegend).update_layout(height=1200)
        fig.add_box(y=data.AVG, name="Avg " + teil[0], col=col, row=row, legendgroup='group2', showlegend=showlegend)
        fig.add_box(y=data.MAX, name="MAX " + teil[0], col=col, row=row, legendgroup='group3', showlegend=showlegend)
    return fig


@app.route('/taktzeit2')
def render_Plot_tkt2():
    fig = make_subplots(
        rows=4, cols=2,
        subplot_titles=(
            "Document Orientated", "Fehlerrate Universell-Relational", "Key-Value-Store", "Proprietäre Datenstruktur",
            "Fehlerrate Document Orientated", "Fehlerrate Universell-Relational",
            "Fehlerrate Key-Value-Store", "Fehlerrate Proprietäre Datenstruktur")
    )
    data = [["C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/" +
             "AuswertungenCSV_Corn/Analyse_2_Output.csv", [1, 1]],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Paul/002.csv",
                [1, 2]],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Clem/takt2.csv",
                [2, 1]],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungenCSV_Lukas/Taktung2.csv",
                [2, 2]]
            ]
    for datapoint in data:
        rohData = txt_loader_tz2(datapoint[0])
        fig = create_Plot_Taktzeit2(fig, rohData, datapoint[1][0], datapoint[1][1])
    fig.update_yaxes(tickformat='%m %dT%H:%M:%S')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("taktzeit1.html", plot=graphJSON)


def txt_loader_tz2(speicherOrt):
    df = pd.read_csv(speicherOrt, delimiter=";")
    df['MIN'] = pd.to_datetime(df["MIN"], unit='s')
    df['MAX'] = pd.to_datetime(df["MAX"], unit='s')
    df['AVG'] = pd.to_datetime(df["AVG"], unit='s')
    df = df.sort_values(by=["TEIL"], ascending=True)
    return df


def create_Plot_Taktzeit2(fig, data, row, col):
    if ((row == 1 or row == 3) and col == 1):
        showlegend = True
    else:
        showlegend = False
    fig.add_scatter(x=data.TEIL, y=data.MIN, name="MIN", row=row, col=col, legendgroup='group1', mode='markers',
                    showlegend=showlegend, marker_color="red").update_layout(height=1200)
    fig.add_scatter(x=data.TEIL, y=data.AVG, name="AVG", row=row, col=col, legendgroup='group2', mode='markers',
                    showlegend=showlegend, marker_color="blue")
    fig.add_scatter(x=data.TEIL, y=data.MAX, name="MAX", col=col, row=row, legendgroup='group3', mode='markers',
                    showlegend=showlegend, marker_color="green")
    fig.add_bar(x=data.TEIL, y=data.FAILURE, name="Fehlerrate", col=col, row=row + 2, marker_color="red",
                showlegend=showlegend)
    return fig


@app.route('/taktzeit4')
def render_Plot_tkt4():
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Document Orientated", "Universell-Relational", "Key-Value-Store", "Proprietäre Datenstruktur")
    )
    data = [["C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/" +
             "AuswertungenCSV_Corn/Analyse_4_Output.csv", [1, 1]
             ],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Paul/004.csv",
                [1, 2],
            ],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Clem/takt4.csv",
                [2, 1]],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungenCSV_Lukas/Taktung4.csv",
                [2, 2]]
            ]
    for datapoint in data:
        rohData = txt_loader_tz4(datapoint[0])
        fig = create_Plot_Taktzeit4(fig, rohData, datapoint[1][0], datapoint[1][1])
    fig.update_xaxes(tickformat='%d %H:%M:%S')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("taktzeit1.html", plot=graphJSON)


def txt_loader_tz4(speicherOrt):
    df = pd.read_csv(speicherOrt, delimiter=";")
    df = df[df.DURATION < 100000]
    df['DURATION'] = pd.to_datetime(df["DURATION"], unit='s')
    # df['DURATION'] = df['DURATION'] - pd.to_datetime(1, unit='d')

    return df


def create_Plot_Taktzeit4(fig, data, row, col):
    showlegend = False
    if (row == 1 and col == 1):
        showlegend = True
    fig.add_scatter(x=data.DURATION, name="Benutzungsdauer", col=col, row=row, mode='markers'
                    , legendgroup='group1', showlegend=showlegend, text=data.LAGER, marker_color="blue").update_layout(
        height=1200)
    return fig


@app.route('/taktzeit5')
def render_Plot_tkt5():
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Document Orientated", "Universell-Relational", "Key-Value-Store", "Proprietäre Datenstruktur"))
    data = [["C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/" +
             "AuswertungenCSV_Corn/Analyse_5_Output.csv", [1, 1], True],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Paul/005.csv",
                [1, 2], False],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Clem/takt5.csv",
                [2, 1], False],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungenCSV_Lukas/Taktung5.csv",
                [2, 2], False]
            ]
    for datapoint in data:
        rohData = txt_loader_tz5(datapoint[0], datapoint[2])
        fig = create_Plot_Taktzeit5(fig, rohData, datapoint[1][0], datapoint[1][1])
    fig.update_yaxes(tickformat='%H:%M:%S')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("taktzeit1.html", plot=graphJSON)


def txt_loader_tz5(speicherOrt, format):
    df = pd.read_csv(speicherOrt, delimiter=";")

    if (format):
        umr = 1000
    else:
        umr = 1
    df = df[(df.MAX / umr) < 86400]
    df['MIN'] = pd.to_datetime(df["MIN"] / umr, unit='s')
    df['MAX'] = pd.to_datetime(df["MAX"] / umr, unit='s')
    df['AVG'] = pd.to_datetime(df["AVG"] / umr, unit='s')
    df = df.groupby('TEIL')
    return df


def create_Plot_Taktzeit5(fig, rohData, row, col):
    for teil in rohData:
        if (row == 1 and col == 1):
            showlegend = True
        else:
            showlegend = False
        data = teil[1]
        fig.add_box(y=data.MIN, name="Min " + teil[0], col=col, row=row, legendgroup='group1', showlegend=showlegend,
                    yaxis="y1")
        fig.add_box(y=data.AVG, name="Avg " + teil[0], col=col, row=row, legendgroup='group2', showlegend=showlegend,
                    yaxis="y1")
        fig.add_box(y=data.MAX, name="MAX " + teil[0], col=col, row=row, legendgroup='group3', showlegend=showlegend,
                    yaxis="y1").update_layout(height=1200)
    return fig


@app.route('/taktzeit7')
def render_Plot_tkt7():
    fig = make_subplots(
        rows=6, cols=2,
        subplot_titles=(
            "MIN Document Orientated", "MIN Universell-Relational", "MIN Key-Value-Store",
            "MIN Proprietäre Datenstruktur",
            "AVG Document Orientated", "AVG Universell-Relational", "AVG Key-Value-Store",
            "AVG Proprietäre Datenstruktur",
            "MAX Document Orientated", "MAX Universell-Relational", "MAX Key-Value-Store",
            "MAX Proprietäre Datenstruktur"
        ))
    data = [["C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/" +
             "AuswertungenCSV_Corn/Analyse_7_Output.csv", [1, 1]],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Paul/007.csv",
                [1, 2]],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Clem/takt7.csv",
                [2, 1]],
            [
                "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungenCSV_Lukas/Taktung7.csv",
                [2, 2]]
            ]
    for datapoint in data:
        rohData = txt_loader_tz7(datapoint[0])
        fig = create_Plot_Taktzeit7(fig, rohData, datapoint[1][0], datapoint[1][1])
    # fig.update_zaxes(tickformat='%H:%M:%S')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("taktzeit1.html", plot=graphJSON)


def txt_loader_tz7(speicherOrt):
    df = pd.read_csv(speicherOrt, delimiter=";")
    df = df[(df.MAX) < 86400]
    df["FROMTO"] = df.FROM + df.TO
    df = df.sort_values(by="FROMTO", ascending=True)
    # df = df.groupby('LINIE')

    return df


def create_Plot_Taktzeit7(fig, rohData, row, col):
    if (False):
        showlegend = True
    else:
        showlegend = False

    fig.add_heatmap(x=rohData.FROM, y=rohData.TO, z=rohData.MIN, col=col, row=row, legendgroup='group1'
                    , showscale=showlegend, zmin=0, zmax=4000).update_layout(height=1800)
    fig.add_heatmap(x=rohData.FROM, y=rohData.TO, z=rohData.AVG, col=col, row=row + 2, legendgroup='group2'
                    , showscale=showlegend, zmin=0, zmax=10000)
    fig.add_heatmap(x=rohData.FROM, y=rohData.TO, z=rohData.MAX, col=col, row=row + 4, legendgroup='group3'
                    , showscale=showlegend, zmin=0, zmax=50000)

    return fig


@app.route('/laufzeit')
def render_Plot_laufzeit():
    fig = make_subplots(
        rows=1, cols=4, shared_yaxes=True,
        subplot_titles=("Analysendauer Proprietäre Datenstruktur"
            , "Analysendauer Universell-Relational", "Analysendauer Schlüssel-Wert-Datenbank",
            "Analysendauer Dokumenten Orientiert",
        ))
    data = [
        [
            "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungenCSV_Corn/DurationAnalysen.csv",
            [1, 4]],
        [
            "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Paul/DurationAnalysen.txt",
            [1, 2]],
        [
            "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Clem/DurationAnalyse.csv",
            [1, 3]],
        [
            "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungenCSV_Lukas/DurationAnalysen.csv",
            [1, 1]]
    ]
    for datapoint in data:
        rohData = txt_loader_laufzeit(datapoint[0])
        fig = create_Plot_laufzeit(fig, rohData, datapoint[1][0], datapoint[1][1])
    # fig.update_zaxes(tickformat='%H:%M:%S')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("taktzeit1.html", plot=graphJSON)


def txt_loader_laufzeit(speicherOrt):
    df = pd.read_csv(speicherOrt, delimiter=";")
    df.Analyse = "Analyse " + df.Analyse.astype(str)
    return df


def create_Plot_laufzeit(fig, rohData, row, col):
    if (row == 1 and row == 1):
        showlegend = True
    else:
        showlegend = False

    #fig.update_xaxes(showticklabels=False)
    fig.add_bar(x=[1,2,3,4,5],y=rohData.Duration, col=col, row=row, legendgroup='group1'
                , showlegend=showlegend, text=rohData.Analyse).update_layout(height=700)

    return fig


@app.route('/about')
def render_Plot_tkt9():
    fig = make_subplots(
        rows=1, cols=1, subplot_titles=("Maximum", "MIN Universell-Relational"))
    data = [["C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/" +
             "AuswertungenCSV_Corn/Analyse_7_Output.csv", [1, 1]]
            ]
    for datapoint in data:
        rohData = txt_loader_tz9(datapoint[0])
        fig = create_Plot_Taktzeit9(fig, rohData, datapoint[1][0], datapoint[1][1])
    # fig.update_zaxes(tickformat='%H:%M:%S')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("taktzeit1.html", plot=graphJSON)


def txt_loader_tz9(speicherOrt):
    df = pd.read_csv(speicherOrt, delimiter=";")
    df = df[(df.MAX) < 86400]
    # df['MIN'] = pd.to_datetime(df["MIN"], unit='s')
    # df['MAX'] = pd.to_datetime(df["MAX"] / umr, unit='s')
    # df['AVG'] = pd.to_datetime(df["AVG"] / umr, unit='s')
    df["FROMTO"] = df.FROM + df.TO
    df = df.sort_values(by="FROMTO", ascending=True)
    # df = df.groupby('LINIE')

    return df


def create_Plot_Taktzeit9(fig, rohData, row, col):
    if (False):
        showlegend = True
    else:
        showlegend = False

    # fig.add_heatmap(x=rohData.FROM, y=rohData.TO, z=rohData.MIN, col=col, row=row, legendgroup='group1'
    #               , zmin=0, zmax=4000).update_layout(width=800,height=800)
    # fig.add_heatmap(x=rohData.FROM, y=rohData.TO, z=rohData.AVG, col=col, row=row, legendgroup='group2'
    #             , zmin=0, zmax=10000).update_layout(width=800,height=800)
    fig.add_heatmap(x=rohData.FROM, y=rohData.TO, z=rohData.MAX, col=col, row=row, legendgroup='group3'
                    , zmin=0, zmax=50000).update_layout(width=800, height=800)

    return fig


@app.route('/durchlauf')
def render_Plot_d():
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=("Input", "Output"), shared_xaxes=True, shared_yaxes=True)
    data = [[
        "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Paul/OutputZeit.csv",
        [1, 2], True],
        [
            "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Paul/InputZeit.csv",
            [1, 1], False],
        [
            "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungenCSV_Corn/Output_Perform.csv",
            [2, 2], False],
        [
            "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Clem/timesIn.txt",
            [3, 1], False],
        [
            "C:/Users/juliu/OneDrive/Studium/WS_20_21/Projekt_Munkelt/projectMunkelt/backendWeb/AuswertungCSV_Clem/timesOut.txt",
            [3, 2], False]
    ]
    for datapoint in data:
        rohData = txt_loader_d(datapoint[0], datapoint[2])
        fig = create_Plot_d(fig, rohData, datapoint[1][0], datapoint[1][1])
    # fig.update_zaxes(tickformat='%H:%M:%S')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("taktzeit1.html", plot=graphJSON)


def txt_loader_d(speicherOrt, format):
    df = pd.read_csv(speicherOrt, delimiter=";")
    return df


def create_Plot_d(fig, rohData, row, col):
    showlegend = False
    if (row == 1 and col == 1):
        showlegend = True
    if (row == 3):
        rohData.TIME = rohData.TIME / 1000

    fig.add_scatter(y=rohData.TIME, col=col, row=row, legendgroup='group1', mode="markers")
    return fig
