import os
import sys
import time
import json
import socket
import datetime
import argparse
import subprocess

CLIENT_BINDING_NAME = 'decentdht'

TEST_SERVER_ADDR = '127.0.0.1'
TEST_SERVER_PORT = 57725

DHT_SERVER_PORT_BEGIN = 57756

THREAD_COUNT_LIST = [40]

MAX_OP_PER_TICKET_LIST = [500, 1000]

BENCHMARKS_HOME_PATH = '.'

def GetBuildDirPath():

	return os.path.join(os.path.dirname(BENCHMARKS_HOME_PATH), 'build')

def GetYcsbHomePath():

	return os.path.join(BENCHMARKS_HOME_PATH, 'YCSB')

def GetYcsbBinPath():

	return os.path.join(GetYcsbHomePath(), 'bin', 'ycsb')

def GetConfigFilePath():

	return os.path.join(GetBuildDirPath(), 'Config.json')

def SetupDirPath():

	global BENCHMARKS_HOME_PATH
	BENCHMARKS_HOME_PATH = os.getcwd()
	os.chdir(GetBuildDirPath())

	print('INFO:', 'YCSB\'s Home Path is:', GetYcsbHomePath())
	print('INFO:', 'Libraries Path is:', GetBuildDirPath())
	print('INFO:', 'Current Working Directory is:', os.getcwd())

def WaitFor(sec):

	leftSec = sec
	while leftSec > 0:
		print('INFO:', 'Execute next command in ' + str(leftSec) + ' second(s).')
		time.sleep(1)
		leftSec = leftSec - 1

def SetJavaSysProperty(maxOpPerTicket):

	os.environ['JAVA_OPTS'] = '-DDecent.maxOpPerTicket="' + str(maxOpPerTicket) + '"'

def GetOutputDirPath(workload, dist, recCount, maxTime):

	dirPath = os.path.join(BENCHMARKS_HOME_PATH, 'results')

	subPath = 'Transactions_' + CLIENT_BINDING_NAME + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	dirPath = os.path.join(dirPath, subPath)

	subPath = workload + '_' + dist + '_' + str(recCount) + '_' + str(maxTime)
	dirPath = os.path.join(dirPath, subPath)

	return dirPath

def CreateDirs(dirPath):

	if not os.path.exists(dirPath):
		print('INFO:', 'Creating directories with path:', dirPath, '...')
		os.makedirs(dirPath)

def ExecuteYcsbTestCommand(command):

	#print('INFO:', 'Executed command:', ' '.join(command))
	procObj = subprocess.Popen(command)# , creationflags=subprocess.CREATE_NEW_CONSOLE
	print('INFO:', 'Executed command:', ' '.join(procObj.args))
	print('INFO:', 'Waiting for process to be done...')
	procObj.wait()

	if procObj.returncode != 0:
		raise RuntimeError('YCSB command returned error.')

	print('INFO:', 'Done!')

	WaitFor(5)

def GetYcsbWorkloadPath(filename):

	return os.path.join(GetYcsbHomePath(), 'workloads', filename)

def LoadDatabase(ycsbPath, outDir, workload, dist, recCount, numOfNode, threadCount, maxOpPerTicket, attemptNum):

	print('INFO:', 'Loading the database...')

	#output report path
	outRepPath = 'Attempt_' + '{0:02d}'.format(attemptNum) + '_' + '{0:02d}'.format(numOfNode) + '_load.txt'
	outRepPath = os.path.join(outDir, outRepPath)

	if os.path.exists(outRepPath):
		raise FileExistsError('The output report file, with path ' + outRepPath + ', already exist!')

	#output raw data path
	outRawPath = 'Attempt_' + '{0:02d}'.format(attemptNum) + '_' + '{0:02d}'.format(numOfNode) + '_load.csv'
	outRawPath = os.path.join(outDir, outRawPath)

	if os.path.exists(outRawPath):
		raise FileExistsError('The output report file, with path ' + outRawPath + ', already exist!')

	#Construct command
	options = []
	options += ['-p', ('recordcount=' + str(recCount * numOfNode))]
	options += ['-p', ('requestdistribution=' + dist)]
	options += ['-p', ('measurementtype=' + 'raw')]
	options += ['-p', ('measurement.raw.output_file=' + (outRawPath))]

	command = ['cmd.exe', '/c', ycsbPath, 'load', CLIENT_BINDING_NAME, '-P', GetYcsbWorkloadPath(workload), '-threads', str(threadCount)]
	command += options
	command += ['>', outRepPath]

	print('INFO:', 'Loading database with maxOpPerTicket =', maxOpPerTicket)
	SetJavaSysProperty(maxOpPerTicket)
	ExecuteYcsbTestCommand(command)

def RunTest(ycsbPath, outDir, workload, dist, recCount, numOfNode, maxOp, maxTime, threadCount, maxOpPerTicket, attemptNum):

	print('INFO:', 'Running the test...')

	#output report path
	outRepPath = 'Attempt_' + '{0:02d}'.format(attemptNum) + '_' + '{0:02d}'.format(numOfNode) + '_' + '{0:02d}'.format(threadCount) + '_' + str(maxOpPerTicket) + '.txt'
	outRepPath = os.path.join(outDir, outRepPath)

	if os.path.exists(outRepPath):
		raise FileExistsError('The output report file, with path ' + outRepPath + ', already exist!')

	#output raw data path
	outRawPath = 'Attempt_' + '{0:02d}'.format(attemptNum) + '_' + '{0:02d}'.format(numOfNode) + '_' + '{0:02d}'.format(threadCount) + '_' + str(maxOpPerTicket) + '.csv'
	outRawPath = os.path.join(outDir, outRawPath)

	if os.path.exists(outRawPath):
		raise FileExistsError('The output report file, with path ' + outRawPath + ', already exist!')

	#Construct command
	options = []
	options += ['-p', ('recordcount=' + str(recCount * numOfNode))]
	options += ['-p', ('requestdistribution=' + dist)]
	options += ['-p', ('operationcount=' + str(maxOp))]
	options += ['-p', ('maxexecutiontime=' + str(maxTime))]
	options += ['-p', ('measurementtype=' + 'raw')]
	options += ['-p', ('measurement.raw.output_file=' + (outRawPath))]

	command = ['cmd.exe', '/c', ycsbPath, 'run', CLIENT_BINDING_NAME, '-P', GetYcsbWorkloadPath(workload), '-threads', str(threadCount)]
	command += options
	command += ['>', outRepPath]

	print('INFO:', 'Running test with maxOpPerTicket =', maxOpPerTicket)
	SetJavaSysProperty(maxOpPerTicket)
	ExecuteYcsbTestCommand(command)

def RunOneAttempt(ycsbPath, outDir, workload, dist, recCount, numOfNode, maxOp, maxTime, attemptNum):

	LoadDatabase(ycsbPath, outDir, workload, dist, recCount, numOfNode, THREAD_COUNT_LIST[len(THREAD_COUNT_LIST) - 1], MAX_OP_PER_TICKET_LIST[len(MAX_OP_PER_TICKET_LIST) - 1], attemptNum)

	for threadCount in THREAD_COUNT_LIST:
		for maxOpPerTicket in MAX_OP_PER_TICKET_LIST:
			RunTest(ycsbPath, outDir, workload, dist, recCount, numOfNode, maxOp, maxTime, threadCount, maxOpPerTicket, attemptNum)

def SendNumOfNode(conn, numOfNode):

	conn.sendall(str(numOfNode).encode())
	data = conn.recv(512)
	if data != b'O':
		raise RuntimeError('Server doesn\'t accept the numOfNode=' + numOfNode + ' !')

def RecvServerReady(conn):

	data = conn.recv(512)
	if data != b'R':
		raise RuntimeError('Server error during setup process.')

def SendServerReady(conn):

	conn.send(b'F')

def SendClientFinished(conn):

	SendNumOfNode(conn, 0)

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

def UpdateClientConfig(numOfNode):

	jsonObj = GetJsonFromFile(GetConfigFilePath())

	jsonObj['Enclaves']['DecentDHT']['Port'] = DHT_SERVER_PORT_BEGIN + (numOfNode - 1)

	WriteJsonToFile(GetConfigFilePath(), jsonObj)

def RunOneTypeNodeSetup(serverConn, ycsbPath, outDir, workload, dist, recCount, numOfNode, maxOp, maxTime, attemptCount):

	UpdateClientConfig(numOfNode)

	for i in range(1, attemptCount + 1):

		#Tell server how many node we need
		print('INFO:', 'Telling server how many node we need...')
		SendNumOfNode(serverConn, numOfNode)

		#Wait for server to complete the setup process
		print('INFO:', 'Waiting for server to complete the setup process...')
		RecvServerReady(serverConn)

		#Begin testing
		print('INFO:', 'Begin testing...')
		RunOneAttempt(ycsbPath, outDir, workload, dist, recCount, numOfNode, maxOp, maxTime, i)

		#Tell server we are done, so the server node can be destroyed
		print('INFO:', 'Tell server we are done, so the server node can be destroyed...')
		SendServerReady(serverConn)

def GetServerConnection():

	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.connect((TEST_SERVER_ADDR, TEST_SERVER_PORT))

	return conn

def SetYcsbHomeEnvVar():

	ycsbHome = GetYcsbHomePath()

	if not os.path.exists(ycsbHome):
		raise FileNotFoundError('Could not find YCSB\'s home directory!')

	os.environ['YCSB_HOME'] = ycsbHome

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--workload', required=True)
	parser.add_argument('--dist', required=True)
	parser.add_argument('--recN', type=int, required=True)
	parser.add_argument('--maxOp', type=int, required=True)
	parser.add_argument('--maxTime', type=int, required=True)
	parser.add_argument('--attemptN', type=int, required=True)
	parser.add_argument('--nodeNum', type=int, required=False)
	parser.add_argument('--maxNode', type=int, required=False)

	args = parser.parse_args()

	if (args.nodeNum == None and args.maxNode == None) or (args.nodeNum != None and args.maxNode != None):
		print('FATAL_ERR:', 'Only one argument of nodeNum and maxNode should be set!')
		exit(-1)

	#Setup necessary paths:
	SetupDirPath()

	#Setup system environment variables
	SetYcsbHomeEnvVar()

	outDirPath = GetOutputDirPath(args.workload, args.dist, args.recN, args.maxTime)
	try:
		print('INFO:', 'Checking output directory...')
		CreateDirs(outDirPath)
	except:
		print('FATAL_ERR:', 'Failed to create output directory with path:', outDirPath)
		exit(-1)

	conn = GetServerConnection()

	if args.nodeNum == None:

		#Test with all num of node setups
		for i in range(1, args.maxNode + 1):
			RunOneTypeNodeSetup(conn, GetYcsbBinPath(), outDirPath, args.workload, args.dist, args.recN, i, args.maxOp, args.maxTime, args.attemptN)

	else:

		#Test with only one num of node setup
		RunOneTypeNodeSetup(conn, GetYcsbBinPath(), outDirPath, args.workload, args.dist, args.recN, args.nodeNum, args.maxOp, args.maxTime, args.attemptN)

	print('INFO:', 'Tests are finished!')
	SendClientFinished(conn)

if __name__ == '__main__':
	sys.exit(main())
