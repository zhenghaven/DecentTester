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

def RecursiveUpdateDict(base, upt):

	if isinstance(base, dict) and isinstance(upt, dict):
		for k, v in upt.items():
			if k in base:
				#key is in base, update it
				if isinstance(v, dict):
					#v is a dict
					RecursiveUpdateDict(base[k], v)
				else:
					base[k] = v
			else:
				#key is not in base, create it
				base[k] = v
	elif base is None or (upt is not None and not isinstance(upt, dict)):
		raise RuntimeError('Invalid arguments')
