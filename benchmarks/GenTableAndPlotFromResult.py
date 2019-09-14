import os
import sys
import time
import argparse
import statistics
import sqlalchemy
import GraphDefinition
import pandas as pd
import progressbar as pbar
import ProgressBarConfig as pbarCfg

DEFAULT_TABLE_NAME = 'FullTestResult'

CSV_POSTFIX = '.csv'
EXCEL_POSTFIX = '.xlsx'

class MyMedian:

	def __init__(self):
		self.data = []

	def step(self, value):
		self.data.append(value)

	def finalize(self):
		return statistics.median(self.data)

class MyMinerr:

	def __init__(self):
		self.data = []

	def step(self, value):
		self.data.append(value)

	def finalize(self):
		return statistics.median(self.data) - min(self.data)

class MyMaxerr:

	def __init__(self):
		self.data = []

	def step(self, value):
		self.data.append(value)

	def finalize(self):
		return max(self.data) - statistics.median(self.data)

def LoadSqlFunctions(engine):

	conn = engine.raw_connection()
	conn.create_aggregate("median", 1, MyMedian)
	conn.create_aggregate("minerr", 1, MyMinerr)
	conn.create_aggregate("maxerr", 1, MyMaxerr)
	conn.close()

def ReadAllCsvFiles(dirPath):

	dfWithNames = []

	print('INFO:', 'Reading all CSV files...')
	for filename in pbar.progressbar(os.listdir(dirPath), **pbarCfg.PBAR_ARGS):
		if filename.endswith(CSV_POSTFIX):
			root, ext = os.path.splitext(filename)
			dfWithNames.append((root, pd.read_csv(os.path.join(dirPath, filename))))

	return dfWithNames

def WriteExcel(outPath, dataTable):

	print('INFO:', 'Writting results into', outPath, '...')

	with pd.ExcelWriter(outPath) as writer:
		dataTable[0][1].to_excel(writer, sheet_name='Index')
		i = 0
		for item in pbar.progressbar(dataTable, **pbarCfg.PBAR_ARGS):
			if i != 0:
				item[1].to_excel(writer, sheet_name=('Sheet_' + '{0:02d}'.format(i)))

			i += 1

def GetStrFromFile(filename):

	file = open(filename, 'r')
	res = file.read()
	file.close()
	return res

def main():

	print()

	parser = argparse.ArgumentParser()
	parser.add_argument('--dir', required=True, type=str)
	parser.add_argument('--graphDef', required=True, type=str)

	args = parser.parse_args()

	#Convert paths to absolute path
	#    Directory path
	dirPath = os.path.abspath(args.dir)

	if (not os.path.exists(dirPath)) or (os.path.isfile(dirPath)):
		print('FATAL_ERR:', 'The input directory:', dirPath, 'does not exist, or it is a file!')
		exit(-1)

	#    Graph Definition path
	graphDefPath = os.path.abspath(args.graphDef)

	if not os.path.isfile(args.graphDef):
		print('FATAL_ERR:', 'The graph definition file,', args.graphDef, 'does not exist!')
		exit(-1)

	#Create an in-memory SQLite database.
	sqlEngine = sqlalchemy.create_engine('sqlite://', echo=False)
	LoadSqlFunctions(sqlEngine)

	#Read all full data tables
	dfWithNames = ReadAllCsvFiles(dirPath)

	#Parse graph definition
	graphDefs = GraphDefinition.GraphDefinition(jsonStr=GetStrFromFile(graphDefPath))

	#Load SQL database
	print('INFO:', 'Loading tables into SQL database...')
	for dfwithName in pbar.progressbar(dfWithNames, **pbarCfg.PBAR_ARGS):
		dfwithName[1].to_sql(dfwithName[0], con=sqlEngine, if_exists='replace')

	#Execute SQL queries and generate data tables
	print('INFO:', 'Executing SQL queries...')
	dataTable = graphDefs.GetCombinedDataTablesWithIndexTable(sqlEngine)

	#Output to Excel file
	excelOutPath = os.path.join(dirPath, 'data_for_graphs' + EXCEL_POSTFIX)
	WriteExcel(excelOutPath, dataTable)

	print()

	return 0

if __name__ == '__main__':
	sys.exit(main())
