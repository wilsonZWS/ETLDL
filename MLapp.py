#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import datetime as dt
import configobj

class MLApplication(object):
    def __init__(self, config):
        # Strategy Instance initialization
        self._config = configobj.ConfigObj(config, interpolation=False)
        strategyId = self._config['General']['strategyId']
        self.__logger.info()

        # Initialize logging.
        # self.__logger = logger.getLogger(Strategy.LOGGER_NAME)

