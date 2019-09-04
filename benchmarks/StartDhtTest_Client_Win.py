import os
import sys
import time
import json
import socket
import psutil
import datetime
import argparse
import subprocess
import SocketTools as st
import procConfigureTools as pct

DEFAULT_PRIORITY = psutil.REALTIME_PRIORITY_CLASS

CLIENT_BINDING_NAME = 'decentdht'

TEST_SERVER_ADDR = '127.0.0.1'
TEST_SERVER_PORT = 57725

DHT_SERVER_PORT_BEGIN = 57756

THREAD_COUNT_LIST = [40]

MAX_OP_PER_TICKET_LIST = [500, 1000]

TARGET_THROUGHPUT_LIST = [-1]

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

def UpdateClientConfig(numOfNode):

	jsonObj = GetJsonFromFile(GetConfigFilePath())

	jsonObj['Enclaves']['DecentDHT']['Port'] = DHT_SERVER_PORT_BEGIN + (numOfNode - 1)

	WriteJsonToFile(GetConfigFilePath(), jsonObj)

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

	#Sets priority of the JVM:
	WaitFor(0.2)
	for p in pct.FindProcsByName('java'):
		p.nice(DEFAULT_PRIORITY)

	print('INFO:', 'Executed command:', ' '.join(procObj.args))
	print('INFO:', 'Waiting for process to be done...')
	procObj.wait()

	if procObj.returncode != 0:
		raise RuntimeError('YCSB command returned error.')

	print('INFO:', 'Done!')

def GetYcsbWorkloadPath(filename):

	return os.path.join(GetYcsbHomePath(), 'workloads', filename)

def LoadDatabase(conn, ycsbPath, outPathBase, workload, dist, recCount, numOfNode, threadCount, maxOpPerTicket):

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
	options += ['-p', ('recordcount=' + str(recCount * numOfNode))]
	options += ['-p', ('requestdistribution=' + dist)]
	options += ['-p', ('measurementtype=' + 'raw')]
	options += ['-p', ('measurement.raw.output_file=' + outRawPath)]

	command = ['cmd.exe', '/c', ycsbPath, 'load', CLIENT_BINDING_NAME, '-P', GetYcsbWorkloadPath(workload), '-threads', str(threadCount)]
	command += options
	command += ['>', outRepPath]

	print('INFO:', 'Loading database with maxOpPerTicket =', maxOpPerTicket)
	SetJavaSysProperty(maxOpPerTicket)

	st.SocketSendPack(conn, 'Start')
	ExecuteYcsbTestCommand(command)
	st.SocketSendPack(conn, 'End')

	WriteStrToFile(outSvrStatPath, st.SocketRecvPack(conn))

	WaitFor(5)

def RunTest(conn, ycsbPath, outPathBase, workload, dist, recCount, numOfNode, maxOp, maxTime, threadCount, maxOpPerTicket, targetThrp):

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

	command = ['cmd.exe', '/c', ycsbPath, 'run', CLIENT_BINDING_NAME]
	command += options
	command += ['>', outRepPath]

	print('INFO:', 'Running test with maxOpPerTicket =', maxOpPerTicket)
	SetJavaSysProperty(maxOpPerTicket)

	st.SocketSendPack(conn, 'Start')
	ExecuteYcsbTestCommand(command)
	st.SocketSendPack(conn, 'End')

	WriteStrToFile(outSvrStatPath, st.SocketRecvPack(conn))

	WaitFor(5)

def RunOneAttempt(conn, ycsbPath, outDir, workload, dist, recCount, numOfNode, maxOp, maxTime, attemptNum):


	CreateDirs(os.path.join(outDir, 'load'))
	loadThreadCount = THREAD_COUNT_LIST[len(THREAD_COUNT_LIST) - 1]
	loadMaxOpPerTicket = MAX_OP_PER_TICKET_LIST[len(MAX_OP_PER_TICKET_LIST) - 1]

	outPathBase = 'Attempt_' + '{0:02d}'.format(attemptNum) + '_' + '{0:02d}'.format(numOfNode) + '_' + '{0:02d}'.format(loadThreadCount) + '_' + str(loadMaxOpPerTicket) + '_-1'
	loadOutPathBase = os.path.join(outDir, 'load', outPathBase)
	LoadDatabase(conn, ycsbPath, loadOutPathBase, workload, dist, recCount, numOfNode, loadThreadCount, loadMaxOpPerTicket)

	for threadCount in THREAD_COUNT_LIST:
		for maxOpPerTicket in MAX_OP_PER_TICKET_LIST:
			for targetThrp in TARGET_THROUGHPUT_LIST:
				outPathBase = 'Attempt_' + '{0:02d}'.format(attemptNum) + '_' + '{0:02d}'.format(numOfNode) + '_' + '{0:02d}'.format(threadCount) + '_' + str(maxOpPerTicket)
				+ '_' + str(targetThrp)
				outPathBase = os.path.join(outDir, outPathBase)
				RunTest(conn, ycsbPath, outPathBase, workload, dist, recCount, numOfNode, maxOp, maxTime, threadCount, maxOpPerTicket, targetThrp)

	st.SocketSendPack(conn, 'Finished')

def SendNumOfNode(conn, numOfNode):

	st.SocketSend_uint64(conn, numOfNode)

	if st.SocketRecvPack(conn) != 'OK':
		raise RuntimeError('Server doesn\'t accept the numOfNode=' + numOfNode + ' !')

def RunOneTypeNodeSetup(serverConn, ycsbPath, outDir, workload, dist, recCount, numOfNode, maxOp, maxTime, attemptCount):

	UpdateClientConfig(numOfNode)

	for i in range(1, attemptCount + 1):

		#Tell server we have test to perform
		st.SocketSendPack(serverConn, 'Test')

		#Tell server how many node we need
		print('INFO:', 'Telling server how many node we need...')
		SendNumOfNode(serverConn, numOfNode)

		#Wait for server to complete the setup process
		print('INFO:', 'Waiting for server to complete the setup process...')
		clientSignal = st.SocketRecvPack(serverConn)
		if clientSignal != 'R':
			raise RuntimeError('Server error during setup process.')

		#Begin testing
		print('INFO:', 'Begin testing...')
		RunOneAttempt(serverConn, ycsbPath, outDir, workload, dist, recCount, numOfNode, maxOp, maxTime, i)
		print('INFO:', 'Finished one attempt.')

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
	parser.add_argument('--minNode', type=int, required=False)
	parser.add_argument('--maxNode', type=int, required=True)

	args = parser.parse_args()

	if (args.minNode != None and args.maxNode != None) and (args.minNode > args.maxNode):
		print('FATAL_ERR:', 'minNode should not be larger than maxNode!')
		exit(-1)

	if (args.minNode != None and args.minNode < 1):
		print('FATAL_ERR:', 'minNode should not be less than 1!')
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

	minNodeNum = 1 if args.minNode == None else args.minNode
	maxNodeNum = args.maxNode

	try:
		for i in range(minNodeNum, maxNodeNum + 1):
			RunOneTypeNodeSetup(conn, GetYcsbBinPath(), outDirPath, args.workload, args.dist, args.recN, i, args.maxOp, args.maxTime, args.attemptN)

		#Tell server we are done
		st.SocketSendPack(conn, 'Done')
	finally:
		conn.shutdown(socket.SHUT_RDWR)
		conn.close()

if __name__ == '__main__':
	sys.exit(main())
