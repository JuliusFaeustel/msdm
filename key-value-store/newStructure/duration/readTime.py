import redis
from datetime import datetime
from time import process_time_ns

r = redis.Redis(decode_responses=True)

print(r.slowlog_len())
timeLog = r.slowlog_get(r.slowlog_len())
timeGes = 0
for time in timeLog:
    timeGes = timeGes + time['duration']
print(timeGes/10**6)
