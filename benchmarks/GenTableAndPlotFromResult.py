import os
import sys
import time
import argparse
import statistics
import sqlalchemy
import progressbar as pbar
import pandas as pd
from python_utils.terminal import get_terminal_size

DEFAULT_TABLE_NAME = 'FullTestResult'

CSV_POSTFIX = '.csv'
EXCEL_POSTFIX = '.xlsx'

KEY_WORD_START = 'STARTGRAPH'
KEY_WORD_END = 'ENDGRAPH'
KEY_WORD_INDEX = 'INDEX'
KEY_WORD_X_AXIS = 'X_AXIS'
KEY_WORD_Y_AXIS = 'Y_AXIS'

TERM_WIDTH = int(get_terminal_size()[0] * (2/3))

PBAR_WIDGETS = [
	pbar.Percentage(), ' (', pbar.SimpleProgress(), ') ',
	pbar.Bar(marker='█', left=' |', right='| ', fill='▁'),
	' ', pbar.Timer(),
	' | ETA ', pbar.ETA()
]

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
	for filename in pbar.progressbar(os.listdir(dirPath), widgets=PBAR_WIDGETS, term_width=TERM_WIDTH):
		if filename.endswith(CSV_POSTFIX):
			root, ext = os.path.splitext(filename)
			dfWithNames.append((root, pd.read_csv(os.path.join(dirPath, filename))))

	return dfWithNames

class GraphDefinition:

	def __init__(self, tableCmt, xLabel, yLabel, index, midQuery, minErrQuery, maxErrQuery):
		self.tableCmt = tableCmt # <- Table comments
		self.xLabel = xLabel # <- Label for the X-Axis
		self.yLabel = yLabel # <- Label for the X-Axis
		self.index = index # <- name of the index column
		self.midQuery = midQuery # <- Query to get median values
		self.minErrQuery = minErrQuery # <- Query to get min error
		self.maxErrQuery = maxErrQuery # <- Query to get max error
		self.midDataF = None # <- Pandas DataFrame for median values
		self.minErrDataF = None # <- Pandas DataFrame for min error
		self.maxErrDataF = None # <- Pandas DataFrame for max error

	def ExecuteQueries(self, sqlEngine):
		self.midDataF = pd.read_sql_query(self.midQuery, con=sqlEngine)
		self.minErrDataF = pd.read_sql_query(self.minErrQuery, con=sqlEngine)
		self.maxErrDataF = pd.read_sql_query(self.maxErrQuery, con=sqlEngine)

		self.midDataF.set_index(self.index, drop=True, inplace=True)
		self.minErrDataF.set_index(self.index, drop=True, inplace=True)
		self.maxErrDataF.set_index(self.index, drop=True, inplace=True)

	def GetConcatenatedDataFrame(self):
		return pd.concat([self.midDataF, self.minErrDataF, self.maxErrDataF], axis=1)

	def GetTitle(self):
		res = self.xLabel + ' vs. ' + self.yLabel
		if self.tableCmt != None and len(self.tableCmt) > 0:
			res = res + ' (' + self.tableCmt + ')'

		return res

	def __str__(self):
		res = 'TABLE_COMMENTS: ' + self.tableCmt + '\n'
		res = res + 'X-Axis: ' + self.xLabel + '\n'
		res = res + 'Y-Axis: ' + self.yLabel + '\n'
		res = res + 'INDEX: ' + self.index + '\n'
		res = res + 'queries:\n'
		for query in self.queries:
			res = res + '\t' + query + '\n'

		return res

def ReadSqlQueries(sqlPath):

	queries = []
	with open(sqlPath, 'r') as sqlFile:
		fullText = sqlFile.read()
		queries = [s.strip() for s in fullText.split(';')]

	graphQurSets = []
	tmpSet = []
	for query in queries:
		if len(query) == 0:
			continue
		elif query.startswith(KEY_WORD_START):
			tmpSet = [query]
		elif query.startswith(KEY_WORD_END):
			graphQurSets.append(tmpSet)
		else:
			tmpSet.append(query)

	graphDefs = []
	for graphQurSet in graphQurSets:
		tableCmt, xLabel, yLabel, index, midQuery, minErrQuery, maxErrQuery = '', '', '', '', '', '', ''
		queryCount = 0
		for query in graphQurSet:
			if query.startswith(KEY_WORD_START):
				tableCmt = (query.replace(KEY_WORD_START, '', 1)).strip()
			elif query.startswith(KEY_WORD_X_AXIS):
				xLabel = (query.replace(KEY_WORD_X_AXIS, '', 1)).strip()
			elif query.startswith(KEY_WORD_Y_AXIS):
				yLabel = (query.replace(KEY_WORD_Y_AXIS, '', 1)).strip()
			elif query.startswith(KEY_WORD_INDEX):
				index = (query.replace(KEY_WORD_INDEX, '', 1)).strip()
			elif queryCount == 0:
				midQuery = query
				queryCount = queryCount + 1
			elif queryCount == 1:
				minErrQuery = query
				queryCount = queryCount + 1
			elif queryCount == 2:
				maxErrQuery = query
				queryCount = queryCount + 1
			else:
				raise RuntimeError('GraphDefinition parse error: too much queries.')

		graphDefs.append(GraphDefinition(tableCmt, xLabel, yLabel, index, midQuery, minErrQuery, maxErrQuery))

	return graphDefs

def ConstructIndexSheet(graphDefs):

	rows = []
	i = 1
	for graphDef in graphDefs:
		rows.append([('Sheet_' + '{0:02d}'.format(i)), graphDef.GetTitle(), graphDef.xLabel, graphDef.yLabel, graphDef.midDataF.shape[0]])

	dataF = pd.DataFrame(data=rows, columns=['Sheet#', 'Title', 'X_Label',  'Y_Label', 'recCount'])
	dataF.set_index('Sheet#', drop=True, inplace=True)
	return dataF

def WriteExcel(outPath, graphDefs):

	print('INFO:', 'Writting results into', outPath, '...')

	with pd.ExcelWriter(outPath) as writer:
		ConstructIndexSheet(graphDefs).to_excel(writer, sheet_name='Index')
		i = 1
		for graphDef in pbar.progressbar(graphDefs, widgets=PBAR_WIDGETS, term_width=TERM_WIDTH):
			graphDef.GetConcatenatedDataFrame().to_excel(writer, sheet_name=('Sheet_' + '{0:02d}'.format(i)))
			i += 1

def main():

	print()

	parser = argparse.ArgumentParser()
	parser.add_argument('--dir', required=True, type=str)
	parser.add_argument('--sql', required=True, type=str)

	args = parser.parse_args()

	#Convert directory path to absolute path
	dirPath = os.path.abspath(args.dir)

	if (not os.path.exists(dirPath)) or (os.path.isfile(dirPath)):
		print('FATAL_ERR:', 'The input directory:', dirPath, 'does not exist, or it is a file!')
		exit(-1)

	sqlPath = os.path.abspath(args.sql)

	if not os.path.isfile(sqlPath):
		print('FATAL_ERR:', 'The SQL file,', sqlPath, 'does not exist!')
		exit(-1)

	#Create an in-memory SQLite database.
	sqlEngine = sqlalchemy.create_engine('sqlite://', echo=False)
	LoadSqlFunctions(sqlEngine)

	dfWithNames = ReadAllCsvFiles(dirPath)

	graphDefs = ReadSqlQueries(sqlPath)

	print('INFO:', 'Loading tables into SQL database...')
	for dfwithName in pbar.progressbar(dfWithNames, widgets=PBAR_WIDGETS, term_width=TERM_WIDTH):
		dfwithName[1].to_sql(dfwithName[0], con=sqlEngine, if_exists='replace')

	print('INFO:', 'Executing SQL queries...')
	for graphDef in pbar.progressbar(graphDefs, widgets=PBAR_WIDGETS, term_width=TERM_WIDTH):
		graphDef.ExecuteQueries(sqlEngine)

	excelOutPath = os.path.join(dirPath, 'data_for_graphs' + EXCEL_POSTFIX)
	WriteExcel(excelOutPath, graphDefs)

	print()

	return 0

if __name__ == '__main__':
	sys.exit(main())
