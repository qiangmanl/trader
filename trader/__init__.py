"""
"""

__version__  = "0.1.0"
import os
from trader import const
from trader.utils.tools import gen_random_id
from werkzeug.local import Local 
from trader.utils.config import Config
from trader.utils.logger import Logger

config = Config("config.json")

if config.log == None:
    logger = Logger()
else:
    logger = Logger(
        **config.log
    )
local   = Local()
local.project = config.project or "unknown"

def init_project()->bool:
    #从文件中获取symbol
    try:
        project_data_dir = f'{const.DATA_DIR}{os.sep}{local.node_domain}'
        project_data_dir_files = os.listdir(project_data_dir)
        if project_data_dir_files == []:
            raise Exception(f'{project_data_dir} is empty directory')
        for filename in project_data_dir_files:
            file_name_split = filename.split('.')
            symbol, tag, fmt = file_name_split
            if (len(file_name_split) == 3 and tag[0].isalpha() and fmt == "csv" )  == False:
                raise Exception(f'{filename} is not a suitable csv file')
            local.project_symbol_map[f'{tag}{symbol}'] = filename
            if not config.update_local_symbols:
                continue
            if local.symbol_domain_map.get(local.node_domain) == None:
                local.symbol_domain_map[local.node_domain] = []
            local.symbol_domain_map[local.node_domain].append(f'{tag}{symbol}')
    except Exception as e:
        logger.error(e.__repr__())
        exit()



if config.kind == "trader":
    node_id = local("node_id")
    if not config.node_id:
        local.node_id = gen_random_id()
        config.update(False,node_id=local.node_id)
    else:
        local.node_id = config.node_id
    if not config.node_domain:
        local.node_domain = "default"
        config.update(False,node_domain=local.node_domain) 
    else:
        local.node_domain = config.node_domain 

    local.domain_dir =  f'{const.DATA_DIR}{os.sep}{local.node_domain}'
    logger.debug(f" local.domain_dir:{local.domain_dir}")
    local.project_symbol_map = dict()
    #只有symbols上传到tasks的时候需要
    local.symbol_domain_map = dict()
    if not config.make_data:
        init_project()
elif config.kind == "amqp_server":
    pass

else:
    logger.error(f'unkonwn project kind: {config.kind}')




