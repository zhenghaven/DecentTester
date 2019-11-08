import os
import sys
import time
import socket
import psutil
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

SELECTED_PRIORITY_LEVELS = {
	'RealTime' : psutil.REALTIME_PRIORITY_CLASS,
	'AboveNormal' : psutil.ABOVE_NORMAL_PRIORITY_CLASS,
	'BelowNormal' : psutil.BELOW_NORMAL_PRIORITY_CLASS,
	'High' : psutil.HIGH_PRIORITY_CLASS,
	'Idle' : psutil.IDLE_PRIORITY_CLASS,
	'Normal' : psutil.NORMAL_PRIORITY_CLASS
}

def ConfigSysProc(svcBinNameList, svcAffList, svcPriority):

	for svcBinName in svcBinNameList:
		for p in pct.FindProcsByName(svcBinName):
			p.nice(svcPriority)
			p.cpu_affinity(svcAffList)

def SetupTestServer(testerSvrAddr, testerSvrPort):

	print('INFO:', 'Setting up the server...')

	svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	svr.bind((testerSvrAddr, testerSvrPort))
	svr.listen(1)

	return svr

def AcceptTestClients(svr):

	print('INFO:', 'Accepting clients\' connection...')

	conn, addr = svr.accept()

	if conn == None:
		raise RuntimeError('Failed to accept client\'s connection.')

	totalClient = st.SocketRecv_uint64(conn)
	clientI = st.SocketRecv_uint64(conn)
	if totalClient <= 0:
		raise RuntimeError('totalClient', totalClient, 'out of range.')
	if clientI >= totalClient:
		raise RuntimeError('ClientI', clientI, 'out of range.')

	connArr = [None for i in range(0, totalClient)]
	connArr[clientI] = conn

	print('INFO:', 'Test client', clientI ,'is connected from', addr)

	for i in range(0, totalClient - 1):
		conn, addr = svr.accept()

		if conn == None:
			raise RuntimeError('Failed to accept client\'s connection!')

		totalClient = st.SocketRecv_uint64(conn)
		clientI = st.SocketRecv_uint64(conn)

		if totalClient != len(connArr):
			raise RuntimeError('Total number of clients said by client', clientI, 'doesn\'t match', len(connArr), 'said by first client.')
		if clientI >= totalClient:
			raise RuntimeError('ClientI', clientI, 'out of range.')
		if connArr[clientI] != None:
			raise RuntimeError('Client', clientI, 'is already connected.')

		connArr[clientI] = conn

		print('INFO:', 'Test client', clientI ,'is connected from', addr)

	return connArr

def RecvNumOfNode(conn, maxNumOfNode):

	numOfNode = st.SocketRecv_uint64(conn)

	if not (1 <= numOfNode and numOfNode <= maxNumOfNode):
		st.SocketSendPack(conn, 'Err')
		raise RuntimeError('The total number of node given (i.e. ' + numOfNode + ') is out of range!')
	else:
		st.SocketSendPack(conn, 'OK')

	return numOfNode

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

def RunTestProgram(numOfNode, targetBin, targetPortStart):

	cWorkDir = os.getcwd()
	dhtAppPath = os.path.join(cWorkDir, targetBin)

	currPortI = targetPortStart + numOfNode - 1
	prevPortI = currPortI

	procObjs = []

	for i in range(numOfNode):

		runCommand = ([dhtAppPath, '-t', str(numOfNode), '-i', str(i), '-s', str(currPortI)])

		if i != 0:
			runCommand = (runCommand + ['-p', str(prevPortI)])

		#print('INFO:', 'Executing command: ' + ' '.join(runCommand))
		procObj = subprocess.Popen(runCommand, creationflags=subprocess.CREATE_NEW_CONSOLE)
		print('INFO:', 'Executed  command: ' + ' '.join(procObj.args))

		if procObj.poll() != None:
			exit(procObj.poll())

		prevPortI = currPortI
		currPortI = currPortI - 1

		WaitFor(i + 3)

		procObjs.append(procObj)

	return procObjs

def GetPidListFromProcObjs(procObjs):

	pidList = []

	for procObj in procObjs:
		pidList.append(procObj.pid)

	return pidList

def KillTestProgram(procObjs):

	if procObjs == None:
		return

	for procObj in procObjs:
		procObj.kill()

def GetClientsStartEndRound(connArr, pList, targetAffList, svcAffList):

	for conn in connArr:
		clientSignal = st.SocketRecvPack(conn)
		# Any non-"Start" reply will terminate the test
		if clientSignal != 'Start':
			return False

	sysStatRecorder = pct.SysStatusRecorderThread(pList, sum(targetAffList, []), svcAffList, 0.1) # Start
	sysStatRecorder.start()

	for conn in connArr:
		st.SocketSendPack(conn, 'Proceed')

	#----- Master client:
	clientSignal = st.SocketRecvPack(connArr[0])
	#Any signal will be treated as end.
	rec = sysStatRecorder.StopAndGetResult() # End

	#----- sub-clients:
	for i in range(1, len(connArr)):
		clientSignal = st.SocketRecvPack(connArr[i])
		#Any signal will be treated as end.

	#----- Master client:
	recCsvStr = pct.ConvertRecord2CsvStr(rec, pList)
	#Send CSV string
	st.SocketSendPack(connArr[0], recCsvStr)

	#----- sub-clients:
	for i in range(1, len(connArr)):
		st.SocketSendPack(connArr[i], '')

	return True

def RunOneTestCase(connArr, targetBin, targetAffFullList, targetPriority, targetPortStart, svcBinNameList, svcAffFullList, svcAffMode, svcPriority):

	#Recv num of server nodes to spawn
	numOfNode = RecvNumOfNode(connArr[0], len(targetAffFullList))

	svcAffList = None
	if svcAffMode == 'ByNodeNum':
		svcAffList = svcAffFullList[:numOfNode]
	elif svcAffMode == 'All':
		svcAffList = svcAffFullList
	else:
		raise RuntimeError('Invalid Server System Services CPU Affinity List Mode (given='+ str(svcAffMode) +').')

	targetAffList = targetAffFullList[:numOfNode]
	ConfigSysProc(svcBinNameList, svcAffList, svcPriority)

	procObjs = None

	try:
		#Run server nodes:
		print('INFO:', 'Spawning', numOfNode, 'nodes...')
		procObjs = RunTestProgram(numOfNode, targetBin, targetPortStart)

		pidList = GetPidListFromProcObjs(procObjs)

		#Configure CPU affinity & priority etc...
		pList = pct.ConfigureProc(pidList, targetAffList, targetPriority)

		for conn in connArr:
			#Now, server is ready
			st.SocketSendPack(conn, 'R')
			print('INFO:', 'Server is ready.')

		isClientFinished = GetClientsStartEndRound(connArr, pList, targetAffList, svcAffList)

		while isClientFinished:
			isClientFinished = GetClientsStartEndRound(connArr, pList, targetAffList, svcAffList)

		print('INFO:', 'Client has finished the current test case.')

	finally:
		KillTestProgram(procObjs)

def ListenToClients(connArr, targetBin, targetAffFullList, targetPriority, targetPortStart, svcBinNameList, svcAffFullList, svcAffMode, svcPriority):

	clientSignal = st.SocketRecvPack(connArr[0])

	while clientSignal == 'Test':
		RunOneTestCase(connArr, targetBin, targetAffFullList, targetPriority, targetPortStart, svcBinNameList, svcAffFullList, svcAffMode, svcPriority)
		clientSignal = st.SocketRecvPack(connArr[0])

def StartTestsByConfig(configPath, startIdx):

	cfg, absOutputDir = ConfigParser.ParseConfig(configPath, 'ycsb.test.json')
	currWorkDir = os.getcwd()

	try:

		for testCfg in cfg['Tests'][startIdx:]:

			testWorkDir = testCfg['WorkDirectory']
			if os.path.isabs(testCfg['WorkDirectory']) and os.path.exists(testCfg['WorkDirectory']):
				testWorkDir = testCfg['WorkDirectory']
			elif not os.path.isabs(testCfg['WorkDirectory']) and os.path.exists(os.path.join(absOutputDir, testCfg['WorkDirectory'])):
				testWorkDir = os.path.join(absOutputDir, testCfg['WorkDirectory'])
			else:
				raise RuntimeError('Given test working directory is invalid.')

			os.chdir(testWorkDir)
			print('INFO:', 'Working directory switched to:', testWorkDir)

			svr = SetupTestServer(testCfg['TesterSvrAddr'], testCfg['TesterSvrPort'])

			connArr = AcceptTestClients(svr)

			ListenToClients(connArr,
			                testCfg['TargetBin'], testCfg['TargetAffinity'], SELECTED_PRIORITY_LEVELS[testCfg['TargetPriority']], testCfg['TargetPortStart'],
			                testCfg['SysSvcBinList'], testCfg['SysSvcAffinity'], testCfg['SysSvcAffinityMode'], SELECTED_PRIORITY_LEVELS[testCfg['SysSvcPriority']]
			)

	finally:
		os.chdir(currWorkDir)

	print('INFO:', 'Tests are finished!')

def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--config', type=str, required=True)
	parser.add_argument('--startIdx', type=int, required=False, default=1)

	args = parser.parse_args()

	StartTestsByConfig(args.config, args.startIdx - 1)

if __name__ == '__main__':
	sys.exit(main())
