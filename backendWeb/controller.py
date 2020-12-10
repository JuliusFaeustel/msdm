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
    rohData = txt_loader_tz1()
    bar = create_Plot_Taktzeit1(rohData)
    return render_template("taktzeit1.html", plot=bar)


def txt_loader_tz1():
    f = open("AuswertungCSV/takt1.txt", "r")
    first = True
    returnSet = []
    for line in f:
        if re.search('TEIL:*', line):
            if False == first:
                returnSet.append([teil, faListe, maxListe, minListe, mittelListe])
            teil = line[:-1]
            faListe = []
            maxListe = []
            minListe = []
            mittelListe = []
            first = False

        else:
            tupel = line.split(";")
            faListe.append(tupel[0])
            maxtime = datetime.datetime.strptime(tupel[2], '%H:%M:%S').time()
            maxListe.append(maxtime.hour / 60 + maxtime.minute + maxtime.second / 100)
            mintime = datetime.datetime.strptime(tupel[3], '%H:%M:%S').time()
            minListe.append(mintime.hour / 60 + mintime.minute + mintime.second / 100)
            mittelListe.append(float(tupel[4][:-2]))
            tupel = []
    returnSet.append([teil, faListe, maxListe, minListe, mittelListe])
    return returnSet


def create_Plot_Taktzeit1(rohData):
    data = []
    # fig = go.Figure(layout=go.Layout(yaxis=dict(range=[0, 1000])))
    # layout = go.Layout(yaxis={'tickformat': '%H:%M:%S'})
    # layout = go.Layout(yaxis={'type': 'linear'})
    fig = go.Figure().update_layout(title={'text': 'Taktzeit Analyse in Minuten', 'xanchor': 'center'})

    for rdat in rohData:
        teil = rdat.pop(0)
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


@app.route('/taktzeit2', methods=['GET', 'POST'])
def render_Plot_tkt2():
    selected = []
    if request.method == 'POST':
        if request.form.get('max'):
            selected.append("max")
        if request.form.get('min'):
            selected.append("min")
        if request.form.get('avg'):
            selected.append("avg")
        if request.form.get('fail'):
            selected.append("fail")
    rohData = txt_loader_tz2()
    bar = create_Plot_Taktzeit2(rohData, selected)
    return render_template("taktzeit2.html", plot=bar)


def txt_loader_tz2():
    f = open("AuswertungCSV/takt2.txt", "r")
    input= pd.read_csv("AuswertungCSV/takt2.txt", delimiter=";")
    input["MIN"] = pd.to_datetime(input["MIN"])
   # input["MAX"] = pd.to_datetime(input["MAX"])
    input["AVG"] = pd.to_datetime(input["AVG"])
    print( pd.to_datetime('04/12/10 21:12:35', format='%d/%m/%y %H:%M:%S').strftime('%d-%H:%M:%S'))
    return input


def create_Plot_Taktzeit2(rohData, selected):
    fig = go.Figure().update_layout(title={'text': 'Analyse 2', 'xanchor': 'center'},yaxis={
        'type': 'date',
        'tickformat': '%H:%M:%S'
    },yaxis2={'overlaying':'y','side':'right'})
    teil=rohData["TEIL"]
   # if "max" in selected:
     #   fig.add_scatter(x=teil, y=maxtime, name="maximale Zeit", mode="markers")
    if "min" in selected:
        fig.add_scatter(x=teil, y=rohData["MIN"], name="minimale Zeit", mode="markers")
    if "avg" in selected:
        fig.add_scatter(x=teil, y=rohData["AVG"], name="durchschnittliche Zeit", mode="markers")
    if "fail" in selected:
        fig.add_scatter(x=teil, y=rohData["FAILURE"], name="Failure Rate", mode="markers",
                        yaxis="y2" ,marker_color="rgba(255,0,0,.9)")


    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/taktzeit4', methods=['GET', 'POST'])
def render_Plot_tkt4():
    rohData = txt_loader_tz4()
    bar = create_Plot_Taktzeit4(rohData)
    return render_template("taktzeit1.html", plot=bar)


def txt_loader_tz4():
    input= pd.read_csv("AuswertungCSV/takt4.txt", delimiter=";")
    input["Start"] = pd.to_datetime(input["Start"])
    input["Ende"] = pd.to_datetime(input["Ende"])
    input["DauerinSek"] =input["DauerinSek"]/60
    #print( pd.to_datetime('04/12/10 21:12:35', format='%d/%m/%y %H:%M:%S').strftime('%d-%H:%M:%S'))
    return input


def create_Plot_Taktzeit4(rohData):

    fig = make_subplots(cols=2)
    fig.add_box(y=rohData["DauerinSek"], name="minimale Zeit in Minuten",row=1,col=1)
    fig.add_box(y=rohData["Anzahl"], name="Anzahl der Durchläufe", yaxis="y2",row=1,col=2)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

@app.route('/taktzeit5')
def render_Plot_tkt5():
    rohData = txt_loader_tz5()
    bar = create_Plot_Taktzeit5(rohData)
    return render_template("taktzeit1.html", plot=bar)


def txt_loader_tz5():
    f = open("AuswertungCSV/takt5.txt", "r")
    first = True
    returnSet = []
    for line in f:
        if re.search('TEIL:*', line):
            if False == first:
                returnSet.append([teil, lagerListe, minListe, avgListe])
            teil = line[:-1]
            lagerListe = []
            maxListe = []
            minListe = []
            avgListe = []
            first = False

        else:
            tupel = line.split(";")
            lagerListe.append(tupel[0])
            #maxtime = datetime.datetime.strptime(tupel[1], '%H:%M:%S').time()
            #maxListe.append(maxtime.hour / 60 + maxtime.minute + maxtime.second / 100)
            mintime = datetime.datetime.strptime(tupel[2], '%H:%M:%S').time()
            minListe.append(mintime.hour / 60 + mintime.minute + mintime.second / 100)
            #mittelListe.append(float(tupel[4][:-2]))
            tupel = []
    returnSet.append([teil, lagerListe, minListe, avgListe])
    return returnSet


def create_Plot_Taktzeit5(rohData):
    data = []
    # fig = go.Figure(layout=go.Layout(yaxis=dict(range=[0, 1000])))
    # layout = go.Layout(yaxis={'tickformat': '%H:%M:%S'})
    # layout = go.Layout(yaxis={'type': 'linear'})
    fig = go.Figure().update_layout(title={'text': 'Taktzeit Analyse in Minuten', 'xanchor': 'center'})
    for rdat in rohData:
        teil = rdat.pop(0)
        faListe = rdat.pop(0)
        #maxListe = rdat.pop(0)
        minListe = rdat.pop(0)
        #mittelListe = rdat.pop(0)
        fig.add_box(y=minListe, name="min" + teil)
        #fig.add_box(y=mittelListe, name="Mittel" + teil, yaxis='y')
        #fig.add_box(y=maxListe, name="max" + teil, yaxis='y')

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON



@app.route('/taktzeit7')
def render_Plot_tkt7():
    rohData = txt_loader_tz7()
    bar = create_Plot_Taktzeit7(rohData)
    return render_template("taktzeit1.html", plot=bar)


def txt_loader_tz7():
    f = open("AuswertungCSV/takt7.txt", "r")
    first = True
    returnSet = []
    for line in f:
        if re.search('LINIE:*', line):
            if False == first:
                returnSet.append([teil, inList,outList, minListe])
            teil = line[:-1]
            faListe = []
            maxListe = []
            minListe = []
            avgListe = []
            outList = []
            inList = []
            first = False

        else:
            tupel = line.split(";")
            inOut= tupel[0].split(":")
            inValue=inOut[0]
            inList.append(inValue)
            outValue=inOut[1]
            outList.append(outValue)

            try:
                mintime = datetime.datetime.strptime(tupel[2], '%H:%M:%S').time()
                minListe.append(mintime.hour / 60 + mintime.minute + mintime.second / 100)
            except:
                print("Error")
            tupel = []
    returnSet.append([teil, inList,outList, minListe])
    return returnSet


def create_Plot_Taktzeit7(rohData):
    fig = go.Figure().update_layout(title={'text': 'Taktzeit Analyse in Minuten', 'xanchor': 'center'})
    for rdat in rohData:
        teil = rdat.pop(0)
        inListe = rdat.pop(0)
        outListe=rdat.pop(0)
        minListe = rdat.pop(0)
        fig.add_scatter3d(x=inListe,y=outListe,z=minListe, name="min" + teil, mode ="markers")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

