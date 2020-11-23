from flask import Flask, request, render_template
import loader
import plotly
import plotly.graph_objs as go
import numpy as np
import json
import plotly.graph_objects as go
import re
import more_itertools

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()


@app.route('/snr', methods=['GET', 'POST'])
def snr():
    dataSet=""
    if request.method == 'POST':
        text = request.form['text']
        snr = text.upper()
        dataSet = loader.findBySNR(snr)

    return render_template("snrLoader.html", content=dataSet)


@app.route('/taktung', methods=['GET'])
def taktung():
    bar = create_plot()
    return render_template("taktung.html", plot=bar)


@app.route('/secondPlot')
def render_realPlot():

    rohData_t =txt_loader()
    bar = create_realPlot(rohData_t)
    return render_template("secondTry.html", plot=bar)

@app.route('/laufzeitFA')
def render_realPlot_FA():

    rohData_t =txt_loader_FA()
    bar = create_realPlot(rohData_t)
    return render_template("laufzeitFA.html", plot=bar)

def txt_loader_FA():
    f = open("faMax.txt", "r")
    first=True
    returnSet=[]
    for line in f:
        if re.search('TEIL:*', line):
            teil=line[:-1]
            if False==first:
               returnSet.append([faListe,werteListe])
            faListe=[]
            werteListe=[]
            first=False

        else:
            tupel = line.split(" ")
            faListe.append(tupel[0])
            werteListe.append(tupel[3])
            tupel=[]
    return returnSet

def txt_loader():
    f = open("diffs.txt", "r")
    first=True
    returnSet=[]
    for line in f:
        if re.search('TEIL:*', line):
            teil=line[:-1]
            if False==first:
               returnSet.append([snrListe,werteListe])
            snrListe=[]
            werteListe=[]
            first=False

        else:
            tupel = line.split(" ")
            snrListe.append(teil)
            werteListe.append(tupel[1][:-1])
            tupel=[]
    return returnSet


def create_realPlot(rohData):
    data = []
    for rdat in rohData:
        snrList=rdat.pop(0)
        time=rdat.pop(0)
        more_itertools.sort_together([time,snrList])
        data.append(go.Scattergl(x=time, y=snrList,mode='markers'))

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def create_plot():
    N = 1000
    random_x = np.random.randn(N)
    random_y = np.random.randn(N)
    random_z = np.random.randn(N)
    random_d = np.random.randn(N)

    # Create a trace
    data = [go.Scatter(
        x=random_x,
        y=random_y,
        mode='markers',
        fillcolor="red",
        name="Testwerte 1",
        hovertext="x-Werte"
    ), go.Scatter(
        x=random_z,
        y=random_d,
        mode='markers',
        fillcolor="red",
        name="Testwerte 2",
        hovertext="y-Werte")]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
