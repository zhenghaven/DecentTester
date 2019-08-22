import os
import io
import sys
import psutil
import openpyxl
import argparse
import threading
import sqlalchemy
import progressbar
import pandas as pd

COLUMN_NAMES = ['Name_Prefix', 'Attempt', 'Num_of_Node', 'Num_of_Thread', 'Ops_per_Session', 'Ops', 'Time_Elapsed_ms', 'Throughput_op_per_s', 'Percentile_Latency_us', 'Overall_Svr_CPU_perc', 'Svr_Node_Proc_CPU_perc']

COLUMN_TYPES = {'Attempt': 'int32', 'Num_of_Node': 'int32', 'Num_of_Thread': 'int32', 'Ops_per_Session': 'int32'}

EXCEL_POSTFIX = '.xlsx'

DEFAULT_TABLE_NAME = 'FullTestResult'

COL_NAME_TIMESTAMP = 'timestamp_ms'
COL_NAME_LATENCY = 'latency_us'

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

def ConstructIndexSheet(sqlList):

	rows = [['Sheet_01', 'Full summary']]
	i = 2
	for sqlQuery in sqlList:
		rows.append([('Sheet_' + '{0:02d}'.format(i)), sqlQuery])

	return pd.DataFrame(data=rows, columns=['Sheet', 'Content'])

def ConstructExcelSheets(summaryDataF, sqlList):

	dataFs = [ConstructIndexSheet(sqlList), summaryDataF]

	if sqlList != None and len(sqlList) > 0:

		#Create an in-memory SQLite database.
		engine = sqlalchemy.create_engine('sqlite://', echo=False)

		summaryDataF.to_sql(DEFAULT_TABLE_NAME, con=engine, if_exists='replace')

		print('INFO:', 'Executing SQL queries...')

		proBar = progressbar.ProgressBar()

		for sqlQuery in proBar(sqlList):
			sqlRes = pd.read_sql_query(sqlQuery, con=engine)
			dataFs.append(sqlRes)

	return dataFs

def WriteExcel(outPath, dataFs):

	print('INFO:', 'Writting results into', outPath, '...')

	proBar = progressbar.ProgressBar()

	with pd.ExcelWriter(outPath) as writer:
		i = 0
		for dataF in proBar(dataFs):
			if i == 0:
				dataF.to_excel(writer, sheet_name='Index')
			else:
				dataF.to_excel(writer, sheet_name=('Sheet_' + '{0:02d}'.format(i)))

			i += 1

def ReadSqlQueries(sqlPath):

	if sqlPath == None:

		return []

	else:

		sqlFile = open(sqlPath, 'r')
		sqlQueries = sqlFile.readlines()
		sqlFile.close()
		return sqlQueries

def GetResultIdList(dirPath):

	idList = []

	print('INFO:', 'Looking for result files...')
	proBar = progressbar.ProgressBar()
	for filename in proBar(os.listdir(dirPath)):

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
	parser.add_argument('--dir', required=True)
	parser.add_argument('--warmUpTime', required=True, type=int)
	parser.add_argument('--percentile', required=True, type=int)
	parser.add_argument('--out', required=True)
	parser.add_argument('--sql', required=False)

	args = parser.parse_args()

	#Convert directory path to absolute path
	dirPath = os.path.abspath(args.dir)

	if (not os.path.exists(dirPath)) or (os.path.isfile(dirPath)):
		print('FATAL_ERR:', 'The input directory:', dirPath, 'does not exist, or it is a file!')
		exit(-1)

	outPath = os.path.abspath(args.out + EXCEL_POSTFIX)

	if os.path.exists(outPath):
		print('FATAL_ERR:', 'The output file path:', outPath, 'already exist!')
		exit(-1)

	if args.sql != None:

		sqlPath = os.path.abspath(args.sql)

		if not os.path.isfile(sqlPath):
			print('FATAL_ERR:', 'The SQL file,', outPath, 'does not exist!')
			exit(-1)

	else:

		sqlPath = None

	sqlQueries = ReadSqlQueries(sqlPath)

	rows = []

	idList = GetResultIdList(dirPath)
	print('INFO:', 'Processing raw data...')

	numOfThreads = (psutil.cpu_count() * 2) if psutil.cpu_count() != None else 1
	sema = threading.Semaphore(value=numOfThreads)
	parThreadList = []
	for id in idList:
		parThread = ResultParserThread(sema, dirPath, id, args.warmUpTime, 1, args.percentile)
		parThread.start()
		parThreadList.append(parThread)

	#Collecting results
	print('INFO:', 'Collecting results...')
	proBar = progressbar.ProgressBar()
	for parThread in proBar(parThreadList):
		rows.append(parThread.JoinAndGetResult())

	summaryDataF = pd.DataFrame(data=rows, columns=COLUMN_NAMES)

	summaryDataF = summaryDataF.astype(COLUMN_TYPES)

	dataFs = ConstructExcelSheets(summaryDataF, sqlQueries)

	WriteExcel(outPath, dataFs)

	print()

if __name__ == '__main__':
	sys.exit(main())
