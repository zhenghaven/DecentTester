import progressbar as pbar
from python_utils.terminal import get_terminal_size

TERM_WIDTH = int(get_terminal_size()[0] * (2/3))

PBAR_WIDGETS = [
	pbar.Percentage(), ' (', pbar.SimpleProgress(), ') ',
	pbar.Bar(marker='█', left=' |', right='| ', fill='▁'),
	' ', pbar.Timer(),
	' | ETA ', pbar.ETA(), ' |'
]

PBAR_ARGS = {
	'widgets' : PBAR_WIDGETS,
	'term_width' : TERM_WIDTH
}