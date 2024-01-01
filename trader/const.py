import os
SEP = '_'
# $HOME/.trader
HOME_DIR = os.environ["HOME"] or os.environ["HOMEPATH"]
DATA_DIR = f'{HOME_DIR}{os.sep}.trader'  or f'{HOME_DIR}{os.sep}.trader' 
# $HOME/.trader/row
ROW_DATA_DIR = f'{DATA_DIR}{os.sep}row'
ADMIN_NODE_ID = "yBhR7ZEmXXWYThv0zN"