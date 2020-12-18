import matplotlib.pyplot as plt
import numpy as np

def boxPlot(datDict):
    fig = plt.figure(1,figsize=(9,6)) #Größe Ausgabefenster
    ax = fig.add_subplot(111)
    ax.set_xticklabels(datDict.keys())
    bp = ax.boxplot(datDict.values(), showmeans=False, showfliers=False)
    plt.show()

def boxPlot4(dauerList):
    fig = plt.figure(1,figsize=(9,6)) #Größe Ausgabefenster
    ax = fig.add_subplot(111)
    bp = ax.boxplot(dauerList, showmeans=False, showfliers=False)
    plt.show()
