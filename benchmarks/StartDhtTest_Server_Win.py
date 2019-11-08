import os
import sys
import time
import socket
import psutil
import argparse
import subprocess
import SocketTools as st
import procConfigureTools as pct

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

def RunOneTestCase(connArr, targetBin, targetAffFullList, targetPriority, targetPortStart, svcBinNameList, svcAffFullList, svcPriority):

	#Recv num of server nodes to spawn
	numOfNode = RecvNumOfNode(connArr[0], len(targetAffFullList))

	svcAffList = svcAffFullList[:numOfNode]
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

def ListenToClients(connArr, targetBin, targetAffFullList, targetPriority, targetPortStart, svcBinNameList, svcAffFullList, svcPriority):

	clientSignal = st.SocketRecvPack(connArr[0])

	while clientSignal == 'Test':
		RunOneTestCase(connArr, targetBin, targetAffFullList, targetPriority, targetPortStart, svcBinNameList, svcAffFullList, svcPriority)
		clientSignal = st.SocketRecvPack(connArr[0])

TEST_TARGET_BINARY = 'DecentDht_App'
TEST_TARGET_AFINITY_LIST = [[1], [3], [5], [7], [9], [11], [13], [15]]
TEST_TARGET_PRIORITY = psutil.REALTIME_PRIORITY_CLASS
TEST_TARGET_PORT_START = 57756

SYS_SVC_AESM_NAME = 'aesm_service'
SYS_SVC_WIN_NET_NAME = 'WmiPrvSE'
SYS_SVC_PYTHON_NAME = 'python'
SYS_SVC_AFINITY_LIST = [0, 2, 4, 6, 8, 10, 12, 14]
SYS_SVC_DEFAULT_PRIORITY = psutil.HIGH_PRIORITY_CLASS

TESTER_SERVER_ADDR = ''
TESTER_SERVER_PORT = 57725

def main():

	svr = SetupTestServer(TESTER_SERVER_ADDR, TESTER_SERVER_PORT)

	connArr = AcceptTestClients(svr)

	ListenToClients(connArr, TEST_TARGET_BINARY, TEST_TARGET_AFINITY_LIST, TEST_TARGET_PRIORITY, TEST_TARGET_PORT_START
		            [SYS_SVC_AESM_NAME, SYS_SVC_WIN_NET_NAME, SYS_SVC_PYTHON_NAME], SYS_SVC_AFINITY_LIST, SYS_SVC_DEFAULT_PRIORITY)

	print('INFO:', 'Tests are finished!')

if __name__ == '__main__':
	sys.exit(main())
