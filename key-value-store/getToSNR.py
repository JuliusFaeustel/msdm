import redis
r = redis.Redis(decode_responses=True)

snr = 2040034481631
con = []

for snrCon in r.scan_iter(match=str(snr)+':*',count=300000):
    con.append(snrCon)

if r.exists(snr):
    for inData in r.lrange(snr,0,-1):

        inCounter = inData.partition(':')[2]
        
        allInfo = r.hgetall(inData)
        print("In"+" : "+allInfo.get("Begin"))

        inDatensatz = str(snr)+":"+inCounter

        for outData in r.lrange(inDatensatz,1,-1):
            allOutInfo = r.hgetall(outData)
            print("Out"+": "+allOutInfo.get("Date"))

    print(con)

else:
    print('SNR nicht gefunden')
    
