import progressbar as pbar
from python_utils.terminal import get_terminal_size

TERM_WIDTH = int(get_terminal_size()[0])

CUSTOM_CHAR_LEN_MAP = {
	'█'  : 1,
}

PBAR_WIDGETS = [
	pbar.Percentage(), ' (', pbar.SimpleProgress(), ') ',
	pbar.Bar(marker='█', left=' |', right='| ', fill='_'),
	' ', pbar.Timer(),
	' | ETA ', pbar.ETA(), ' |'
]

def CustomCharLen(value):

	total = 0
	for c in value:
		total += CUSTOM_CHAR_LEN_MAP.get(c, 1)

	return total

PBAR_ARGS = {
	'widgets' : PBAR_WIDGETS,
	'term_width' : TERM_WIDTH,
	'len_func' : CustomCharLen
}