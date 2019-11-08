
ID_COMPONENT_CACL_FUNC = { \
	'i+' : lambda lst : sum([int(x) for x in lst]) \
	}

def TrimOffByTimeRange(dataF, tsColName, timeRange):

	dataF.sort_values(by=[tsColName], inplace=True)
	dataF.reset_index(drop=True, inplace=True)

	recCount = dataF.shape[0]

	startIdx = 0
	endIdx = recCount

	for ts in dataF[tsColName]:
		if ts < timeRange[0]:
			startIdx = startIdx + 1
		else:
			break

	for ts in reversed(dataF[tsColName]):
		if ts > timeRange[1]:
			endIdx = endIdx - 1
		else:
			break

	return dataF[startIdx:endIdx].reset_index(drop=True)

def GetTimestampRange(dataF, tsColName):

	dataF.sort_values(by=[tsColName], inplace=True)
	dataF.reset_index(drop=True, inplace=True)

	recCount = dataF.shape[0]

	if recCount == 0:
		return [0, 0]

	starttime = dataF[tsColName][0]
	endtime = dataF[tsColName][recCount - 1]

	return [starttime, endtime]

def GetIdResult(idPair, idDef):

	idComponentsList = [['999999999999' if w == '-1' else w for w in id.split('_')] for id in idPair]

	return [idComponentsList[0][i] if idDef[i] is None else \
	            ID_COMPONENT_CACL_FUNC[idDef[i][1]]([idComponents[i] for idComponents in idComponentsList]) \
	                for i in range(0, len(idDef))]

def GetYcsbDataResult(df, timeRange, percentile, tsColName, latColName):

	df = TrimOffByTimeRange(df, tsColName, timeRange)

	trimedTimeRange = GetTimestampRange(df, tsColName)

	totalOps = df.shape[0]
	timeElapsedMs = trimedTimeRange[1] - trimedTimeRange[0] #In millisecond
	timeElapsedS = timeElapsedMs / 1000 # In sec
	throughtput = totalOps / timeElapsedS
	perLat = df[latColName].quantile(q=(percentile / 100.0), interpolation='higher')
	avgLat = df[latColName].mean()

	return [totalOps, timeElapsedMs, throughtput, perLat, avgLat]

def GetSvrStatDataResult(df, timeRange, tsColName, overallColName, nodeOverallColName, sysOverallColName):

	df = TrimOffByTimeRange(df, tsColName, timeRange)

	avgs = df.drop([tsColName], axis=1).mean(axis=0)

	return [avgs[overallColName], avgs[nodeOverallColName], avgs[sysOverallColName], avgs.drop([overallColName, nodeOverallColName, sysOverallColName]).mean()]
