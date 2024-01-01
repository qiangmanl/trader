"""
"""

__version__  = "0.1.0"

from trader.utils.tools import gen_random_id
from werkzeug.local import Local 
from trader.utils.config import Config

config = Config("config.json")
local   = Local()
node_id = local("node_id")
local.node_id = config.node_id or gen_random_id()
config.update(False,node_id=local.node_id)

local.node_domain = config.node_domain or "default"
config.update(False, node_id=local.node_id)
config.update(False, node_domain=local.node_domain)
if config.project == "trader":
    from trader.utils.logger import Logger
    local.symbol_file_map = dict()
    #只有symbols上传到tasks的时候需要
    local.symbol_domain_map = dict()
    local.historial_flows = None
    if config.log == None:
        logger = Logger()
    else:
        logger = Logger(
            **config.log
        )





