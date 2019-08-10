import os
import sys
import argparse
import progressbar
import pandas as pd

COLUMN_NAMES = ['Name_Prefix', 'Attempt', 'Num_of_Node', 'Num_of_Thread', 'Ops_per_Session', 'Ops', 'Time_Elapsed_ms', 'Throughput_op_per_s', 'Percentile_Latency_us']

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

	return [totalOps, timeElapsedMs, throughtput, latencyPer]

def ParseFileName(filepath):

	root, ext = os.path.splitext(filepath)
	filename = os.path.basename(root)

	components = filename.split('_')

	return components

def SummaryOneResultSet(filepath, warmUpTime, percentile):

	filenameRes = ParseFileName(filepath)
	dataRes = ProcOneResultSet(filepath, warmUpTime, percentile)

	return filenameRes + dataRes

def main():

	print()

	parser = argparse.ArgumentParser()
	parser.add_argument('--dir', required=True)
	parser.add_argument('--warmUpTime', required=True, type=int)
	parser.add_argument('--percentile', required=True, type=int)
	parser.add_argument('--out', required=True)

	args = parser.parse_args()

	#Convert directory path to absolute path
	dirPath = os.path.abspath(args.dir)

	if (not os.path.exists(dirPath)) or (os.path.isfile(dirPath)):
		print('FATAL_ERR:', 'The input directory:', dirPath, 'does not exist, or it is a file!')
		exit(-1)

	outPath = os.path.abspath(args.out)

	if os.path.exists(outPath):
		print('FATAL_ERR:', 'The output file path:', outPath, 'already exist!')
		exit(-1)

	rows = []

	print('INFO:', 'Processing...')

	proBar = progressbar.ProgressBar()

	#iterate through files in the directory
	for filename in proBar(os.listdir(dirPath)):

		#looking for all csv files
		if filename.endswith(".csv"):

			filepath = os.path.join(dirPath, filename)

			#Make sure it is a file (not a directory)
			if os.path.isfile(filepath):

				#print('.', end='', flush=True)
				row = SummaryOneResultSet(filepath, args.warmUpTime, args.percentile)
				rows.append(row)

	summaryDataF = pd.DataFrame(data=rows, columns=COLUMN_NAMES)

	print('INFO:', 'Writting results into', outPath, '...')

	summaryDataF.to_csv(outPath)

	print()

if __name__ == '__main__':
	sys.exit(main())
