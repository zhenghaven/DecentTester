import os
import sys
import time
import socket
import psutil
import argparse
import subprocess
import SocketTools as st
import procConfigureTools as pct

AFINITY_LIST = [[3], [4], [5], [7], [6], [1]]
DEFAULT_PRIORITY = psutil.REALTIME_PRIORITY_CLASS

DHT_PORT_START = 57756

DHT_PROG_NAME = 'DecentDht_App'

SYS_REL_AESM_NAME = 'aesm_service'
SYS_REL_WIN_NET_NAME = 'WmiPrvSE'
SYS_REL_AFINITY_LIST = [0, 2]
SYS_REL_DEFAULT_PRIORITY = psutil.HIGH_PRIORITY_CLASS

TEST_SERVER_ADDR = ''
TEST_SERVER_PORT = 57725

def ConfigSysProc():

	for p in pct.FindProcsByName(SYS_REL_AESM_NAME):
		p.nice(SYS_REL_DEFAULT_PRIORITY)
		p.cpu_affinity(SYS_REL_AFINITY_LIST)

	for p in pct.FindProcsByName(SYS_REL_WIN_NET_NAME):
		p.nice(SYS_REL_DEFAULT_PRIORITY)
		p.cpu_affinity(SYS_REL_AFINITY_LIST)

def SetupTestServer():

	print('INFO:', 'Setting up the server...')

	svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	svr.bind((TEST_SERVER_ADDR, TEST_SERVER_PORT))
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

def RecvNumOfNode(conn):

	numOfNode = st.SocketRecv_uint64(conn)

	if numOfNode > len(AFINITY_LIST) or numOfNode < 1:
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

def RunTestProgram(numOfNode):

	cWorkDir = os.getcwd()
	dhtAppPath = os.path.join(cWorkDir, DHT_PROG_NAME)

	currPortI = DHT_PORT_START + numOfNode - 1
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

def GetClientsStartEndRound(connArr, pList, numOfNode):

	for conn in connArr:
		clientSignal = st.SocketRecvPack(conn)
		# Any non-"Start" reply will terminate the test
		if clientSignal != 'Start':
			return False

	sysStatRecorder = pct.SysStatusRecorderThread(pList, sum(AFINITY_LIST[:numOfNode], []), SYS_REL_AFINITY_LIST, 0.1) # Start
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

def RunOneTestCase(connArr):

	ConfigSysProc()

	#Recv num of server nodes to spawn
	numOfNode = RecvNumOfNode(connArr[0])

	procObjs = None

	try:
		#Run server nodes:
		print('INFO:', 'Spawning', numOfNode, 'nodes...')
		procObjs = RunTestProgram(numOfNode)

		pidList = GetPidListFromProcObjs(procObjs)

		#Configure CPU affinity & priority etc...
		pList = pct.ConfigureProc(pidList, AFINITY_LIST, DEFAULT_PRIORITY)

		for conn in connArr:
			#Now, server is ready
			st.SocketSendPack(conn, 'R')
			print('INFO:', 'Server is ready.')

		isClientFinished = GetClientsStartEndRound(connArr, pList, numOfNode)

		while isClientFinished:
			isClientFinished = GetClientsStartEndRound(connArr, pList, numOfNode)

		print('INFO:', 'Client has finished the current test case.')

	finally:
		KillTestProgram(procObjs)

def ListenToClients(connArr):

	clientSignal = st.SocketRecvPack(connArr[0])

	while clientSignal == 'Test':
		RunOneTestCase(connArr)
		clientSignal = st.SocketRecvPack(connArr[0])

def main():

	svr = SetupTestServer()

	connArr = AcceptTestClients(svr)

	ListenToClients(connArr)

	print('INFO:', 'Tests are finished!')

if __name__ == '__main__':
	sys.exit(main())
