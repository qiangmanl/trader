import os
import json

from trader.utils.base import DictBase

class ConfigBase(DictBase):
    def __init__(self):
        self.configures = {}



class Config(ConfigBase):

    def __init__(self, config_file="config.json"):
        """ Load config file.

        Args:
            config_file: config json file.
        """

        
        self.config_file = '{}{}{}'.format(os.path.abspath(""),os.sep,config_file)
        if config_file:
            try:
                with open(config_file) as f:
                    data = f.read()
                    #如果为空  data 为空str
                    if data:
                        self.configures = json.loads(data)
            except Exception as e:
                print(e)
                exit(0)
            if not self.configures:
                print("config json file error!")
                exit(0)


        self._update_file_config(self.configures)

    # def __getattr__(self, name):
    #     return {}
        
        

    def _update_file_config(self, update_fields):
        """ Update config attributes.

        Args:
            update_fields: Update fields.
        """
        for k, v in update_fields.items():
            self.__setattr__(k, v)

    def update(self, temporary=True , **kwargs):
        """
        Usage:
            config.update(False,x=11)
        """
        for k,v in kwargs.items():
            self.__setattr__(k , v)
            if temporary == False:
                self.configures[k] = v
                self.dump(inplace=True)

    def dump(self,inplace:bool=False):
        if inplace:
            config_file = self.config_file
        else:
            config_file = f'{self.config_file}.new'
        with open(config_file, 'w') as j_f:
            json.dump(self.configures, j_f, indent=4)

