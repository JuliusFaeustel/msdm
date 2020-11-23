import redis
from SNRMapper import SNRMapper
from tabulate import tabulate

r = redis.Redis(decode_responses=True)


def findBySNR(SNR):
    outdata = []
    indata = []
    if r.exists(SNR):
        for inData in r.lrange(SNR, 0, -1):
            inCounter = inData.partition(':')[2]

            allInfo = r.hgetall(inData)
            indata.append("In:" + allInfo.get("Begin"))

            inDatensatz = str(SNR) + ":" + inCounter
            for outData in r.lrange(inDatensatz, 1, -1):
                allOutInfo = r.hgetall(outData)
                outdata.append("Out:" + allOutInfo.get("Date"))

        table = [[SNR, indata, outdata]]
        return tabulate(table, tablefmt='html', headers=["SNR", "In", "Out"])
    else:
        return 'SNR nicht gefunden'
