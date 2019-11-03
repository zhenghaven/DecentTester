import os
import json

def GetFullStrFromFile(filename):

	file = open(filename, 'r')
	res = file.read()
	file.close()
	return res

def ParseConfig(plainPath, cfgSuffix = '.resproc.json'):

	absPath = os.path.abspath(plainPath)

	if not os.path.isfile(absPath):
		absPath = absPath + cfgSuffix
		if not os.path.isfile(absPath):
			raise RuntimeError('The config file doesn\'t exist (path=' + plainPath + ').')

	jsonObj = json.loads(GetFullStrFromFile(absPath))

	outDirPath, basename = os.path.split(absPath)

	return jsonObj, outDirPath
