import io
import pandas as pd

def SaveOneParsedTable(destDict, label, srcIo):

	srcIo.seek(0)
	if label and srcIo.readline():
		if label in destDict:
			raise RuntimeError('The given operation label, ' + label + ', already exist!')
		# prev table not empty
		srcIo.seek(0)
		destDict[label] = pd.read_csv(srcIo)

def ParseYcsbCsv(csvFile, tsColName, isFailAllowed):

	line = csvFile.readline()
	csvDict = {}
	sepCsvIo = io.StringIO()
	tableOpStr = ''

	while line:
		if tsColName in line:
			# new table, save prev table
			SaveOneParsedTable(csvDict, tableOpStr, sepCsvIo)
			sepCsvIo.close()
			sepCsvIo = io.StringIO()
			# Set table operation label string
			tableOpStr = line.split()[0]
			#print('Found op:', tableOpStr)

		if (not isFailAllowed) and ('fail' in line.lower()):
			sepCsvIo.close()
			raise RuntimeError('Failed operation found in the data file.')

		sepCsvIo.write(line)

		line = csvFile.readline()

	SaveOneParsedTable(csvDict, tableOpStr, sepCsvIo)
	sepCsvIo.close()
	return csvDict

def ParseYcsbCsvFromPath(path, tsColName, isFailAllowed):

	file = open(path, 'r')
	res = ParseYcsbCsv(file, tsColName, isFailAllowed)
	file.close()

	return res

def MergeTableDict(dictA, dictB):

	if (dictA is None) or (len(dictA) is 0):
		return dictB
	elif (dictB is None) or (len(dictB) is 0):
		return dictA

	keySet = set(dictA).union(set(dictB))

	dictRes = {}

	for keyAB in keySet:
		#print('Checking key:', keyAB)
		if keyAB in dictA:
			if keyAB in dictB:
				# in A & B
				dictRes[keyAB] = pd.concat([dictA[keyAB], dictB[keyAB]]).reset_index(drop=True)
			else:
				# Only in A
				dictRes[keyAB] = dictA[keyAB]
		else:
			# Only in B
			dictRes[keyAB] = dictB[keyAB]

	return dictRes

def CombineTableInDict(d, opColName, opColIdx):

	res = None

	for key, val in d.items():
		colOriName = str(val.columns[opColIdx])
		val.rename(columns = {colOriName : opColName}, inplace=True)
		val.rename(columns=lambda x: x.strip(), inplace=True)
		res = pd.concat([res, val])

	res.sort_values(by=[val.columns[1]], inplace=True)
	res.reset_index(drop=True, inplace=True)
	return res

def GetPreProcedYcsbData(pathList, tsColName, opColName, opColIdx, isFailAllowed):

	mergedRes = None

	for path in pathList:
		mergedRes = MergeTableDict(mergedRes, ParseYcsbCsvFromPath(path, tsColName, isFailAllowed))

	return CombineTableInDict(mergedRes, opColName, opColIdx)

def GetPreProcedSvrStatData(pathList):

	return pd.read_csv(pathList[0])
