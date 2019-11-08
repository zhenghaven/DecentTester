import os
import sys
import argparse

# import submodules:
if __name__ == '__main__':
	from YcsbModules import ConfigParser
	from YcsbModules import ProcRawData
	from YcsbModules import GenTableAndPlotFromResult
else:
	from .YcsbModules import ConfigParser
	from .YcsbModules import ProcRawData
	from .YcsbModules import GenTableAndPlotFromResult

def ProcessPhase1(p1Cfg, absOutputDir):

	print()

	print('************************************************')
	print('* ')
	print('* Phase 1 - Process RAW YCSB result data')
	print('* ')
	print('************************************************')
	print()

	processorList = []

	for resSetName, resSetDef in p1Cfg['ResultSet'].items():
		print('INFO:', 'Setting up processor for result set', resSetName, '...')
		processorList.append(ProcRawData.RawDataProcessor(resSetName, \
		                        [os.path.abspath(os.path.join(absOutputDir, resSetPath)) for resSetPath in resSetDef['Path']], \
		                        p1Cfg['IdSuffix'], resSetDef['IdDef'], absOutputDir, \
		                        p1Cfg['WarmupTime'], p1Cfg['TerminateTime'], p1Cfg['LatencyPercentile'], p1Cfg['IsFailOpsAllowed'], \
		                        p1Cfg['ColumnNames'], p1Cfg['ColumnTypes']))

	for processor in processorList:
		print('INFO:', 'Running processor for result set', processor.resSetName, '...')
		processor.Process()
		print()
		processor.SaveResult()

	print()

def ProcessPhase2(p2Cfg, absOutputDir):

	print()

	print('************************************************')
	print('* ')
	print('* Phase 2 - Select Data and Draw Graphs')
	print('* ')
	print('************************************************')
	print()

	GenTableAndPlotFromResult.SelectDataAndDrawGraphs(absOutputDir, p2Cfg)

PROCESS_PHASE_FUNCTIONS =  \
	[ \
		lambda p1Cfg, absOutputDir : ProcessPhase1(p1Cfg, absOutputDir), \
		lambda p2Cfg, absOutputDir : ProcessPhase2(p2Cfg, absOutputDir) \
	]

PROCESS_PHASE_CONFIG_KEY =  \
	[ \
		'ProcRawResult', \
		'PickDataAndDrawGraph' \
	]

DEFAULT_MIN_PHASE_IDX = 0
DEFAULT_MAX_PHASE_IDX = len(PROCESS_PHASE_FUNCTIONS)

def Process(configPath, minPhaseIdx):

	if not (DEFAULT_MIN_PHASE_IDX <= minPhaseIdx and minPhaseIdx < DEFAULT_MAX_PHASE_IDX):
		raise RuntimeError('Given start phase out of range.')

	cfg, absOutputDir = ConfigParser.ParseConfig(configPath)

	for phaseIdx in range(minPhaseIdx, DEFAULT_MAX_PHASE_IDX):
		pxCfg = cfg[PROCESS_PHASE_CONFIG_KEY[phaseIdx]]
		PROCESS_PHASE_FUNCTIONS[phaseIdx](pxCfg, absOutputDir)

def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--config', required=True, type=str)
	parser.add_argument('--startPhase', required=False, type=int, default=(DEFAULT_MIN_PHASE_IDX + 1))

	args = parser.parse_args()

	Process(args.config, args.startPhase - 1)

if __name__ == '__main__':
	sys.exit(main())
