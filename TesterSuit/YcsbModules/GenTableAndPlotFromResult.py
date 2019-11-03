import os
import sys
import time
import json
import argparse
import statistics
import sqlalchemy

import pandas as pd
import progressbar as pbar

if __name__ == '__main__':
	import ProgressBarConfig as pbarCfg
	import GraphDefinition
	import ResProcConfigParser
else:
	from . import ProgressBarConfig as pbarCfg
	from . import GraphDefinition
	from . import ResProcConfigParser

CSV_FILE_SUFFIX = '.csv'
EXCEL_FILE_SUFFIX = '.xlsx'
EXCEL_MACRO_POSTFIX = '.xlsm'
EXCEL_BUTTON_CFG = {'macro'  : 'DrawGraph',
                    'caption': 'Draw Graph',
                    'width'  : 120,
                    'height' : 20
                    }

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
		if filename.endswith(CSV_FILE_SUFFIX):
			root, ext = os.path.splitext(filename)
			dfWithNames.append((root, pd.read_csv(os.path.join(dirPath, filename))))

	return dfWithNames

def WriteExcel(outPath, dataTable):

	print('INFO:', 'Writting results into', outPath + EXCEL_FILE_SUFFIX, '...')

	with pd.ExcelWriter(outPath + EXCEL_FILE_SUFFIX, engine='xlsxwriter') as writer:
		dataTable[0][1].to_excel(writer, sheet_name='Index')
		i = 0
		for item in pbar.progressbar(dataTable, **pbarCfg.PBAR_ARGS):
			if i != 0:
				item[1].to_excel(writer, sheet_name=('Sheet_' + '{0:02d}'.format(i)))

			i += 1

		#print('INFO:', 'Writting macro-enables Excel file,', outPath + EXCEL_MACRO_POSTFIX, '...')
		macroWorkBook = writer.book
		#macroWorkBook.filename = outPath + EXCEL_MACRO_POSTFIX
		for i, item in zip(range(0, len(dataTable)), dataTable):
			if i == 0:
				continue

			sheetName = 'Sheet_' + '{0:02d}'.format(i)
			wSheet = macroWorkBook.get_worksheet_by_name(sheetName)
			wSheet.insert_button(item[1].shape[0] + 2, 0, EXCEL_BUTTON_CFG)

		writer.save()

def SelectDataAndDrawGraphs(dirPath, cfgJson):

	#Convert paths to absolute path
	#    Directory path
	dirPath = os.path.abspath(dirPath)

	if (not os.path.exists(dirPath)) or (os.path.isfile(dirPath)):
		raise RuntimeError('The given directory:' + dirPath + 'does not exist, or it is a file!')

	#Create an in-memory SQLite database.
	sqlEngine = sqlalchemy.create_engine('sqlite://', echo=False)
	LoadSqlFunctions(sqlEngine)

	#Read all full data tables
	dfWithNames = ReadAllCsvFiles(dirPath)

	#Parse graph definition
	graphDefs = GraphDefinition.GraphDefinition(jsonObj=cfgJson)

	#Load SQL database
	print('INFO:', 'Loading tables into SQL database...')
	for dfwithName in pbar.progressbar(dfWithNames, **pbarCfg.PBAR_ARGS):
		dfwithName[1].to_sql(dfwithName[0], con=sqlEngine, if_exists='replace')

	#Execute SQL queries and generate data tables
	print('INFO:', 'Executing SQL queries...')
	dataTable = graphDefs.GetCombinedDataTablesWithIndexTable(sqlEngine)

	#Output to Excel file
	excelOutPath = os.path.join(dirPath, 'data_for_graphs')
	WriteExcel(excelOutPath, dataTable)

def main():

	print()

	parser = argparse.ArgumentParser()
	parser.add_argument('--dir', required=True, type=str)
	parser.add_argument('--config', required=True, type=str)

	args = parser.parse_args()

	# Graph Definition path
	graphDefPath = os.path.abspath(args.graphDef)

	if not os.path.isfile(args.graphDef):
		print('FATAL_ERR:', 'The graph definition file,', args.graphDef, 'does not exist!')
		exit(-1)

	cfgJson = json.loads(GetFullStrFromFile(graphDefPath))

	SelectDataAndDrawGraphs(args.dir, cfgJson)

	print()

	return 0

if __name__ == '__main__':
	sys.exit(main())
