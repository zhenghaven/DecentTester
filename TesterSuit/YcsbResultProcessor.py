import os
import sys
import argparse

# import submodules:
if __name__ == '__main__':
	from YcsbModules import ResProcConfigParser
	from YcsbModules import ProcRawData
else:
	from .YcsbModules import ResProcConfigParser
	from .YcsbModules import ProcRawData

def Process(configPath):

	cfg, absOutputDir = ResProcConfigParser.ParseConfig(configPath)

	print()
	print('************************************************')
	print('* ')
	print('* Phase 1 - Process RAW YCSB result data')
	print('* ')
	print('************************************************')
	print()

	p1Cfg = cfg['ProcRawResult']

	for resSetName, resSetDef in p1Cfg['ResultSet'].items():
		print('INFO:', 'Processing result set', resSetName, '...')
		ProcRawData.ProcRawData(resSetName, \
		                        [os.path.abspath(os.path.join(absOutputDir, resSetPath)) for resSetPath in resSetDef['Path']], \
		                        p1Cfg['IdSuffix'], resSetDef['IdDef'], absOutputDir, \
		                        p1Cfg['WarmupTime'], p1Cfg['TerminateTime'], p1Cfg['LatencyPercentile'], p1Cfg['IsFailOpsAllowed'], \
		                        p1Cfg['ColumnNames'], p1Cfg['ColumnTypes'])

	print()

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--config', required=True, type=str)

	args = parser.parse_args()

	Process(args.config)

if __name__ == '__main__':
	sys.exit(main())
