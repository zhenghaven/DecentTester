import os
import sys
import openpyxl
import argparse
import sqlalchemy
import progressbar
import pandas as pd

COLUMN_NAMES = ['Name_Prefix', 'Attempt', 'Num_of_Node', 'Num_of_Thread', 'Ops_per_Session', 'Ops', 'Time_Elapsed_ms', 'Throughput_op_per_s', 'Percentile_Latency_us']

COLUMN_TYPES = {'Attempt': 'int32', 'Num_of_Node': 'int32', 'Num_of_Thread': 'int32', 'Ops_per_Session': 'int32'}

EXCEL_POSTFIX = '.xlsx'

DEFAULT_TABLE_NAME = 'FullTestResult'

def PreProcCsv(oriFilePath, resFilePath):

	inputfile= open(oriFilePath, 'r')
	outputfile = open(resFilePath, "w")

	outputfile.write('Op,Timestamp_ms,Latency_us\n')

	lines = inputfile.readlines()
	for line in lines:
		if 'timestamp(ms)' not in line:
			outputfile.write(line)

	inputfile.close()
	outputfile.close()

def TrimOffWarmUpPhase(dataF, warmUpTime):

	dataF.sort_values(by=['Timestamp_ms'], inplace=True)
	dataF = dataF.reset_index(drop=True)

	length = dataF.shape[0]
	starttime = dataF.iat[0,1]
	trimindex = 0

	for i in range(0, length):
		if dataF.iat[i,1] - starttime >= warmUpTime * 1000:
			trimindex = i
			break

	return dataF[trimindex:].reset_index(drop=True)

def ProcOneResultSet(inputfilepath, warmUpTime, percentile):

	time_ignore = int()

	#Generate intermediate file:
	immedfilepath = inputfilepath + '.tmp'
	PreProcCsv(inputfilepath, immedfilepath)

	dataF = pd.read_csv(immedfilepath)
	os.remove(immedfilepath)

	dataF = TrimOffWarmUpPhase(dataF, warmUpTime)
	#dataF.to_csv(immedfilepath)

	totalOps = dataF.shape[0]

	if totalOps == 0:
		return [0, 0, 0, 0]

	timeElapsedMs = dataF.iat[totalOps - 1, 1] - dataF.iat[0, 1] #In millisecond
	timeElapsedS = timeElapsedMs / 1000 # In sec
	throughtput = totalOps / timeElapsedS
	latencyPer = dataF.Latency_us.quantile(q=(percentile / 100.0), interpolation='higher')

	return [totalOps, timeElapsedMs, throughtput, latencyPer]

def ParseFileName(filepath):

	root, ext = os.path.splitext(filepath)
	filename = os.path.basename(root)

	components = filename.split('_')

	return components

def SummaryOneResultSet(filepath, warmUpTime, percentile):

	filenameRes = ParseFileName(filepath)
	dataRes = ProcOneResultSet(filepath, warmUpTime, percentile)

	return filenameRes + dataRes

def ConstructIndexSheet(sqlList):

	rows = [['Sheet_01', 'Full summary']]
	i = 2
	for sqlQuery in sqlList:
		rows.append([('Sheet_' + '{0:02d}'.format(i)), sqlQuery])

	return pd.DataFrame(data=rows, columns=['Sheet', 'Content'])

def ConstructExcelSheets(summaryDataF, sqlList):

	dataFs = [ConstructIndexSheet(sqlList), summaryDataF]

	if sqlList != None and len(sqlList) > 0:

		#Create an in-memory SQLite database.
		engine = sqlalchemy.create_engine('sqlite://', echo=False)

		summaryDataF.to_sql(DEFAULT_TABLE_NAME, con=engine, if_exists='replace')

		print('INFO:', 'Executing SQL queries...')

		proBar = progressbar.ProgressBar()

		for sqlQuery in proBar(sqlList):
			sqlRes = pd.read_sql_query(sqlQuery, con=engine)
			dataFs.append(sqlRes)

	return dataFs

def WriteExcel(outPath, dataFs):

	print('INFO:', 'Writting results into', outPath, '...')

	proBar = progressbar.ProgressBar()

	with pd.ExcelWriter(outPath) as writer:
		i = 0
		for dataF in proBar(dataFs):
			if i == 0:
				dataF.to_excel(writer, sheet_name='Index')
			else:
				dataF.to_excel(writer, sheet_name=('Sheet_' + '{0:02d}'.format(i)))

			i += 1

def ReadSqlQueries(sqlPath):

	if sqlPath == None:

		return []

	else:

		sqlFile = open(sqlPath, 'r')
		sqlQueries = sqlFile.readlines()
		sqlFile.close()
		return sqlQueries

def main():

	print()

	parser = argparse.ArgumentParser()
	parser.add_argument('--dir', required=True)
	parser.add_argument('--warmUpTime', required=True, type=int)
	parser.add_argument('--percentile', required=True, type=int)
	parser.add_argument('--out', required=True)
	parser.add_argument('--sql', required=False)

	args = parser.parse_args()

	#Convert directory path to absolute path
	dirPath = os.path.abspath(args.dir)

	if (not os.path.exists(dirPath)) or (os.path.isfile(dirPath)):
		print('FATAL_ERR:', 'The input directory:', dirPath, 'does not exist, or it is a file!')
		exit(-1)

	outPath = os.path.abspath(args.out + EXCEL_POSTFIX)

	if os.path.exists(outPath):
		print('FATAL_ERR:', 'The output file path:', outPath, 'already exist!')
		exit(-1)

	if args.sql != None:

		sqlPath = os.path.abspath(args.sql)

		if not os.path.isfile(sqlPath):
			print('FATAL_ERR:', 'The SQL file,', outPath, 'does not exist!')
			exit(-1)

	else:

		sqlPath = None

	sqlQueries = ReadSqlQueries(sqlPath)

	rows = []

	print('INFO:', 'Processing raw data...')

	proBar = progressbar.ProgressBar()

	#iterate through files in the directory
	for filename in proBar(os.listdir(dirPath)):

		#looking for all csv files
		if filename.endswith(".csv"):

			filepath = os.path.join(dirPath, filename)

			#Make sure it is a file (not a directory)
			if os.path.isfile(filepath):

				#print('.', end='', flush=True)
				row = SummaryOneResultSet(filepath, args.warmUpTime, args.percentile)
				rows.append(row)

	summaryDataF = pd.DataFrame(data=rows, columns=COLUMN_NAMES)

	summaryDataF = summaryDataF.astype(COLUMN_TYPES)

	dataFs = ConstructExcelSheets(summaryDataF, sqlQueries)

	WriteExcel(outPath, dataFs)

	print()

if __name__ == '__main__':
	sys.exit(main())
