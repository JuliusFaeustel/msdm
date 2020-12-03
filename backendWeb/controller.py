from flask import Flask, request, render_template
import loader
import plotly
import json
import plotly.graph_objects as go
import re
import datetime
import statistics

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

@app.route('/taktzeit1')
def render_realPlot():

    rohData = txt_loader_tz1()
    bar = create_Plot_Taktzeit(rohData)
    return render_template("taktzeit1.html", plot=bar)

@app.route('/laufzeitFA')
def render_realPlot_FA():

    rohData_t =txt_loader_FA()
    bar = create_Laufzeit_Artikel(rohData_t)
    return render_template("laufzeitFA.html", plot=bar)

def txt_loader_FA():
    f = open("AuswertungCSV/faMax.txt", "r")
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


def txt_loader_tz1():
    f = open("AuswertungCSV/takt1.txt", "r")
    first=True
    returnSet=[]
    for line in f:
        if re.search('TEIL:*', line):
            teil=line[:-1]
            if False==first:
               returnSet.append([teil,faListe,maxListe,minListe,mittelListe])
            faListe=[]
            maxListe=[]
            minListe=[]
            mittelListe=[]
            first=False

        else:
            tupel = line.split(" ")
            faListe.append(tupel[0])
            maxtime=datetime.datetime.strptime(tupel[2], '%H:%M:%S').time()
            maxListe.append(maxtime.hour/60+maxtime.minute+maxtime.second/100)
            mintime = datetime.datetime.strptime(tupel[3], '%H:%M:%S').time()
            minListe.append(mintime.hour / 60 + mintime.minute + mintime.second / 100)
            mittelListe.append(float(tupel[4][:-2]))
            tupel=[]
    returnSet.append([teil, faListe, maxListe, minListe, mittelListe])
    return returnSet

def create_Plot_Taktzeit(rohData):
    data = []
    #fig = go.Figure(layout=go.Layout(yaxis=dict(range=[0, 1000])))
    #layout = go.Layout(yaxis={'tickformat': '%H:%M:%S'})
    #layout = go.Layout(yaxis={'type': 'linear'})
    fig = go.Figure().update_layout(title={'text':'Taktzeit Analyse in Minuten', 'xanchor': 'center'})

    for rdat in rohData:
        teil=rdat.pop(0)
        faListe = rdat.pop(0)
        maxListe = rdat.pop(0)
        minListe = rdat.pop(0)
        mittelListe = rdat.pop(0)
        try:
            print(teil)
            print(statistics.mean(minListe))
            print(statistics.mean(mittelListe))
            print(statistics.mean(maxListe))
        except:
            print("error")
        fig.add_box(y=minListe, name="min" + teil)
        fig.add_box(y=mittelListe, name="Mittel" + teil, yaxis='y')
        fig.add_box(y=maxListe, name="max" + teil, yaxis='y')





    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def create_Laufzeit_Artikel(rohData):
    data = []
    for rdat in rohData:
        snrList=rdat.pop(0)
        time=rdat.pop(0)
        data.append(go.Box(y=time))

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

