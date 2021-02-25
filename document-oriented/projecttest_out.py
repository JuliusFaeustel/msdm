import pymongo
import pandas as pd
import glob

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["projekttest"]

mycol_null = mydb["empty_out"]

files = glob.glob("C:/Users/liepe/Desktop/Projektseminar/htw/out/*.txt")


def convert_from_ms( milliseconds ):
	seconds, milliseconds = divmod(milliseconds,1000)
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	seconds = seconds + milliseconds/1000
	return days, hours, minutes, seconds

def loadOutput(filename):
    snr = None
    return_df = []
    obj_id = None

    df = pd.read_csv(filename, sep = ';', names = ["SNR", "LINIE","TRÄGER", "MAT", "NAHT", "DistMmX", "DistMmy", "AngleGrad", "LengthMM", "LengthDiffMM", "AngleDiffGrad", "AxisDistMMX", "AxisDistMMY", "AxisDistMM", "RTotalNominal", "RTotalCurrent", "RCount", "Date"], index_col=None)
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

    if (snr == "nan"):
        print("null")
        mycol_null.insert_many(df.to_dict('records'))
    else:
        x = mydb.in_data_embedded.aggregate([{'$match': {'SNR': snr}},{'$project': {'_id':1, 'SNR': 1, 'DATE': 1, 'difference':{'$subtract':[date,'$DATE']}}}])
        return_df = pd.DataFrame()
        for data in x:
            data_x = pd.DataFrame(data, index=[data.get('_id')])
            return_df = return_df.append(data_x)
        if (not return_df.empty):
            return_df = return_df.drop(return_df[return_df.difference < 0].index)
            if (not return_df.empty):
                obj_id = return_df['difference'].idxmin()
                mydb.in_data_embedded.update_one({'_id': obj_id}, {"$addToSet": {"out": dictionary}})
