import os
import json
import enum
import pandas as pd               # pip install pandas
import plotly.graph_objects as go # pip install plotly==4.2.1 requests && npm install -g electron@1.8.4 orca
import plotly

if __name__ == '__main__':
	import ConfigParser
else:
	from . import ConfigParser

PLOTY_MARKER_SELECTED_SYMBOLS = [
	'circle',			'square',			'diamond',			'cross',			'x',
	'star',				'hexagram',			'hourglass',		'triangle-up',		'triangle-down',
	'triangle-left',	'triangle-right',	'pentagon',			'hexagon',			'triangle-ne',
	'triangle-se',		'triangle-sw',		'triangle-nw'
]

class GraphTypes(enum.Enum):

	CATEGORY = (0, 'category')
	XY       = (1, 'linear')
	LOG      = (2, 'log')

	def __init__(self, idx, plotyType):

		self.idx = idx
		self.plotyType = plotyType

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
		self.plotlyLayoutUpt = jsonObj['PlotlyLayout'] if 'PlotlyLayout' in jsonObj else None

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
		return 'FROM' + ' ' + '"' + self.table + '"'

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

	def GetMidXY(self, sqlEngine):
		pass

	def GetPlotyErrorXY(self, sqlEngine):
		pass

	def TestPrint(self):
		print(self.GenMidSqlQuery())

	def GetScatter(self, sqlEngine, idx, markerSym = None):

		if markerSym is None and idx >= len(PLOTY_MARKER_SELECTED_SYMBOLS):
			raise RuntimeError('The number of series is more than the selected marker symbols')

		markerSym = markerSym if markerSym is not None else PLOTY_MARKER_SELECTED_SYMBOLS[idx]

		midXY = self.GetMidXY(sqlEngine)
		errorXY = self.GetPlotyErrorXY(sqlEngine)

		scatter = {}
		if 'X' in errorXY and 'Y' in errorXY:
			scatter = {
				'name' : self.name,
				'mode' : 'lines+markers',
				'marker' : {'symbol' : markerSym, 'size' : 13},
				'x' : midXY['X'],
				'y' : midXY['Y'],
				'error_x' : errorXY['X'],
				'error_y' : errorXY['Y']
			}
		elif 'X' in errorXY:
			scatter = {
				'name' : self.name,
				'mode' : 'lines+markers',
				'marker' : {'symbol' : markerSym, 'size' : 13},
				'x' : midXY['X'],
				'y' : midXY['Y'],
				'error_x' : errorXY['X']
			}
		elif 'Y' in errorXY:
			scatter = {
				'name' : self.name,
				'mode' : 'lines+markers',
				'marker' : {'symbol' : markerSym, 'size' : 13},
				'x' : midXY['X'],
				'y' : midXY['Y'],
				'error_y' : errorXY['Y']
			}
		else:
			scatter = {
				'name' : self.name,
				'mode' : 'lines+markers',
				'marker' : {'symbol' : markerSym, 'size' : 13},
				'x' : midXY['X'],
				'y' : midXY['Y']
			}

		ConfigParser.RecursiveUpdateDict(scatter, self.plotlyLayoutUpt)
		return go.Scatter(**scatter)

class SeriesCategory(SeriesBase):

	def __init__(self, jsonObj, defaultSeries):
		super(SeriesCategory, self).__init__(jsonObj, defaultSeries)

	def GetMidDataFromSql(self, sqlEngine):
		return super(SeriesCategory, self).GetMidDataFromSql(sqlEngine).set_index(super(SeriesCategory, self).GetMidXColName(), drop=True)

	def GetMinDataFromSql(self, sqlEngine):
		return super(SeriesCategory, self).GetMinDataFromSql(sqlEngine).set_index(super(SeriesCategory, self).GetMinXColName(), drop=True)

	def GetMaxDataFromSql(self, sqlEngine):
		return super(SeriesCategory, self).GetMaxDataFromSql(sqlEngine).set_index(super(SeriesCategory, self).GetMaxXColName(), drop=True)

	def GetMidXY(self, sqlEngine):
		df = self.GetMidDataFromSql(sqlEngine)
		return { 'X' : df.index.tolist(), 'Y' : df[df.columns[0]].tolist()}

	def GetPlotyErrorXY(self, sqlEngine):
		minDF = self.GetMinDataFromSql(sqlEngine)
		maxDF = self.GetMaxDataFromSql(sqlEngine)

		return {
			'Y' : {
				'type' :     'data',
				'symmetric' : False,
				'array' :      maxDF[maxDF.columns[0]].tolist(),
				'arrayminus' : minDF[minDF.columns[0]].tolist()
			}
		}

class SeriesXy(SeriesBase):

	def __init__(self, jsonObj, defaultSeries):
		super(SeriesXy, self).__init__(jsonObj, defaultSeries)

	def GetMidXColName(self):
		return self.xField

	def GetMinXColName(self):
		return self.xField + '_Min_Err'

	def GetMaxXColName(self):
		return self.xField + '_Max_Err'

	def GenMidSelectStr(self):
		return 'SELECT' + ' ' + 'median(' + self.xField + ')' + ' AS ' + '"' + self.GetMidXColName() + '"' + ', ' + 'median(' + self.yField + ')' + ' AS ' + '"' + self.name + '"'

	def GenMinSelectStr(self):
		return 'SELECT' + ' ' + 'minerr(' + self.xField + ')' + ' AS ' + '"' + self.GetMinXColName() + '"' + ', ' + 'minerr(' + self.yField + ')' + ' AS ' + '"' + self.name + '"'

	def GenMaxSelectStr(self):
		return 'SELECT' + ' ' + 'maxerr(' + self.xField + ')' + ' AS ' + '"' + self.GetMaxXColName() + '"' + ', ' + 'maxerr(' + self.yField + ')' + ' AS ' + '"' + self.name + '"'

	def GetMidXY(self, sqlEngine):
		df = self.GetMidDataFromSql(sqlEngine)
		return { 'X' : df[df.columns[0]].tolist(), 'Y' : df[df.columns[1]].tolist()}

	def GetPlotyErrorXY(self, sqlEngine):
		minDF = self.GetMinDataFromSql(sqlEngine)
		maxDF = self.GetMaxDataFromSql(sqlEngine)

		return {
			'X' : {
				'type' :     'data',
				'symmetric' : False,
				'array' :      maxDF[maxDF.columns[0]].tolist(),
				'arrayminus' : minDF[minDF.columns[0]].tolist()
			},
			'Y' : {
				'type' :     'data',
				'symmetric' : False,
				'array' :      maxDF[maxDF.columns[1]].tolist(),
				'arrayminus' : minDF[minDF.columns[1]].tolist()
			}
		}

class SeriesLog(SeriesXy):

	def __init__(self, jsonObj, defaultSeries):
		super(SeriesLog, self).__init__(jsonObj, defaultSeries)

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
			elif self.type is GraphTypes.LOG:
				self.series.append(SeriesLog(item, self.defaultSeries))
			else:
				raise RuntimeError('Unsupported series type.')
		self.plotlyLayout = {
			'title'  : self.GetInGraphTitle(),
			'legend' : {'orientation' : 'h', 'y' : -0.30},
			'yaxis'  : {'gridcolor' : '#eee', 'title' : self.yLabel},
			'xaxis'  : {'gridcolor' : '#eee', 'title' : self.xLabel, 'type' : self.type.plotyType},
			'width'  : 600,
			'height' : 350,
			'margin' : {'l' : 0, 'r' : 0, 't' : 50, 'b' : 0},
			'plot_bgcolor' : '#fff'
		}
		if 'PlotlyLayout' in jsonObj:
			ConfigParser.RecursiveUpdateDict(self.plotlyLayout, jsonObj['PlotlyLayout'])

	def GetTitle(self):
		return self.xLabel + ' VS. ' + self.yLabel + ' (' + self.comment + ')'

	def GetInGraphTitle(self):
		return self.xLabel + ' VS. ' + self.yLabel + '<br>    (' + self.comment + ')'

	def GenImgFileName(self):
		return (self.xLabel.replace('/', '-per-') + ' VS ' + self.yLabel.replace('/', '-per-') + ' (' + self.comment + ')').replace(' ', '-')

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

	def Plot(self, sqlEngine, outDirPath):

		fig = go.Figure()
		fig.update_layout(self.plotlyLayout)

		for i in range(0, len(self.series)):
			fig.add_trace(self.series[i].GetScatter(sqlEngine=sqlEngine, idx=i))

		#fig.show()
		fig.write_image(os.path.join(outDirPath, self.GenImgFileName() + '.pdf'))
		fig.write_image(os.path.join(outDirPath, self.GenImgFileName() + '.png'))
		plotly.offline.plot(fig, auto_open=False, filename=os.path.join(outDirPath, self.GenImgFileName() + '.html'))

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
