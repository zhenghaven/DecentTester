import os
import sys
import time
import json
import socket
import datetime
import argparse
import subprocess

# import submodules:
if __name__ == '__main__':
	from YcsbModules import ConfigParser
	from YcsbModules import SocketTools as st
	from YcsbModules import procConfigureTools as pct
else:
	from .YcsbModules import ConfigParser
	from .YcsbModules import SocketTools as st
	from .YcsbModules import procConfigureTools as pct

TCP_CONNECT_RETRY_TIME_LIST = [2, 4, 8, 16, 20]

def GetConfigFilePath():

	return os.path.join(os.path.abspath('.'), 'Config.json')

def WaitFor(sec):

	sys.stdout.write('INFO: Execute next command in ' + str(sec) + ' second(s).')
	sys.stdout.flush()
	leftSec = sec
	while leftSec > 0:
		time.sleep(leftSec if leftSec < 1 else 1)
		leftSec = leftSec - 1
		sys.stdout.write('.')
		sys.stdout.flush()

	print()

def GetStrFromFile(filename):

	file = open(filename, 'r')
	res = file.read()
	file.close()

	return res

def GetJsonFromFile(filename):

	return json.loads(GetStrFromFile(filename))

def WriteStrToFile(filename, outStr):

	file = open(filename, 'w')
	file.write(outStr)
	file.close()

def WriteJsonToFile(filename, jsonObj):

	WriteStrToFile(filename, json.dumps(jsonObj, indent='\t'))

def UpdateClientConfig(numOfNode, svrPortBegin):

	jsonObj = GetJsonFromFile(GetConfigFilePath())

	jsonObj['Enclaves']['DecentDHT']['Port'] = svrPortBegin + (numOfNode - 1)

	WriteJsonToFile(GetConfigFilePath(), jsonObj)

def SetJavaSysProperty(maxOpPerTicket):

	os.environ['JAVA_OPTS'] = '-DDecent.maxOpPerTicket="' + str(maxOpPerTicket) + '"'

def GetOutputDirPath(absOutputDirPath, bindingName, workload, dist, recCount, maxTime, hostName):

	subPath = 'Transactions_' + bindingName + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_' + hostName
	dirPath = os.path.join(absOutputDirPath, subPath)

	subPath = workload + '_' + dist + '_' + str(recCount) + '_' + str(maxTime)
	dirPath = os.path.join(dirPath, subPath)

	return dirPath

def CreateDirs(dirPath):

	if not os.path.exists(dirPath):
		print('INFO:', 'Creating directories with path:', dirPath, '...')
		os.makedirs(dirPath)

def ExecuteYcsbTestCommand(command, procPriority):

	#print('INFO:', 'Executed command:', ' '.join(command))
	procObj = subprocess.Popen(command)# , creationflags=subprocess.CREATE_NEW_CONSOLE

	#Sets priority of the JVM:
	WaitFor(0.2)
	for p in pct.FindProcsByName('java'):
		p.nice(procPriority)

	print('INFO:', 'Executed command:', ' '.join(procObj.args))
	print('INFO:', 'Waiting for process to be done...')
	procObj.wait()

	if procObj.returncode != 0:
		raise RuntimeError('YCSB command returned error.')

	print('INFO:', 'Done!')

def GetYcsbWorkloadPath(filename):

	return os.path.join(GetYcsbHomePath(), 'workloads', filename)

def LoadDatabase(conn, ycsbPath, bindingName, procPriority, outPathBase, workload, dist, recCount, numOfNode, threadCount, maxOpPerTicket):

	print('INFO:', 'Loading the database...')

	#output report path
	outRepPath = outPathBase + '.txt'
	if os.path.exists(outRepPath):
		raise FileExistsError('The output report file, with path ' + outRepPath + ', already exist!')

	#output raw data path
	outRawPath = outPathBase + '.ycsb.csv'
	if os.path.exists(outRawPath):
		raise FileExistsError('The output report file, with path ' + outRawPath + ', already exist!')

	#output server sys status data path
	outSvrStatPath = outPathBase + '.SvrStat.csv'
	if os.path.exists(outSvrStatPath):
		raise FileExistsError('The output report file, with path ' + outSvrStatPath + ', already exist!')

	#Construct command
	options = []
	options += ['-P', GetYcsbWorkloadPath(workload)]
	options += ['-threads', str(threadCount)]

	options += ['-p', ('recordcount=' + str(recCount * numOfNode))]
	options += ['-p', ('requestdistribution=' + dist)]
	options += ['-p', ('measurementtype=' + 'raw')]
	options += ['-p', ('measurement.raw.output_file=' + outRawPath)]

	command = ['cmd.exe', '/c', ycsbPath, 'load', bindingName]
	command += options
	command += ['>', outRepPath]

	print('INFO:', 'Loading database with maxOpPerTicket =', maxOpPerTicket)
	SetJavaSysProperty(maxOpPerTicket)

	st.SocketSendPack(conn, 'Start')
	if st.SocketRecvPack(conn) != 'Proceed':
		raise RuntimeError('Server respond error.')
	ExecuteYcsbTestCommand(command, procPriority)
	st.SocketSendPack(conn, 'End')

	WriteStrToFile(outSvrStatPath, st.SocketRecvPack(conn))

	WaitFor(5)

def RunTest(conn, ycsbPath, bindingName, procPriority, outPathBase, workload, dist, recCount, numOfNode, maxOp, maxTime, threadCount, maxOpPerTicket, targetThrp):

	print('INFO:', 'Running the test...')

	#output report path
	outRepPath = outPathBase + '.txt'
	if os.path.exists(outRepPath):
		raise FileExistsError('The output report file, with path ' + outRepPath + ', already exist!')

	#output raw data path
	outRawPath = outPathBase + '.ycsb.csv'
	if os.path.exists(outRawPath):
		raise FileExistsError('The output report file, with path ' + outRawPath + ', already exist!')

	#output server sys status data path
	outSvrStatPath = outPathBase + '.SvrStat.csv'
	if os.path.exists(outSvrStatPath):
		raise FileExistsError('The output report file, with path ' + outSvrStatPath + ', already exist!')

	#Construct command
	options = []
	options += ['-P', GetYcsbWorkloadPath(workload)]
	options += ['-threads', str(threadCount)]
	options += ['-target', str(targetThrp)] if targetThrp >= 0 else []

	options += ['-p', ('recordcount=' + str(recCount * numOfNode))]
	options += ['-p', ('requestdistribution=' + dist)]
	options += ['-p', ('operationcount=' + str(maxOp))]
	options += ['-p', ('maxexecutiontime=' + str(maxTime))]
	options += ['-p', ('measurementtype=' + 'raw')]
	options += ['-p', ('measurement.raw.output_file=' + outRawPath)]

	command = ['cmd.exe', '/c', ycsbPath, 'run', bindingName]
	command += options
	command += ['>', outRepPath]

	print('INFO:', 'Running test with maxOpPerTicket =', maxOpPerTicket)
	SetJavaSysProperty(maxOpPerTicket)

	st.SocketSendPack(conn, 'Start')
	if st.SocketRecvPack(conn) != 'Proceed':
		raise RuntimeError('Server respond error.')
	ExecuteYcsbTestCommand(command, procPriority)
	st.SocketSendPack(conn, 'End')

	WriteStrToFile(outSvrStatPath, st.SocketRecvPack(conn))

	WaitFor(5)

def SendNumOfNode(conn, numOfNode):

	st.SocketSend_uint64(conn, numOfNode)

	if st.SocketRecvPack(conn) != 'OK':
		raise RuntimeError('Server doesn\'t accept the numOfNode=' + numOfNode + ' !')

def RunOneTypeNodeSetup(conn, svrPortBegin, isMaster, ycsbPath, bindingName, procPriority, outDir, attemptNum, numOfNode, workload, dist, recCount, maxOp, maxTime, threadCountList, opPerSessList, targetThrpList):

	UpdateClientConfig(numOfNode, svrPortBegin)

	#----- Setup server nodes
	if isMaster:
		#Tell server we have test to perform
		st.SocketSendPack(conn, 'Test')

		#Tell server how many node we need
		print('INFO:', 'Telling server how many node we need...')
		SendNumOfNode(conn, numOfNode)

	#----- Wait for server to complete the setup process
	print('INFO:', 'Waiting for server to complete the setup process...')
	clientSignal = st.SocketRecvPack(conn)
	if clientSignal != 'R':
		raise RuntimeError('Server error during setup process.')

	#----- Load database:
	print('INFO:', 'Loading database...')
	if isMaster:
		CreateDirs(os.path.join(outDir, 'load'))
		loadThreadCount = threadCountList[len(threadCountList) - 1]
		loadMaxOpPerTicket = opPerSessList[len(opPerSessList) - 1]

		outPathBase = 'Attempt_' + '{0:02d}'.format(attemptNum) + '_' + '{0:02d}'.format(numOfNode) + '_' + '{0:02d}'.format(loadThreadCount) + '_' + str(loadMaxOpPerTicket) + '_-1'
		loadOutPathBase = os.path.join(outDir, 'load', outPathBase)
		LoadDatabase(conn, ycsbPath, bindingName, procPriority, loadOutPathBase, workload, dist, recCount, numOfNode, loadThreadCount, loadMaxOpPerTicket)
	else:
		st.SocketSendPack(conn, 'Start')
		if st.SocketRecvPack(conn) != 'Proceed':
			raise RuntimeError('Server respond error.')
		st.SocketSendPack(conn, 'End')
		st.SocketRecvPack(conn)

	#----- Run transactions:
	print('INFO:', 'Begin testing...')
	for threadCount in threadCountList:
		for maxOpPerTicket in opPerSessList:
			for targetThrp in targetThrpList:
				outPathBase = 'Attempt_' + '{0:02d}'.format(attemptNum) + '_' + '{0:02d}'.format(numOfNode) + '_' + '{0:02d}'.format(threadCount) \
							+ '_' + str(maxOpPerTicket) + '_' + str(targetThrp)
				outPathBase = os.path.join(outDir, outPathBase)
				RunTest(conn, ycsbPath, bindingName, procPriority, outPathBase, workload, dist, recCount, numOfNode, maxOp, maxTime, threadCount, maxOpPerTicket, targetThrp)

	if isMaster:
		st.SocketSendPack(conn, 'Finished')

	print('INFO:', 'Finished test with', numOfNode ,'nodes.')

def GetServerConnection(svrAddr, svrPort, totalClient, clientI, retryTimeList):

	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	isConnected = False
	retryCount = 0

	while isConnected is False:
		try:
			conn.connect((svrAddr, svrPort))
			isConnected = True
		except Exception:
			print('Failed to connect to the Tester Server.', 'Retry later...')
			waitTime = retryTimeList[retryCount if retryCount < len(retryTimeList) else len(retryTimeList) - 1]
			if waitTime < 0:
				raise
			else:
				WaitFor(waitTime)
			retryCount = retryCount + 1

	st.SocketSend_uint64(conn, totalClient)
	st.SocketSend_uint64(conn, clientI)

	return conn

def SetYcsbHomeEnvVar(ycsbHome):

	if not os.path.exists(ycsbHome):
		raise FileNotFoundError('Could not find YCSB\'s home directory!')

	os.environ['YCSB_HOME'] = ycsbHome

def GetAbsPathInConfig(cfg, key, cfgParentAbsPath):

	absPath = cfg[key]
	if os.path.isabs(absPath) and os.path.exists(absPath):
		return absPath
	elif os.path.exists(os.path.join(cfgParentAbsPath, absPath)):
		return os.path.join(cfgParentAbsPath, absPath)
	else:
		raise RuntimeError('The given path to the ' + key + ' is invalid (path='+ absPath +').')

def StartOneTestsByConfig(testCfg, cfgParentAbsPath, hostName):

	#===== Setup work directory
	testWorkDir = GetAbsPathInConfig(testCfg, 'WorkDirectory', cfgParentAbsPath)
	os.chdir(testWorkDir)
	print('INFO:', 'Working directory switched to:', testWorkDir)

	#===== Setup output path
	absOutputDirPath = GetAbsPathInConfig(testCfg, 'OutputDirectory', cfgParentAbsPath)
	outDirPath = GetOutputDirPath(absOutputDirPath,
		testCfg['Target']['BindingName'],
		testCfg['Test']['WorkloadType'],
		testCfg['Test']['DistType'],
		testCfg['Test']['RecordCount'],
		testCfg['Test']['MaxTime'],
		hostName)
	CreateDirs(outDirPath)

	#===== Setup YCSB_HOME path
	YcsbHomePath = GetAbsPathInConfig(testCfg, 'YcsbHome', cfgParentAbsPath)
	SetYcsbHomeEnvVar(YcsbHomePath)

	#===== Try to connect to the Tester Server
	conn = GetServerConnection(testCfg['Tester']['SvrAddr'], testCfg['Tester']['SvrPort'], testCfg['Test']['TotalNumOfClient'], testCfg['Test']['ClientIdx'], TCP_CONNECT_RETRY_TIME_LIST)

	#===== Setup System Services processes priority
	for sysSvcBinName in testCfg['SysSvc']['BinList']:
		pct.ConfigProcAffAndPrioByName(sysSvcBinName, None, ConfigParser.SELECTED_PRIORITY_LEVELS[testCfg['SysSvc']['Priority']])

	#===== Start to run the test
	try:
		for attemptNum in range(1, testCfg['Test']['AttemptCount'] + 1):
			for nodeNum in testCfg['Test']['NumOfNodeList']:
				RunOneTypeNodeSetup(conn,
					testCfg['Target']['ServerPortStart'],
					(testCfg['Test']['ClientIdx'] is 0),
					os.path.join(YcsbHomePath, 'bin', 'ycsb'),
					testCfg['Target']['BindingName'],
					ConfigParser.SELECTED_PRIORITY_LEVELS[testCfg['Target']['Priority']],
					outDirPath,
					attemptNum,
					nodeNum,
					testCfg['Test']['WorkloadType'],
					testCfg['Test']['DistType'],
					testCfg['Test']['RecordCount'],
					testCfg['Test']['MaxOpCount'],
					testCfg['Test']['MaxTime'],
					testCfg['Test']['ThreadCountList'],
					testCfg['Test']['OpPerSessionList'],
					testCfg['Test']['TargetThroughputList'])
			print('INFO:', 'Finished attempt', attemptNum, '.')

		#Tell server we are done
		st.SocketSendPack(conn, 'Done')
	finally:
		conn.shutdown(socket.SHUT_RDWR)
		conn.close()

def StartTestsByConfig(cfg, cfgParentAbsPath, startIdx):

	hostName = socket.gethostname()
	currWorkDir = os.getcwd()

	try:

		for testCfg in cfg['ClientTests'][startIdx:]:
			StartOneTestsByConfig(testCfg, cfgParentAbsPath, hostName)

	finally:
		os.chdir(currWorkDir)

def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--config', type=str, required=True)
	parser.add_argument('--startIdx', type=int, required=False, default=1)

	args = parser.parse_args()

	cfg, absOutputDir = ConfigParser.ParseConfig(args.config, 'ycsb.test.json')

	StartTestsByConfig(cfg, absOutputDir, args.startIdx - 1)

if __name__ == '__main__':
	sys.exit(main())
