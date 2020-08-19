# coding=utf-8

import pandas as pd
import numpy as np
import math
from sklearn.preprocessing import StandardScaler
from enum import Enum
# from base.env.pre_process_setting import analysis
# from helper.util import get_attribute
from base import pre_process


class MLpipline(object):
    Running = 0
    Done = -1

    class Source(Enum):
        CSV = 'CSV'
        MONGODB = 'MongoDB'

    def __init__(self, cfg):
        # Initialize codes.
        self.cfg = cfg
        self.index_codes = []
        self.state_code = []
        # Initialize dates.
        self.dates = dict()
        self.t_dates = dict()
        self.e_dates = dict()
        # Initialize data frames.
        self.data_count = dict()
        self.origin_frames = dict()
        self.scaled_frames = dict()
        self.post_frames = dict()
        self.bound_index = dict()
        self.seq_data_x = dict()
        self.seq_data_y = dict()
        self.train_data_x = dict()
        self.train_data_y = dict()
        self.test_data_x = dict()
        self.test_data_y = dict()

        # Initialize scaled  data x, y.
        self.data_x = None
        self.data_y = None
        # Initialize scaled seq data x, y.
        self.seq_data_x = None
        self.seq_data_y = None
        # Initialize flag date.
        self.next_date = None
        self.iter_dates = None
        self.current_date = None
        # self.col_order = col_order
        # Initialize parameters.
        self._init_cfg(cfg)
        # Initialize stock data.
        self._init_data()


    def _init_cfg(self, cfg):
        if 'instList' in cfg['General']:
            self.state_code = pd.read_csv(cfg['General']['instList'])['instCode'].values
        else:
            self.state_code = None

        if 'use_sequence' in cfg['Setting']:
            self.use_sequence = eval(cfg['Setting']['use_sequence'])
        else:
            self.use_sequence = False

        if 'use_normalized' in cfg['Setting']:
            self.use_normalized = cfg['use_normalized']
        else:
            self.use_normalized = True

        if 'seq_length' in cfg['Parameter']:
            self.seq_length = eval(cfg['Parameter']['seq_length'])
        else:
            self.seq_length = 1

        if 'train_data_ratio' in cfg['Parameter']:
            self.train_data_ratio = eval(cfg['Parameter']['train_data_ratio'])
        else:
            self.train_data_ratio = 0.7
        # if 'scaler' in cfg['Setting']:
        #     self.scaler = cfg['Setting']['scaler']
        # else:
        #     self.scaler = StandardScaler()

    def _init_data(self):
        self._init_data_frames()
        self._init_env_data()
        # self._init_data_indices()

    # def _validate_codes(self):
    #     if not self.state_code_count:
    #         raise ValueError("Codes cannot be empty.")
    #     for code in self.state_codes:
    #         if not self.doc_class.exist_in_db(code):
    #             raise ValueError("Code: {} not exists in database.".format(code))

    # def _init_data_frames(self, start_date, end_date, source=Source.CSV.value):
    #     self.dates, self.scaled_frames, self.origin_frames, self.post_frames = \
    #         pre_process.ProcessStrategy(#action_fetch, action_pre_analyze, action_analyze, action_post_analyze,
    #                                     self.state_codes, start_date, end_date, self.scaler[0], self.pre_process_strategy, self.col_order).process()

    def _init_data_frames(self):
        self.dates, self.scaled_frames, self.origin_frames, self.post_frames = \
            pre_process.ProcessStrategy(self.cfg).process()


    def getScaledFrames(self, inst):
        return self.scaled_frames[inst]

    # def _init_env_data(self):
    #     if not self.use_sequence:
    #         self._init_series_data()
    #     else:
    #         self._init_sequence_data()


    def _init_env_data(self):
        self._init_sequence_data()


    def _init_sequence_data(self):
        for index, code in enumerate(self.state_code):
            # Calculate data count.
            self.data_count[code] = len(self.dates[code][: -1 - self.seq_length])
            # Calculate bound index.
            # self.bound_index = int(self.data_count[code] * self.train_data_ratio)
            label = self.cfg['Analyze']['label']
            scaled_frame = self.scaled_frames[code][:-1-self.seq_length]
            data_y = np.array(scaled_frame[label].values.reshape(len(scaled_frame[label]), 1, 1))
            data_x = []
            for date_index, date in enumerate(self.dates[code][: -1]):
                # Continue until valid date index.
                if date_index < self.seq_length:
                    continue
                # Get scaled frame by code.
                scaled_frame = self.scaled_frames[code]
                # Get instrument data x.
                # instruments_x = scaled_frame.drop([label], axis=1).iloc[date_index - self.seq_length: date_index]
                instruments_x = scaled_frame.iloc[date_index - self.seq_length: date_index]
                data_x.append(np.array(instruments_x))

            data_x = np.array(data_x)
            print (data_x.shape, data_y.shape)
            split_index = int(len(data_x) * self.train_data_ratio)
            self.train_data_x[code] = data_x[:split_index]
            self.train_data_y[code] = data_y[:split_index]
            self.test_data_x[code] = data_x[split_index:]
            self.test_data_y[code] = data_y[split_index:]
            # self.seq_data_x[code] = np.array(data_x)
            # self.seq_data_y[code] = np.array(data_y)


    def getTestTrainData(self):
        return self.train_data_x, self.train_data_y, self.test_data_x, self.test_data_y



    def _init_data_indices(self):
        # Calculate indices range.
        self.data_indices = np.arange(0, self.data_count)
        # Calculate train and eval indices.
        self.t_data_indices = self.data_indices[:self.bound_index]
        self.e_data_indices = self.data_indices[self.bound_index:]
        # Generate train and eval dates.
        self.t_dates = self.dates[:self.bound_index]
        self.e_dates = self.dates[self.bound_index:]

    def _origin_data(self, code, date):
        date_index = self.dates.index(date)
        return self.origin_frames[code].iloc[date_index]

    def _scaled_data_as_state(self, date):
        if not self.use_sequence:
            data = self.data_x[self.dates.index(date)]
            if self.mix_trader_state:
                trader_state = self.trader.scaled_data_as_state()
                data = np.insert(data, -1, trader_state).reshape((1, -1))
            return data
        else:
            return self.seq_data_x[self.dates.index(date)]


    @property
    def code_count(self):
        return len(self.codes)

    @property
    def index_code_count(self):
        return len(self.index_codes)

    @property
    def state_code_count(self):
        return len(self.state_codes)


    def getInputShape(self):
        return self.train_data_x[self.state_code[0]].shape[2]

    def getInstCode(self):
        return self.state_code


