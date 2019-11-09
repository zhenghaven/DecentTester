import psutil
import datetime
import threading
import pandas as pd

def ConfigureProc(pIdList, affinityList, priority):

	if len(pIdList) == 0:
		return

	if len(pIdList) > len(affinityList):
		raise RuntimeError('Number of processes is more than the length of the affinityList')

	pList = []

	#Construct process list
	for pId in pIdList:
		pList.append(psutil.Process(pid=pId))

	#Set affinity and priority
	for i in range(0, len(pList)):
		pList[i].cpu_affinity(affinityList[i])
		pList[i].nice(priority)

	return pList

class SysStatusRecorderThread(threading.Thread):

	def __init__(self, pList, nodeCpuList, sysCpuList, interval):
		super(SysStatusRecorderThread, self).__init__()
		self.pList = pList
		self.nodeCpuList = nodeCpuList
		self.sysCpuList = sysCpuList
		self.interval = interval
		self.stopFlag = threading.Event()
		self.rows = []
		self.error = None

	def RecordOneSysStatus(self):
		ts = datetime.datetime.now().timestamp()
		tsMiSec = int(ts * 1000)

		overall = psutil.cpu_percent(interval=self.interval)
		overallIdvi = psutil.cpu_percent(percpu=True)
		nodeCpu = [overallIdvi[x] for x in self.nodeCpuList]
		sysCpu = [overallIdvi[x] for x in self.sysCpuList]
		row = [tsMiSec, overall, (sum(nodeCpu)/float(len(nodeCpu))), (sum(sysCpu)/float(len(sysCpu)))]

		for p in self.pList:
			row.append(p.cpu_percent())

		return row

	def run(self):

		try:
			#First record is not accurate; discards it.
			self.RecordOneSysStatus()
			self.rows = []

			while not self.stopFlag.isSet():
				self.rows.append(self.RecordOneSysStatus())
		except Exception as e:
			self.error = e

	def StopAndGetResult(self, timeout=None):
		self.stopFlag.set()
		self.join(timeout)

		if (not self.is_alive()) and (self.error == None):
			return self.rows
		elif self.error != None:
			raise self.error
		else:
			return []

def ConvertRecord2CsvStr(recRows, pList):

	columns = ['timestamp_ms', 'overall_percent', 'node_overall_percent', 'sys_overall_percent']

	for p in pList:
		columns.append(str(p.pid))

	dataF = pd.DataFrame(data=recRows, columns=columns)
	return dataF.to_csv(path_or_buf=None, index=False, line_terminator='\n')

def FindProcsByName(name):

	ls = []

	for p in psutil.process_iter(attrs=['name']):
		if p.info['name'].startswith(name):
			ls.append(p)
	return ls

def ConfigProcAffAndPrioByName(svcBinNameList, svcAffList, svcPriority):

	for svcBinName in svcBinNameList:
		for p in FindProcsByName(svcBinName):
			if not (svcAffList == None):
				p.cpu_affinity(svcAffList)
			if not (svcPriority == None):
				p.nice(svcPriority)
