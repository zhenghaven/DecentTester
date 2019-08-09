import pandas as pd 
import sys
import os

inputfilepath = sys.argv[1]
outputfilepath = inputfilepath + '.opt'
time_ignore = int(sys.argv[2])

# inputfilepath = '/Users/xiaoweic/Desktop/Attempt_01_02_40.csv'
# outputfilepath = '/Users/xiaoweic/Desktop/Attempt_01_02_40.csv.opt'
# time_ignore = 20

inputfile= open(inputfilepath, 'r')
lines = inputfile.readlines()

outputfile = open(outputfilepath, "w")
outputfile.write('op,timestamp(ms),latency(us)\n')
for line in lines:
    if 'timestamp(ms)' not in line:
        outputfile.write(line)

inputfile.close()
outputfile.close()

data = pd.read_csv(outputfilepath) 
data.sort_values(by=['timestamp(ms)'], inplace=True)
data = data.reset_index(drop=True)

length = data.shape[0]
starttime = data.iat[0,1]
trimindex = 0 

for i in range(0,length):
    if data.iat[i,1] - starttime >= time_ignore*1000:
        trimindex = i
        break

data = data[trimindex:]
data = data.reset_index(drop=True)
throughtput = data.shape[0]/((data.iat[data.shape[0]-1,1]-data.iat[0,1])/1000)

data.sort_values(by=['latency(us)'], inplace=True)
data = data.reset_index(drop=True)
length = data.shape[0]
latency95 = data.iat[int(length*0.95//1),2] 

print('Throughput:'+ str(throughtput))
print('95Percentil_latency:' + str(latency95))
os.remove(outputfilepath)