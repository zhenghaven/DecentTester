import json
import enum
import pandas as pd

class GraphTypes(enum.Enum):
	CATEGORY = 0
	XY       = 1

	def ShortName(self):
		return self.name

class DefaultSeries:

	def __init__(self, jsonObj=None, name=None, xField=None, yField=None, table=None, where=None, groupBy=None, orderBy=None):
		if jsonObj is not None:
			self.name    = jsonObj['name']    if 'name'    in jsonObj else name
			self.xField  = jsonObj['xField']  if 'xField'  in jsonObj else xField
			self.yField  = jsonObj['yField']  if 'yField'  in jsonObj else yField
			self.table   = jsonObj['table']   if 'table'   in jsonObj else table
			self.where   = jsonObj['where']   if 'where'   in jsonObj else where

			self.groupBy = [x for x in jsonObj['groupBy']] if 'groupBy' in jsonObj else groupBy
			self.orderBy = [x for x in jsonObj['orderBy']] if 'orderBy' in jsonObj else orderBy
		else:
			self.name = name
			self.xField = xField
			self.yField = yField
			self.table = table
			self.where = where
			self.groupBy = groupBy
			self.orderBy = orderBy

class SeriesBase:

	def __init__(self, jsonObj, defaultSeries):
		self.name = jsonObj['name'] if 'name' in jsonObj else defaultSeries.name
		self.xField = jsonObj['xField'] if 'xField' in jsonObj else defaultSeries.xField
		self.yField = jsonObj['yField'] if 'yField' in jsonObj else defaultSeries.yField
		self.table = jsonObj['table'] if 'table' in jsonObj else defaultSeries.table
		self.where = jsonObj['where'] if 'where' in jsonObj else defaultSeries.where
		self.groupBy = [x for x in jsonObj['groupBy']] if 'groupBy' in jsonObj else defaultSeries.groupBy
		self.orderBy = [x for x in jsonObj['orderBy']] if 'orderBy' in jsonObj else defaultSeries.orderBy

	def GetMidXColName(self):
		return self.xField

	def GetMinXColName(self):
		return self.xField

	def GetMaxXColName(self):
		return self.xField

	def GetMidYColName(self):
		return self.name;

	def GetMinYColName(self):
		return self.name + ' Min Err'

	def GetMaxYColName(self):
		return self.name + ' Max Err'

	def GenMidSqlQuery(self):
		return self.GenMidSelectStr() + '\n' + self.GenMidFromStr() + '\n' + self.GenMidWhereStr() + '\n' + self.GenMidGroupByStr() + '\n' + self.GenMidOrderByStr()

	def GenMinSqlQuery(self):
		return self.GenMinSelectStr() + '\n' + self.GenMinFromStr() + '\n' + self.GenMinWhereStr() + '\n' + self.GenMinGroupByStr() + '\n' + self.GenMinOrderByStr()

	def GenMaxSqlQuery(self):
		return self.GenMaxSelectStr() + '\n' + self.GenMaxFromStr() + '\n' + self.GenMaxWhereStr() + '\n' + self.GenMaxGroupByStr() + '\n' + self.GenMaxOrderByStr()

	def GenMidSelectStr(self):
		return 'SELECT' + ' ' + self.xField + ' AS ' + '"' + self.GetMidXColName() + '"' + ', ' + 'median(' + self.yField + ')' + ' AS ' + '"' + self.GetMidYColName() + '"'

	def GenMinSelectStr(self):
		return 'SELECT' + ' ' + self.xField + ' AS ' + '"' + self.GetMinXColName() + '"' + ', ' + 'minerr(' + self.yField + ')' + ' AS ' + '"' + self.GetMinYColName() + '"'

	def GenMaxSelectStr(self):
		return 'SELECT' + ' ' + self.xField + ' AS ' + '"' + self.GetMaxXColName() + '"' + ', ' + 'maxerr(' + self.yField + ')' + ' AS ' + '"' + self.GetMaxYColName() + '"'

	def GenFromStr(self):
		return 'FROM' + ' ' + self.table

	def GenMidFromStr(self):
		return self.GenFromStr()

	def GenMinFromStr(self):
		return self.GenFromStr()

	def GenMaxFromStr(self):
		return self.GenFromStr()

	def GenWhereStr(self):
		return 'WHERE' + ' ' + self.where

	def GenMidWhereStr(self):
		return self.GenWhereStr()

	def GenMinWhereStr(self):
		return self.GenWhereStr()

	def GenMaxWhereStr(self):
		return self.GenWhereStr()

	def GenGroupByStr(self):
		if len(self.groupBy) > 0:
			res = 'GROUP BY'
			i = 0
			for item in self.groupBy:
				res += ((' ' if i == 0 else ', ') + item)
				i += 1
			return res
		else:
			return ''

	def GenMidGroupByStr(self):
		return self.GenGroupByStr()

	def GenMinGroupByStr(self):
		return self.GenGroupByStr()

	def GenMaxGroupByStr(self):
		return self.GenGroupByStr()

	def GenOrderByStr(self):
		if len(self.orderBy) > 0:
			res = 'ORDER BY'
			i = 0
			for item in self.orderBy:
				res += ((' ' if i == 0 else ', ') + item)
				i += 1
			return res
		else:
			return ''

	def GenMidOrderByStr(self):
		return self.GenOrderByStr()

	def GenMinOrderByStr(self):
		return self.GenOrderByStr()

	def GenMaxOrderByStr(self):
		return self.GenOrderByStr()

	def GetMidDataFromSql(self, sqlEngine):
		return pd.read_sql_query(self.GenMidSqlQuery(), con=sqlEngine)

	def GetMinDataFromSql(self, sqlEngine):
		return pd.read_sql_query(self.GenMinSqlQuery(), con=sqlEngine)

	def GetMaxDataFromSql(self, sqlEngine):
		return pd.read_sql_query(self.GenMaxSqlQuery(), con=sqlEngine)

	def TestPrint(self):
		print(self.GenMidSqlQuery())

class SeriesCategory(SeriesBase):

	def __init__(self, jsonObj, defaultSeries):
		super(SeriesCategory, self).__init__(jsonObj, defaultSeries)

	def GetMidDataFromSql(self, sqlEngine):
		return super(SeriesCategory, self).GetMidDataFromSql(sqlEngine).set_index(super(SeriesCategory, self).GetMidXColName(), drop=True)

	def GetMinDataFromSql(self, sqlEngine):
		return super(SeriesCategory, self).GetMinDataFromSql(sqlEngine).set_index(super(SeriesCategory, self).GetMinXColName(), drop=True)

	def GetMaxDataFromSql(self, sqlEngine):
		return super(SeriesCategory, self).GetMaxDataFromSql(sqlEngine).set_index(super(SeriesCategory, self).GetMaxXColName(), drop=True)

class SeriesXy(SeriesBase):

	def __init__(self, jsonObj, defaultSeries):
		super(SeriesXy, self).__init__(jsonObj, defaultSeries)

	def GetMidXColName(self):
		return super(SeriesXy, self).name + '.' + super(SeriesXy, self).xField

	def GetMinXColName(self):
		return super(SeriesXy, self).name + '.' + super(SeriesXy, self).xField + ' Min Err'

	def GetMaxXColName(self):
		return super(SeriesXy, self).name + '.' + super(SeriesXy, self).xField + ' Max Err'

	def GenMidSelectStr(self):
		return 'SELECT' + ' ' + 'median(' + self.xField + ')' + ', ' + 'median(' + self.yField + ')' + ' AS ' + '"' + self.name + '"'

	def GenMinSelectStr(self):
		return 'SELECT' + ' ' + 'minerr(' + self.xField + ')' + ', ' + 'minerr(' + self.yField + ')' + ' AS ' + '"' + self.name + '"'

	def GenMaxSelectStr(self):
		return 'SELECT' + ' ' + 'maxerr(' + self.xField + ')' + ', ' + 'maxerr(' + self.yField + ')' + ' AS ' + '"' + self.name + '"'

class Graph:

	def __init__(self, jsonObj):
		self.comment = jsonObj['comment']
		self.xLabel = jsonObj['xLabel']
		self.yLabel = jsonObj['yLabel']
		self.type = GraphTypes[jsonObj['type']]
		self.defaultSeries = DefaultSeries(jsonObj=(None if 'seriesDefault' not in jsonObj else jsonObj['seriesDefault']))
		self.series = []
		seriesArray = jsonObj['series']
		for item in seriesArray:
			if self.type is GraphTypes.CATEGORY:
				self.series.append(SeriesCategory(item, self.defaultSeries))
			elif self.type is GraphTypes.XY:
				self.series.append(SeriesXy(item, self.defaultSeries))
			else:
				raise RuntimeError('Unsupported series type.')

	def GetTitle(self):
		return self.xLabel + ' VS. ' + self.yLabel + ' (' + self.comment + ')'

	def GetMidDataTable(self, sqlEngine):
		seriesDataFs = []
		for item in self.series:
			seriesDataFs.append(item.GetMidDataFromSql(sqlEngine))
		return pd.concat(seriesDataFs, axis=1)

	def GetMinDataTable(self, sqlEngine):
		seriesDataFs = []
		for item in self.series:
			seriesDataFs.append(item.GetMinDataFromSql(sqlEngine))
		return pd.concat(seriesDataFs, axis=1)

	def GetMaxDataTable(self, sqlEngine):
		seriesDataFs = []
		for item in self.series:
			seriesDataFs.append(item.GetMaxDataFromSql(sqlEngine))
		return pd.concat(seriesDataFs, axis=1)

	def GetDataTable(self, sqlEngine):
		print('INFO:', 'Generating data table,', self.GetTitle(), '...')
		return pd.concat([self.GetMidDataTable(sqlEngine), self.GetMinDataTable(sqlEngine), self.GetMaxDataTable(sqlEngine)], axis=1)

	def GetSeriesCount(self):
		return len(self.series)

	def TestPrint(self):
		for item in self.series:
			item.TestPrint()

class GraphDefinition:

	def __init__(self, jsonStr=None, jsonObj=None):
		if jsonObj is None and jsonStr is None:
			raise RuntimeError('Either JSON string or JSON object should be given.')

		if jsonObj is None:
			jsonObj = json.loads(jsonStr)

		self.graphs = [Graph(item) for item in jsonObj['graphs']]

	def GetCombinedDataTables(self, sqlEngine):
		return [(graph, graph.GetDataTable(sqlEngine))for graph in self.graphs]

	def GetCombinedDataTablesWithIndexTable(self, sqlEngine):
		dataTables = self.GetCombinedDataTables(sqlEngine)
		idxRows = [[('Sheet_' + '{0:02d}'.format(i + 1)), item[0].GetTitle(), item[0].xLabel, item[0].yLabel, item[0].GetSeriesCount(), item[1].shape[0], item[0].type.ShortName()] \
		           for i, item in zip(range(0, len(dataTables)), dataTables)]

		idxDataF = pd.DataFrame(data=idxRows, columns=['Sheet#', 'Title', 'X_Label',  'Y_Label', 'seriesCount', 'recCount', 'graphType'])
		idxDataF.set_index('Sheet#', drop=True, inplace=True)

		return [(None, idxDataF)] + dataTables

	def TestPrint(self):
		for item in self.graphs:
			item.TestPrint()
