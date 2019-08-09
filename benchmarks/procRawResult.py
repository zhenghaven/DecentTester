import os
import sys
import argparse
import pandas as pd

def PreProcCsv(oriFilePath, resFilePath):

	inputfile= open(oriFilePath, 'r')
	outputfile = open(resFilePath, "w")

	outputfile.write('Op,Timestamp_ms,Latency_us\n')

	lines = inputfile.readlines()
	for line in lines:
		if 'timestamp(ms)' not in line:
			outputfile.write(line)

	inputfile.close()
	outputfile.close()

def TrimOffWarmUpPhase(dataF, warmUpTime):

	dataF.sort_values(by=['Timestamp_ms'], inplace=True)
	dataF = dataF.reset_index(drop=True)

	length = dataF.shape[0]
	starttime = dataF.iat[0,1]
	trimindex = 0

	for i in range(0, length):
		if dataF.iat[i,1] - starttime >= warmUpTime * 1000:
			trimindex = i
			break

	return dataF[trimindex:].reset_index(drop=True)

def ProcOneResultSet(inputfilepath, warmUpTime, percentile):

	time_ignore = int()

	#Generate intermediate file:
	immedfilepath = inputfilepath + '.tmp'
	PreProcCsv(inputfilepath, immedfilepath)

	dataF = pd.read_csv(immedfilepath)
	os.remove(immedfilepath)

	dataF = TrimOffWarmUpPhase(dataF, warmUpTime)
	#dataF.to_csv(immedfilepath)

	totalOps = dataF.shape[0]
	timeElapsedMs = dataF.iat[totalOps - 1, 1] - dataF.iat[0, 1] #In millisecond
	timeElapsedS = timeElapsedMs / 1000 # In sec
	throughtput = totalOps / timeElapsedS
	latencyPer = dataF.Latency_us.quantile(q=(percentile / 100.0), interpolation='higher')

	return totalOps, timeElapsedMs, throughtput, latencyPer

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--file', required=True)
	parser.add_argument('--warmUpTime', required=True, type=int)
	parser.add_argument('--percentile', required=True, type=int)

	args = parser.parse_args()

	totalOps, timeElapsedMs, throughtput, latencyPer = ProcOneResultSet(args.file, args.warmUpTime, args.percentile)

	print('')
	print('Total OPs:', str(totalOps))
	print('Throughput(ops/s):', str(throughtput))
	print(str(args.percentile), 'Percentil_latency(us):', str(latencyPer))
	print('')

if __name__ == '__main__':
	sys.exit(main())
