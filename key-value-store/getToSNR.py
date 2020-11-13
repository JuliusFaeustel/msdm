import redis
r = redis.Redis(decode_responses=True)

snr = 4152432766450

if r.exists(snr):
    for inData in r.lrange(snr,0,-1):

        inCounter = inData.partition(':')[2]
        
        allInfo = r.hgetall(inData)
        print("In"+" : "+allInfo.get("Begin"))

        inDatensatz = str(snr)+":"+inCounter

        for outData in r.lrange(inDatensatz,1,-1):
            allOutInfo = r.hgetall(outData)
            print("Out"+": "+allOutInfo.get("Date"))

else:
    print('SNR nicht gefunden')
    
