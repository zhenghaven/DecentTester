import os
import threading

import pandas as pd
import progressbar as pbar

if __name__ == '__main__':
	import ProgressBarConfig as pbarCfg
	import PreProcRawData
	import FinalProcRawData
else:
	from . import ProgressBarConfig as pbarCfg
	from . import PreProcRawData
	from . import FinalProcRawData

YCSB_COL_IDX_OP        = 0
YCSB_COL_IDX_TIMESTAMP = 1
YCSB_COL_IDX_LATENCY   = 2
YCSB_COL_NAME_OP        = 'op'
YCSB_COL_NAME_TIMESTAMP = 'timestamp(ms)'
YCSB_COL_NAME_LATENCY   = 'latency(us)'

CSV_FILE_SUFFIX = '.csv'

NUMBER_OF_THREADS = 16

ID_COMPONENT_REPLACE_FUNC = { \
	'*' : lambda s : '*' \
	}

class ResultParserThread(threading.Thread):

	def __init__(self, sema, dirPathList, idPair, idDef, warnupT, terminateT, percentile, isFailOpsAllowed):
		super(ResultParserThread, self).__init__()
		self.sema = sema
		self.finishFlag = threading.Event()
		self.dirPathList = dirPathList
		self.idPair = idPair
		self.idDef = idDef
		self.warnupT = warnupT
		self.terminateT = terminateT
		self.percentile = percentile
		self.isFailOpsAllowed = isFailOpsAllowed
		self.idRes = []
		self.ycsbRes = []
		self.serverRes = []
		self.error = None

	def ProcessResultSet(self):

		#############################
		# Pre-Processing
		#############################

		ycsbDataF = PreProcRawData.GetPreProcedYcsbData( \
		            [os.path.join(dirPath, id + '.ycsb.csv') for dirPath, id in zip(self.dirPathList, self.idPair)], \
		            YCSB_COL_NAME_TIMESTAMP, YCSB_COL_NAME_OP, YCSB_COL_IDX_OP, self.isFailOpsAllowed)

		svrStatDataF = PreProcRawData.GetPreProcedSvrStatData( \
		               [os.path.join(dirPath, id + '.SvrStat.csv') for dirPath, id in zip(self.dirPathList, self.idPair)])

		#############################
		# Final-Processing
		#############################

		#Time Ranges
		ycsbFullTimeRange = FinalProcRawData.GetTimestampRange(ycsbDataF, YCSB_COL_NAME_TIMESTAMP)
		startTs = ycsbFullTimeRange[0] + (self.warnupT * 1000)
		endTs = ycsbFullTimeRange[1] - (self.terminateT * 1000)
		trimedTimeRange = (startTs, endTs)

		#Process result ID
		self.idRes = FinalProcRawData.GetIdResult(self.idPair, self.idDef)

		#Process YCSB CSV data

		self.ycsbRes = FinalProcRawData.GetYcsbDataResult(ycsbDataF, trimedTimeRange, self.percentile, YCSB_COL_NAME_TIMESTAMP, YCSB_COL_NAME_LATENCY)

		#Process server system status data
		self.serverRes = FinalProcRawData.GetSvrStatDataResult(svrStatDataF, trimedTimeRange, 'timestamp_ms', 'overall_percent', 'node_overall_percent', 'sys_overall_percent')

	def run(self):

		self.sema.acquire()

		try:

			self.ProcessResultSet()

		except Exception as e:
			self.error = e

		self.sema.release()
		self.finishFlag.set()

	def JoinAndGetResult(self, timeout=None):

		self.join(timeout)

		if self.is_alive():
			raise RuntimeError('Failed to stop the thread')
		elif self.error != None:
			raise self.error
		else:
			return self.idRes + self.ycsbRes + self.serverRes

	def IsFinished(self):
		return self.finishFlag.isSet();

def GetResultIdList(absDirPath, idSuffix):

	idList = []

	for filename in os.listdir(absDirPath):

		#looking for all txt files
		if filename.endswith(idSuffix) and os.path.isfile(os.path.join(absDirPath, filename)):
			root, ext = os.path.splitext(filename)
			idList.append(root)

	return idList

def GenIdWithWildcard(id, idDef):

	idComponets = id.split('_')
	if len(idComponets) != len(idDef):
		raise RuntimeError('The len of ID Definition given doesn\'t match the ID found')

	return '_'.join([item if defItem is None else ID_COMPONENT_REPLACE_FUNC[defItem[0]](item) for item, defItem in zip(idComponets, idDef)])

class RawDataProcessor:

	def __init__(self, resSetName, dirPathList, idSuffix, idDef, outputDirPath, warmupTime, endTime, latPercentile, isFailOpsAllowed, resColNames, resColTypes):

		#------- Pre-Checks:

		# Convert directory path to absolute path
		absDirPathList = [os.path.abspath(dirPath) for dirPath in dirPathList]

		for absDirPath in absDirPathList:
			if not os.path.exists(absDirPath):
				raise RuntimeError('The input directory doesn\'t exist (path='+ absDirPath +').')
			elif os.path.isfile(absDirPath):
				raise RuntimeError('The given input directory path is a file (path='+ absDirPath +').')

		absOutputDirPath = os.path.abspath(outputDirPath)
		absOutputPath = os.path.join(absOutputDirPath, resSetName + CSV_FILE_SUFFIX)

		# Getting ID pairs:
		# print('INFO:', 'Looking for result files...')
		idWildcardPairListList = [[(id, GenIdWithWildcard(id, idDef)) for id in GetResultIdList(absDirPath, idSuffix)] for absDirPath in absDirPathList]

		# Sort each list
		pairListLen = len(idWildcardPairListList[0])

		if pairListLen is 0:
			raise RuntimeError('There is no data to process for result set ' + resSetName + '.')

		for idWildcardPairList in idWildcardPairListList:
			if len(idWildcardPairList) != pairListLen:
				raise RuntimeError('There are unmatched test result pair in a result set.')
			idWildcardPairList.sort(key=lambda pair : pair[1])
			#print('INFO:', idWildcardPairList)

		# Ensure all pairs are matched
		for pairIdx in range(0, pairListLen):
			cmpId = idWildcardPairListList[0][pairIdx][1]
			# tmpPrint = cmpId
			for pairListIdx in range(1, len(idWildcardPairListList)):
				# tmpPrint += ' = ' + idWildcardPairListList[pairListIdx][pairIdx][1]
				if idWildcardPairListList[pairListIdx][pairIdx][1] != cmpId:
					raise RuntimeError('There are unmatched test result pair in a result set.')
			# print(tmpPrint)

		# Construct ID pair list
		idPairList = [[idWildcardPairListList[pairListIdx][pairIdx][0] for pairListIdx in range(0, len(idWildcardPairListList))] for pairIdx in range(0, pairListLen)]
		#print(idPairList)

		# Check latency percentile range
		if not (0 < latPercentile and latPercentile < 100):
			raise RuntimeError('Latency percentile given is out of range.')

		self.resSetName = resSetName
		self.absDirPathList = absDirPathList
		self.absOutputDirPath = absOutputDirPath
		self.absOutputPath = absOutputPath
		self.idPairList = idPairList
		self.idDef = idDef
		self.warmupTime = warmupTime
		self.endTime = endTime
		self.latPercentile = latPercentile
		self.isFailOpsAllowed = isFailOpsAllowed
		self.resColNames = resColNames
		self.resColTypes = resColTypes
		self.resDF = []

	def Process(self):

		#print('INFO:', 'Processing...')
		sema = threading.Semaphore(value=NUMBER_OF_THREADS)
		parThreadList = []
		for idPair in self.idPairList:
			parThread = ResultParserThread(sema, self.absDirPathList, idPair, self.idDef, self.warmupTime, self.endTime, self.latPercentile, self.isFailOpsAllowed)
			parThread.start()
			parThreadList.append(parThread)

		resRows = []

		# Collecting results
		error = None
		progBar = pbar.ProgressBar(max_value=len(parThreadList), **pbarCfg.PBAR_ARGS)
		progBar.update(0)
		while len(parThreadList) > 0:
			for item in parThreadList:
				if item.IsFinished():
					try:
						resRows.append(item.JoinAndGetResult())
					except Exception as e:
						print('FATAL_ERROR:', 'Exception raised.')
						resRows.append(None)
						error = e if error is None else error
					parThreadList.remove(item)
					progBar.update(len(resRows))

		if error is not None:
			raise error

		self.resDF = pd.DataFrame(data=resRows, columns=self.resColNames)
		self.resDF = self.resDF.astype(self.resColTypes)

	def SaveResult(self):

		self.resDF.to_csv(self.absOutputPath, index=False)
