import builtins
import json


### CUSTOM PRINT METHOD
class pcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Overload print function with custom pretty-print
def cprint(*args, **kwargs):
	# Check if silent is set
	try:
		silent = kwargs.pop('silent')
	except:
		silent = False
	if not silent:
		if type(args[0]) is dict:
			return builtins.print(json.dumps(*args, **kwargs, indent = 4, sort_keys = True))
		else:
			try:
				args = list(args)
				if 'warning' in args[0].lower():
					args[0] = f'{pcolors.WARNING}{args[0]}{pcolors.ENDC}'
				elif 'error' in args[0].lower():
					args[0] = f'{pcolors.ERROR}{args[0]}{pcolors.ENDC}'
				elif 'fail' in args[0].lower():
					args[0] = f'{pcolors.ERROR}{args[0]}{pcolors.ENDC}'
				elif 'success' in args[0].lower():
					args[0] = f'{pcolors.OKGREEN}{args[0]}{pcolors.ENDC}'
				elif 'pass' in args[0].lower():
					args[0] = f'{pcolors.OKGREEN}{args[0]}{pcolors.ENDC}'
				elif 'main' in args[0].lower():
					args[0] = f'{pcolors.HEADER}{args[0]}{pcolors.ENDC}'
				elif 'skipping' in args[0].lower():
					args[0] = f'{pcolors.BOLD}{args[0]}{pcolors.ENDC}'
				args = tuple(args)
			except:
				pass
			return builtins.print(*args, **kwargs)
###
