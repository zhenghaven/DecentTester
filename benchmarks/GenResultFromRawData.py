import os
import io
import sys
import argparse
import threading
import progressbar as pbar
import pandas as pd
from python_utils.terminal import get_terminal_size

COLUMN_NAMES = ['Name_Prefix', 'Attempt', 'Num_of_Node', 'Num_of_Thread', 'Ops_per_Session', 'Ops', 'Time_Elapsed_ms', 'Throughput_op_per_s', 'Percentile_Latency_us', 'Overall_Svr_CPU_perc', 'Svr_Node_Proc_CPU_perc']

COLUMN_TYPES = {'Attempt': 'int32', 'Num_of_Node': 'int32', 'Num_of_Thread': 'int32', 'Ops_per_Session': 'int32'}

CSV_POSTFIX = '.csv'

COL_NAME_TIMESTAMP = 'timestamp_ms'
COL_NAME_LATENCY = 'latency_us'

TERM_WIDTH = int(get_terminal_size()[0] * (2/3))

PBAR_WIDGETS = [
	pbar.Percentage(), ' (', pbar.SimpleProgress(), ') ',
	pbar.Bar(marker='█', left=' |', right='| ', fill='▁'),
	' ', pbar.Timer(),
	' | ETA ', pbar.ETA()
]

def GetYcsbImCsvData(dirPath, resultId):

	ycsbCsvPath = os.path.join(dirPath, resultId + '.ycsb.csv')

	inputfile= open(ycsbCsvPath, 'r')
	outputfile = io.StringIO()

	outputfile.write('op,' + COL_NAME_TIMESTAMP + ',' + COL_NAME_LATENCY + '\n')

	for line in inputfile.readlines():
		if 'timestamp(ms)' not in line:
			outputfile.write(line)

	inputfile.close()

	outputfile.seek(0)
	dataF = pd.read_csv(outputfile)

	outputfile.close()

	return dataF

def GetServerStatCsvData(dirPath, resultId):

	serverCsvPath = os.path.join(dirPath, resultId + '.SvrStat.csv')
	dataF = pd.read_csv(serverCsvPath)
	return dataF

def GetTimestampRange(dataF, tsColName):

	dataF.sort_values(by=[tsColName], inplace=True)
	dataF.reset_index(drop=True, inplace=True)

	recCount = dataF.shape[0]

	if recCount == 0:
		return [0, 0]

	starttime = dataF[tsColName][0]
	endtime = dataF[tsColName][recCount - 1]

	return [starttime, endtime]

def TrimOffByTimeRange(dataF, tsColName, startTs, endTs):

	dataF.sort_values(by=[tsColName], inplace=True)
	dataF.reset_index(drop=True, inplace=True)

	recCount = dataF.shape[0]

	startIdx = 0
	endIdx = recCount

	for ts in dataF[tsColName]:
		if ts < startTs:
			startIdx = startIdx + 1
		else:
			break

	for ts in reversed(dataF[tsColName]):
		if ts > endTs:
			endIdx = endIdx - 1
		else:
			break

	return dataF[startIdx:endIdx].reset_index(drop=True)

def ProcSvrCsv(dataF, tsColName, overallColName):

	avgs = dataF.drop([tsColName], axis=1).mean(axis=0)

	return [avgs[overallColName], avgs.drop(overallColName).mean()]

def GetResultIdList(dirPath):

	idList = []

	print('INFO:', 'Looking for result files...')
	for filename in pbar.progressbar(os.listdir(dirPath), widgets=PBAR_WIDGETS, term_width=TERM_WIDTH):

		#looking for all txt files
		if filename.endswith(".txt") and os.path.isfile(os.path.join(dirPath, filename)):
			root, ext = os.path.splitext(filename)
			idList.append(root)

	print('INFO:', 'Found', len(idList), 'items.')

	return idList

class ResultParserThread(threading.Thread):

	def __init__(self, sema, dirPath, resId, warnupT, terminateT, percentile):
		super(ResultParserThread, self).__init__()
		self.sema = sema
		self.dirPath = dirPath
		self.resId = resId
		self.warnupT = warnupT
		self.terminateT = terminateT
		self.percentile = percentile
		self.idRes = []
		self.ycsbRes = []
		self.serverRes = []
		self.error = None

	def ProcessResultSet(self):

		#Process result ID
		self.idRes = self.resId.split('_')
		self.idRes = ['999999999' if w == '-1' else w for w in self.idRes]

		#Process YCSB CSV data
		ycsbDataF = GetYcsbImCsvData(self.dirPath, self.resId)
		ycsbTimeRange = GetTimestampRange(ycsbDataF, COL_NAME_TIMESTAMP)

		startTs = ycsbTimeRange[0] + (self.warnupT * 1000)
		endTs = ycsbTimeRange[1] - (self.terminateT * 1000)

		ycsbDataF = TrimOffByTimeRange(ycsbDataF, COL_NAME_TIMESTAMP, startTs, endTs)
		ycsbTimeRange = GetTimestampRange(ycsbDataF, COL_NAME_TIMESTAMP)

		totalOps = ycsbDataF.shape[0]
		timeElapsedMs = ycsbTimeRange[1] - ycsbTimeRange[0] #In millisecond
		timeElapsedS = timeElapsedMs / 1000 # In sec
		throughtput = totalOps / timeElapsedS
		latencyPer = ycsbDataF[COL_NAME_LATENCY].quantile(q=(self.percentile / 100.0), interpolation='higher')

		self.ycsbRes = [totalOps, timeElapsedMs, throughtput, latencyPer]

		#Process server system status data
		svrDataF = GetServerStatCsvData(self.dirPath, self.resId)
		svrDataF = TrimOffByTimeRange(svrDataF, COL_NAME_TIMESTAMP, startTs, endTs)

		self.serverRes = ProcSvrCsv(svrDataF, COL_NAME_TIMESTAMP, 'overall_percent')

	def run(self):

		try:

			self.sema.acquire()
			self.ProcessResultSet()
			self.sema.release()

		except Exception as e:
			self.error = e

	def JoinAndGetResult(self, timeout=None):

		self.join(timeout)

		if self.is_alive():
			raise RuntimeError('Failed to stop the thread')
		elif self.error != None:
			raise self.error
		else:
			return self.idRes + self.ycsbRes + self.serverRes

def main():

	print()

	parser = argparse.ArgumentParser()
	parser.add_argument('--dir', required=True, type=str)
	parser.add_argument('--warmUpTime', required=True, type=int)
	parser.add_argument('--endTime', required=True, type=int)
	parser.add_argument('--percentile', required=True, type=int)
	parser.add_argument('--out', required=True, type=str)

	args = parser.parse_args()

	#Convert directory path to absolute path
	dirPath = os.path.abspath(args.dir)

	if (not os.path.exists(dirPath)) or (os.path.isfile(dirPath)):
		print('FATAL_ERR:', 'The input directory:', dirPath, 'does not exist, or it is a file!')
		exit(-1)

	outPath = ''
	if args.out.endswith(CSV_POSTFIX):
		outPath = os.path.abspath(args.out)
	else:
		outPath = os.path.abspath(args.out + CSV_POSTFIX)

	if os.path.exists(outPath):
		print('FATAL_ERR:', 'The output file path:', outPath, 'already exist!')
		exit(-1)

	rows = []

	idList = GetResultIdList(dirPath)
	print('INFO:', 'Processing raw data...')

	numOfThreads = (os.cpu_count()) if os.cpu_count() != None else 1
	sema = threading.Semaphore(value=numOfThreads)
	parThreadList = []
	for id in idList:
		parThread = ResultParserThread(sema, dirPath, id, args.warmUpTime, args.endTime, args.percentile)
		parThread.start()
		parThreadList.append(parThread)

	#Collecting results
	print('INFO:', 'Collecting results...')
	for parThread in pbar.progressbar(parThreadList, widgets=PBAR_WIDGETS, term_width=TERM_WIDTH):
		rows.append(parThread.JoinAndGetResult())

	summaryDataF = pd.DataFrame(data=rows, columns=COLUMN_NAMES)

	summaryDataF = summaryDataF.astype(COLUMN_TYPES)

	summaryDataF.to_csv(outPath, index=False)

	print()

if __name__ == '__main__':
	sys.exit(main())
