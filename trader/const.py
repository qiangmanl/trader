import os
SEP = '_'
# $HOME/.trader
HOME_DIR = os.environ["HOME"] or os.environ["HOMEPATH"]
DATA_DIR = f'{HOME_DIR}{os.sep}.trader'
