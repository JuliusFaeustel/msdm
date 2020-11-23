import pymongo
import pandas as pd
import glob
import numpy as np
import time

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekttest"]

mycol = mydb["simulation"]

files = glob.glob("C:/Users/liepe/Desktop/Projektseminar/htw/in/*.txt")
files_out = glob.glob("C:/Users/liepe/Desktop/Projektseminar/htw/out/*.txt")

rows = []
i = 0

print(type(files))

while i < len(files):
    print("Reading Input \n")
    df = pd.read_csv(files[i], sep = ';', names = ["DATE", "FA", "NR", "TEIL", "SNR", "LINIE", "E","ScanE","MessageE","A2","V2","A1","V1","UseM3","UseM1","UseM2","Delta","Fehler","Span","ChargeM1","ChargeM2","ChargeM3","ScanA","MessungA","LagerIn","LagerOut","Begin"], index_col=None)
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

    print("Sleeeping 5 seconds")
    time.sleep(10)

    print("Reading output \n\n")
    df = pd.read_csv(files_out[i], sep = ';', names = ["SNR", "LINIE","TRÄGER", "MAT", "NAHT", "DistMmX", "DistMmy", "AngleGrad", "LengthMM", "LengthDiffMM", "AngleDiffGrad", "AxisDistMMX", "AxisDistMMY", "AxisDistMM", "RTotalNominal", "RTotalCurrent", "RCount", "Date"], index_col=None)
    df.reset_index(drop = True, inplace = True)
    df['SNR'] = df['SNR'].astype(str)
    df['LINIE'] = df['LINIE'].astype(str)
    df['TRÄGER'] = df['TRÄGER'].astype(bool)
    df['MAT'] = df['MAT'].astype(bool)
    df['NAHT'] = df['NAHT'].astype(bool)
    df['AngleGrad'] = df['AngleGrad'].astype(float)
    df['LengthMM'] = df['LengthMM'].astype(float)
    df['LengthDiffMM'] = df['LengthDiffMM'].astype(float)
    df['AngleDiffGrad'] = df['AngleDiffGrad'].astype(float)
    df['AxisDistMMX'] = df['AxisDistMMX'].astype(float)
    df['AxisDistMMY'] = df['AxisDistMMY'].astype(float)
    df['AxisDistMM'] = df['AxisDistMM'].astype(float)
    df['RTotalNominal'] = df['RTotalNominal'].astype(float)
    df['RTotalCurrent'] = df['RTotalCurrent'].astype(float)
    df['RCount'] = df['RCount'].astype(float)
    df['Date'] = pd.to_datetime(df['Date'])
    snr = df.iloc[0]['SNR']
    LINIE = df.iloc[0]['LINIE']
    date = df.iloc[0]['Date']

    dictionary = {
        "SNR": snr,
        "LINIE": LINIE,
        "TRÄGER": bool(df.iloc[0]["TRÄGER"]),
        "MAT": bool(df.iloc[0]["MAT"]),
        "NAHT": bool(df.iloc[0]["NAHT"]),
        "AngleGrad": df.iloc[0]["AngleGrad"],
        "LengthMM": df.iloc[0]["LengthMM"],
        "LengthdiffMM": df.iloc[0]['LengthDiffMM'],
        'AngleDiffGrad': df.iloc[0]['AngleDiffGrad'],
        'AxisDistMMX': df.iloc[0]['AxisDistMMX'],
        'AxisDistMMY': df.iloc[0]['AxisDistMMY'],
        'AxisDistMM': df.iloc[0]['AxisDistMM'],
        'RTotalNominal': df.iloc[0]['RTotalNominal'],
        'RTotalCurrent': df.iloc[0]['RTotalCurrent'],
        'RCount': df.iloc[0]['RCount'],
        'Date': df.iloc[0]['Date'],
    }

    if (df['SNR'][0] == np.nan):
        mycol_null.insert_many(df.to_dict('records'))
    else:
        x = mydb.simulation.aggregate([{'$match': {'SNR': snr}},{'$project': {'_id':1, 'SNR': 1, 'DATE': 1, 'difference':{'$subtract':[date,'$DATE']}}}])
        # mydb.in_data_embedded.update_one({"SNR": snr}, {"$addToSet": {"out": dictionary}})
        return_df = pd.DataFrame()
        for data in x:
            data_x = pd.DataFrame(data, index=[data.get('_id')])
            return_df = return_df.append(data_x)
    if (not return_df.empty):        
        return_df = return_df.drop(return_df[return_df.difference < 0].index)
        if (not return_df.empty):  
            obj_id = return_df['difference'].idxmin() 
            mydb.simulation.update_one({'_id': obj_id}, {"$addToSet": {"out": dictionary}})    
    time.sleep(1)
    i = i+1
    print(i)

    