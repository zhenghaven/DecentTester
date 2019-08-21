import os
import sys
import time
import socket
import psutil
import argparse
import subprocess
import SocketTools as st
import procConfigureTools as pct

AFINITY_LIST = [[3], [4], [5], [7], [6], [1]] #, [0], [2]
DEFAULT_PRIORITY = psutil.REALTIME_PRIORITY_CLASS

DHT_PORT_START = 57756

DHT_PROG_NAME = 'DecentDht_App'

TEST_SERVER_ADDR = ''
TEST_SERVER_PORT = 57725

def SetupTestServer():

	print('INFO:', 'Setting up the server...')

	svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	svr.bind((TEST_SERVER_ADDR, TEST_SERVER_PORT))
	svr.listen(1)

	return svr

def AcceptTestClient(svr):

	print('INFO:', 'Accepting client\'s connection...')

	conn, addr = svr.accept()

	if conn == None:
		raise RuntimeError('Failed to accept client\'s connection!')

	print('INFO:', 'Test client is connected from', addr)
	return conn

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

def GetClientStartEndRound(conn, pList):

	clientSignal = st.SocketRecvPack(conn)
	if clientSignal != 'Start':
		return False

	sysStatRecorder = pct.SysStatusRecorderThread(pList, 0.1) # Start
	sysStatRecorder.start()

	clientSignal = st.SocketRecvPack(conn)
	#Any signal will be treated as end.
	rec = sysStatRecorder.StopAndGetResult() # End

	recCsvStr = pct.ConvertRecord2CsvStr(rec, pList)
	#Send CSV string
	st.SocketSendPack(conn, recCsvStr)

	return True

def RunOneTestCase(conn):

	#Recv num of server nodes to spawn
	numOfNode = RecvNumOfNode(conn)

	procObjs = None

	try:
		#Run server nodes:
		print('INFO:', 'Spawning', numOfNode, 'nodes...')
		procObjs = RunTestProgram(numOfNode)

		pidList = GetPidListFromProcObjs(procObjs)

		#Configure CPU affinity & priority etc...
		pList = pct.ConfigureProc(pidList, AFINITY_LIST, DEFAULT_PRIORITY)

		#Now, server is ready
		st.SocketSendPack(conn, 'R')
		print('INFO:', 'Server is ready.')

		isClientFinished = GetClientStartEndRound(conn, pList)

		while isClientFinished:
			isClientFinished = GetClientStartEndRound(conn, pList)

		print('INFO:', 'Client has finished the current test case.')

	finally:
		KillTestProgram(procObjs)

def ListenToClient(conn):

	clientSignal = st.SocketRecvPack(conn)

	while clientSignal == 'Test':
		RunOneTestCase(conn)
		clientSignal = st.SocketRecvPack(conn)

def main():

	svr = SetupTestServer()

	conn = AcceptTestClient(svr)

	ListenToClient(conn)

	print('INFO:', 'Tests are finished!')

if __name__ == '__main__':
	sys.exit(main())
