import os
import json
import psutil

SELECTED_PRIORITY_LEVELS = {
	'RealTime' : psutil.REALTIME_PRIORITY_CLASS,
	'AboveNormal' : psutil.ABOVE_NORMAL_PRIORITY_CLASS,
	'BelowNormal' : psutil.BELOW_NORMAL_PRIORITY_CLASS,
	'High' : psutil.HIGH_PRIORITY_CLASS,
	'Idle' : psutil.IDLE_PRIORITY_CLASS,
	'Normal' : psutil.NORMAL_PRIORITY_CLASS
}

def GetFullStrFromFile(filename):

	file = open(filename, 'r')
	res = file.read()
	file.close()
	return res

def ParseConfig(plainPath, cfgSuffix = 'ycsb.resproc.json'):

	absPath = os.path.abspath(plainPath)

	if not os.path.isfile(absPath):
		absPath = absPath + cfgSuffix
		if not os.path.isfile(absPath):
			raise RuntimeError('The config file doesn\'t exist (path=' + plainPath + ').')

	jsonObj = json.loads(GetFullStrFromFile(absPath))

	outDirPath, basename = os.path.split(absPath)

	return jsonObj, outDirPath
