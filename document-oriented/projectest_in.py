import pymongo
import pandas as pd
import glob
import numpy as np

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekttest"]

mycol = mydb["in_data_embedded"]

files = glob.glob("C:/Users/liepe/Desktop/Projektseminar/htw/in/*.txt")

print(len(files))

rows = []
i = 0

for filename in files:
    df = pd.read_csv(filename, sep = ';', names = ["DATE", "FA", "NR", "TEIL", "SNR", "LINIE", "E","ScanE","MessageE","A2","V2","A1","V1","UseM3","UseM1","UseM2","Delta","Fehler","Span","ChargeM1","ChargeM2","ChargeM3","ScanA","MessungA","LagerIn","LagerOut","Begin"], index_col=None)
    df.reset_index(drop = True, inplace = True)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['Begin'] = pd.to_datetime(df['Begin'])
    df['FA'] = df['FA'].astype(str)
    df['SNR'] = df['SNR'].astype(str)
    df['LINIE'] = df['LINIE'].astype(str)
    df['E'] = df['E'].astype(str)
    df['ScanE'] = df['ScanE'].astype(bool)
    df['MessageE'] = df['MessageE'].astype(bool)
    df['V2'] = df['V2'].astype(np.float64)
    df['V1'] = df['V1'].astype(np.float64)
    df['UseM3'] = df['UseM3'].astype(np.float64)
    df['UseM2'] = df['UseM2'].astype(np.float64)
    df['UseM1'] = df['UseM1'].astype(np.float64)
    df['Delta'] = df['Delta'].astype(np.float64)
    df['Fehler'] = df['Fehler'].astype(int)
    df['Span'] = df['Span'].astype(int)
    df['ChargeM1'] = df['ChargeM1'].astype(str)
    df['ChargeM2'] = df['ChargeM2'].astype(str)
    df['ChargeM3'] = df['ChargeM3'].astype(str)
    df['ScanA'] = df['ScanA'].astype(bool)
    df['MessungA'] = df['MessungA'].astype(bool)
    df['LagerIn'] = df['LagerIn'].astype(str)
    df['LagerOut'] = df['LagerOut'].astype(str)
    df['Begin'] = pd.to_datetime(df['Begin'])
    mycol.insert_many(df.to_dict('records'))
    i = i+1
    print(i)

print("Finished uploading all Data")