"""
"""

__version__  = "0.1.0"
from datetime import datetime
import os
from trader import const
from trader.utils.tools import gen_random_id
from werkzeug.local import Local 
from trader.utils.config import Config
from trader.utils.logger import Logger

local   = Local()



try:
    config = Config("config.json")
    if config.log == None:
        logger = Logger()
    else:
        logger = Logger(
            **config.log
        )
    local.project = config.project or "unknown"

    if config.kind == "trader":
        node_id = local("node_id")
        if not config.node_id:
            local.node_id = gen_random_id()
            config.update(node_id=local.node_id)
        else:
            local.node_id = config.node_id
        if not config.node_domain:
            local.node_domain = "default"
            config.update(node_domain=local.node_domain) 
        else:
            local.node_domain = config.node_domain 

        local.domain_dir =  f'{const.DATA_DIR}{os.sep}{local.node_domain}'
        local.project_symbol_map = dict()
        #只有symbols上传到tasks的时候需要
        local.all_tasks_symbol = []
                # cache_id = datetime.now().strftime('%Y%m%d-%H%M%S')
        # local.latest_cache_dir = f'{const.DATA_DIR}{os.sep}{cache_id}'


        logger.debug(f" local.domain_dir:{local.domain_dir}")
        os.path.exists(local.domain_dir) == True or os.makedirs(local.domain_dir)
    elif config.kind == "amqp_server":
        pass

    else:
        logger.error(f'unkonwn project kind: {config.kind}')

except Exception:
    pass
