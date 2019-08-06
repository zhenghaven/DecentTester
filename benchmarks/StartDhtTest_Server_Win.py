import os
import sys
import subprocess
import argparse
import time
import socket

AFINITY_LIST = ['40', '80', '08', '10', '20', '02'] #, '04', '01'

DHT_PORT_START = 57756

PROG_CFG_NAME = 'ProcConfigurer'

DHT_PROG_NAME = 'DecentDht_App'

TEST_SERVER_ADDR = '127.0.0.1'
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

	data = conn.recv(512)
	numOfNode = int(data)

	if numOfNode > len(AFINITY_LIST):
		conn.send(b'N')
		raise RuntimeError('The total number of node given (i.e. ' + numOfNode + ') is out of range!')
	else:
		conn.send(b'O')

	return numOfNode

def SendServerReady(conn):

	conn.send(b'R')

def WaitForClientFinish(conn):

	data = conn.recv(512)
	if data != b'F':
		raise RuntimeError('client error during test.')

def WaitFor(sec):

	leftSec = sec
	while leftSec > 0:
		print('INFO:', 'Execute next command in ' + str(leftSec) + ' second(s).')
		time.sleep(1)
		leftSec = leftSec - 1

def RunTestProgram(numOfNode):

	cWorkDir = os.getcwd()
	ProcConfigurerPath = os.path.join(cWorkDir, PROG_CFG_NAME)
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

		print('INFO:', 'Setting affinity and priority...')
		setProcRes = subprocess.run([ProcConfigurerPath, '-i', str(procObj.pid), '-a', AFINITY_LIST[i], '-p', '5'])
		if setProcRes.returncode != 0:
			raise RuntimeError('Failed to set affinity and priority, with command ' + ' '.join(setProcRes.args))

		prevPortI = currPortI
		currPortI = currPortI - 1

		WaitFor(i + 3)

		procObjs.append(procObj)

	return procObjs

def KillTestProgram(procObjs):

	for procObj in procObjs:
		procObj.kill()

def ListenToClient(conn):

	numOfNode = RecvNumOfNode(conn)

	#Check if the client wants to finish the test
	while numOfNode > 0:

		procObjs = RunTestProgram(numOfNode)
		SendServerReady(conn)
		print('INFO:', 'Server is ready')
		WaitForClientFinish(conn)
		print('INFO:', 'Client has finished the current test.')
		KillTestProgram(procObjs)
		print('INFO:', 'Waiting for client\'s next instruction...')
		numOfNode = RecvNumOfNode(conn)

def main():

	svr = SetupTestServer()

	conn = AcceptTestClient(svr)

	ListenToClient(conn)

	print('INFO:', 'Tests are finished!')

if __name__ == '__main__':
	sys.exit(main())
