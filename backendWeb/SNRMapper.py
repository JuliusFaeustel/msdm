from tabulate import tabulate

class SNRMapper:

    def __init__(self, snr, inputList, outputList):
        self.snr = snr
        self.inputList = inputList
        self.outputList = outputList


    def toHTML(self):
        table= [self.snr,self.inputList,self.outputList]
        return tabulate(table, tablefmt='html', headers= ["SNR","In","Out"])



