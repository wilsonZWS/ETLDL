import inspect
import configobj
import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod
from helper.util import catch_exception
from helper.util import get_attribute
from helper.util import get_logger
import sklearn.preprocessing as preprocessing
import talib


LOGGER = get_logger(__name__)


class Action(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def fire(self, data_frame, col_order):
        raise NotImplementedError


class Fetch(Action):

    @staticmethod
    @abstractmethod
    def fire(self, data_frame=None, col_order=None):
        raise NotImplementedError


class PreAnalyze(Action):

    @staticmethod
    @abstractmethod
    def fire(self, origin_frame, col_order=None):
        print('this is pre analyze')
        # raise NotImplementedError


class Analyze(Action):
    @staticmethod
    @abstractmethod
    def fire(self, pre_frame, label):
        for state_code in self._state_codes:
            analyze_frames = IndicatorAnalysis(pre_frame[state_code], self._indicators, label).add_analysis()
            self._analyze_frames[state_code] = analyze_frames

class PostAnalyze(Action):
    @staticmethod
    @abstractmethod
    def fire(self, data_frame, col_order=None):
        raise NotImplementedError
        # print("this is PostAnalyze")
        # for state_code in self._state_codes:
        #     self._analyze_frames[state_code].to_csv("../../back_testing/data/{}.csv".format(state_code))


class FetchCSVConfig(Fetch):
    @staticmethod
    def fire(self):
        source_root = self.cfg['General']['source']
        if self._state_codes is None:
            raise TypeError("you should add correct inst_list")

        for state_code in self._state_codes:
            file_path = source_root + state_code + ".csv"
            try:
                df_ori = pd.read_csv(file_path)
            except Exception:
                print (state_code, "the source file has error path")
                continue
            mask = (df_ori.date > self._start_date) & (df_ori.date <= self._end_date)
            self._origin_frames[state_code] = df_ori.loc[mask]
            self._dates[state_code] = self._origin_frames[state_code]['date']
            self._origin_frames[state_code].set_index('date', inplace=True)


class PreAnalyzeDefault(PreAnalyze):
    @staticmethod
    def fire(self, origin_frames, col_order=None):
        self._pre_frames = origin_frames

class PostAnalyzeDefault(PostAnalyze):
    ### single csv data
    @staticmethod
    def fire(self, analyze_frames, col_order=None):
        # print("this is PostAnalyzeDefault")
        scales = self._scaler
        for state_code in self._state_codes:
            post_frame = analyze_frames[state_code].copy()
            scales.fit(post_frame)
            post_frame = scales.transform(post_frame)
            self._post_frames[state_code] = pd.DataFrame(data=post_frame, index=self._dates[state_code],
                                                         columns=analyze_frames[state_code].columns)
            self._origin_frames[state_code] = self._origin_frames[state_code].dropna(axis=0)
            self._post_frames[state_code] = self._post_frames[state_code].dropna(axis=0)
            self._dates[state_code] = list(self._post_frames[state_code].index)


def fetchcfg(cfg):
    # config = configobj.ConfigObj(cfg, encoding='UTF8')
    module = cfg['General']['module']
    fetch = cfg['PreProcess']['fetch']
    pre_analyze = cfg['PreProcess']['pre_analyze']
    post_analyze = cfg['PreProcess']['post_analyze']
    label = cfg['Analyze']['label']
    indicators = cfg['Analyze']['indicators']
    if label is None:
        label = 'close'
    action_fetch = get_attribute('.'.join([module, fetch]))
    action_pre_analyze = get_attribute('.'.join([module, pre_analyze]))
    action_post_analyze = get_attribute('.'.join([module, post_analyze]))
    return action_fetch, action_pre_analyze, indicators, action_post_analyze, label


class ProcessStrategy(object):
    def __init__(self,  cfg):
        self.cfg = cfg
        self._fetch, self._pre_analyze, self._indicators, self._post_analyze, self._label = fetchcfg(self.cfg)
        self._analyze = Analyze # the analyze function in this module
        if 'instList' in cfg['General']:
            self._state_codes = list(pd.read_csv(cfg['General']['instList'])['instCode'])
        else:
            self._state_codes = None

        if 'start_date' in cfg['Parameter']:
            self._start_date = cfg['Parameter']['start_date']
        else:
            self._start_date = '2007-01-01'

        if 'end_date' in cfg['Parameter']:
            self._end_date = cfg['Parameter']['end_date']
        else:
            self._end_date = '2020-07-30'
        # self._end_date = end_date
        # self._indicators = action_analyze
        if 'scaler' in cfg['Setting']:
            self._scaler = getattr(preprocessing, cfg['Setting']['scaler'])()
        else:
            self._scaler = preprocessing.StandardScaler()

        # self._scaler = scaler
        self._dates = dict()
        self._origin_frames = dict()
        self._pre_frames = dict()
        self._analyze_frames = dict()   # with analysis added
        self._post_frames = dict()
        self._col_order = cfg['Analyze']['indicators']
        # self._scaled_frames = dict()

    @classmethod
    def get_instance(cls, data_source, state_codes, start_date, end_date, indicators, scaler, **kwargs):
        cls = get_attribute(inspect.getmodule(cls).__name__ + '.Process' + data_source)
        return cls(data_source, state_codes, start_date, end_date, indicators, scaler, **kwargs)

    def process(self):
        self._fetch.fire(self)
        self._pre_analyze.fire(self, self._origin_frames)
        self._analyze.fire(self, self._pre_frames, self._label)
        self._post_analyze.fire(self, self._analyze_frames, self._col_order)
        return self._dates, self._post_frames, self._origin_frames, self._post_frames


class IndicatorAnalysis:
    def __init__(self, origin_frame, indicators, label):
        self._origin_frame = origin_frame
        self._indicators = indicators
        self._index = origin_frame.index.values
        self._label = label

    # def rsi(self, *args):
    #     para = args[0]
    #     result = talib.RSI(self._origin_frame[para[0]], int(para[1]))
    #     return pd.DataFrame(result, columns=['rsi_{}'.format(para[1])])
    #
    # def macd(self, *args):
    #     para = args[0]
    #     result = talib.MACD(self._origin_frame[para[0]], int(para[1]), int(para[2]), int(para[3]))
    #     return pd.DataFrame(result[0], columns=['macd'])

    # def stoch(self, *args):
    #     # df_indicators = pd.DataFrame()
    #
    #     para = args[0]
    #     result = talib.STOCH(self._origin_frame['high'], self._origin_frame['low'], self._origin_frame[para[0]],
    #                          fastk_period=int(para[1]), slowk_period=int(para[2]), slowd_period=int(para[3]))
    #
    #     for idx, res in enumerate(result):
    #         if idx == 0:
    #             df_result = pd.DataFrame(res, columns=['stoch' + str(idx)])
    #         else:
    #             df_result = df_result.join(pd.DataFrame(res, columns=['stoch' + '_' + str(idx)]))
    #
    #     return df_result


    def trend(self, *args):
        """  If closing price value leads its MA 15 and MA 15 is rising for last 5 days then trend is Uptrend
        i.e. trend signal is 1.

        If closing price value lags its MA 15 and MA 15 is falling for last 5 days then trend is Downtrend
        i.e. trend signal is 0.

        For up trend:
        Tr_i = [(cp_i - min cp)/(max cp - min cp)] * 0.5 + 0.5

        For down trend:
        Tr_i = [(cp_i - min cp)/(max cp - min cp)] * 0.5

        min cp = min(cp_i, cp_i+1, cp_i+2)
        max cp = max(cp_i, cp_i+1, cp_i+2)

        """

        TREND_DOWN = -1
        TREND_NO = 0
        TREND_UP = 1

        def determine_trend_ma(targets, trend_bars_idx, current_val):
            # determine the trend based on the move average.
            # e.x. if the target falling in last 5(trend_bars_idx) days and current value lower than mv, trend is down
            latest_trend = None
            for idx in range(trend_bars_idx):

                # if trend_bars_idx - idx - 2 == 0:break

                # if the current target is larger than the previous one
                if targets[trend_bars_idx - idx] >= targets[trend_bars_idx - idx - 1]:
                    trend = TREND_UP
                    if latest_trend == TREND_DOWN:
                        return TREND_NO
                    latest_trend = trend
                if targets[trend_bars_idx - idx] < targets[trend_bars_idx - idx - 1]:
                    trend = TREND_DOWN
                    if latest_trend == TREND_UP:
                        return TREND_NO
                    latest_trend = trend

            if trend == TREND_UP and current_val < targets[trend_bars_idx]:
                return TREND_NO
            elif trend == TREND_DOWN and current_val > targets[trend_bars_idx]:
                return TREND_NO

            return trend

        def calculate_up_trend(current_val, target_future_bars):
            if max(target_future_bars) == min(target_future_bars):
                breakpoint()
            return (1-((current_val - min(target_future_bars)) / (max(target_future_bars) - min(target_future_bars)))) * 0.5 + 0.5
            # return ((current_val - min(target_future_bars)) / (max(target_future_bars) - min(target_future_bars))) * 0.5 + 0.5

        def calculate_down_trend(current_val, target_future_bars):
            return (1-((current_val - min(target_future_bars)) / (max(target_future_bars) - min(target_future_bars)))) * 0.5
            # return ((current_val - min(target_future_bars)) / (max(target_future_bars) - min(target_future_bars))) * 0.5

        # we calculate the trend
        target = args[0]
        result = target.copy()

        ma_bars = int(args[1])
        trend_bars = int(args[2])
        future_bars = int(args[3])

        # get moving average
        ma = talib.MA(target, timeperiod=ma_bars)

        last_trend = None
        for curr_idx, val in enumerate(target):
            result[curr_idx] = None
            if curr_idx >= ma_bars + trend_bars-1 and curr_idx < (len(target)-future_bars):
                target_trend_bars = ma[curr_idx-trend_bars: curr_idx+1]

                # determine the trend based on the move average.
                # e.x. if falling in last 5 days, trend is down
                ma_trend = determine_trend_ma(target_trend_bars, trend_bars, val)

                # if trend is down and price is lower than the ma we calculate trend with down formula
                if ma_trend == TREND_DOWN:
                    last_trend = TREND_DOWN
                    result[curr_idx] = calculate_down_trend(val, target[curr_idx: curr_idx+future_bars])

                # if trend is up and price is higher than the ma we calculate trend with up formula
                elif ma_trend == TREND_UP:
                    last_trend = TREND_UP
                    result[curr_idx] = calculate_up_trend(val, target[curr_idx: curr_idx+future_bars])
                elif ma_trend == TREND_NO:
                    # if have no trend, we get the last trend and calculate the trend
                    if last_trend == TREND_DOWN:
                        result[curr_idx] = calculate_down_trend(val, target[curr_idx: curr_idx + future_bars])
                    elif last_trend == TREND_UP:
                        result[curr_idx] = calculate_up_trend(val, target[curr_idx: curr_idx + future_bars])

        # return pd.DataFrame(result).rename(columns={'close': 'trend_{}'.format(args[1:4])})
        # self._label = 'trend_{}'.format("_".join([str(v) for v in args[1:4]]))
        return pd.DataFrame(data=result, index=self._index.flatten(), columns=[self._label])


    def trend_backward(self, *args):
        """  If closing price value leads its MA 15 and MA 15 is rising for last 5 days then trend is Uptrend
        i.e. trend signal is 1.

        If closing price value lags its MA 15 and MA 15 is falling for last 5 days then trend is Downtrend
        i.e. trend signal is 0.

        For up trend:
        Tr_i = [(cp_i - min cp)/(max cp - min cp)] * 0.5 + 0.5

        For down trend:
        Tr_i = [(cp_i - min cp)/(max cp - min cp)] * 0.5

        min cp = min(cp_i, cp_i-1, cp_i-2)
        max cp = max(cp_i, cp_i-1, cp_i-2)

        """

        TREND_DOWN = -1
        TREND_NO = 0
        TREND_UP = 1

        def determine_trend_ma(targets, trend_bars_idx, current_val):
            # determine the trend based on the move average.
            # e.x. if the target falling in last 5(trend_bars_idx) days and current value lower than mv, trend is down
            latest_trend = None
            for idx in range(trend_bars_idx):

                # if trend_bars_idx - idx - 2 == 0:break

                # if the current target is larger than the previous one
                if targets[trend_bars_idx - idx] >= targets[trend_bars_idx - idx - 1]:
                    trend = TREND_UP
                    if latest_trend == TREND_DOWN:
                        return TREND_NO
                    latest_trend = trend
                if targets[trend_bars_idx - idx] < targets[trend_bars_idx - idx - 1]:
                    trend = TREND_DOWN
                    if latest_trend == TREND_UP:
                        return TREND_NO
                    latest_trend = trend

            if trend == TREND_UP and current_val < targets[trend_bars_idx]:
                return TREND_NO
            elif trend == TREND_DOWN and current_val > targets[trend_bars_idx]:
                return TREND_NO
            return trend

        def calculate_up_trend(current_val, target_past_bars):
            # if max(target_past_bars) == min(target_past_bars):
            #     breakpoint()
            # return (1 - ((current_val - min(target_past_bars)) / (max(target_past_bars) - min(target_past_bars)))) * 0.5 + 0.5
            return ((current_val - min(target_past_bars)) / (max(target_past_bars) - min(target_past_bars))) * 0.5 + 0.5

        def calculate_down_trend(current_val, target_past_bars):
            # return (1 - ((current_val - min(target_past_bars)) / (max(target_past_bars) - min(target_past_bars)))) * 0.5
            return ((current_val - min(target_past_bars)) / (max(target_past_bars) - min(target_past_bars))) * 0.5

        # we calculate the trend
        target = args[0]
        result = target.copy()

        ma_bars = int(args[1])
        trend_bars = int(args[2])
        past_bars = int(args[3])
        input_col = args[4]

        # get moving average
        ma = talib.MA(target, timeperiod=ma_bars)

        last_trend = None
        for curr_idx, val in enumerate(target):
            result[curr_idx] = None
            if curr_idx >= ma_bars + trend_bars-1 and curr_idx >= past_bars:
                target_trend_bars = ma[curr_idx-trend_bars: curr_idx+1]

                # determine the trend based on the move average.
                # e.x. if falling in last 5 days, trend is down
                ma_trend = determine_trend_ma(target_trend_bars, trend_bars, val)

                # if trend is down and price is lower than the ma we calculate trend with down formula
                if ma_trend == TREND_DOWN:
                    last_trend = TREND_DOWN
                    result[curr_idx] = calculate_down_trend(val, target[curr_idx-past_bars+1: curr_idx+1])

                # if trend is up and price is higher than the ma we calculate trend with up formula
                elif ma_trend == TREND_UP:
                    last_trend = TREND_UP
                    result[curr_idx] = calculate_up_trend(val, target[curr_idx-past_bars+1: curr_idx+1])
                elif ma_trend == TREND_NO:
                    # if have no trend, we get the last trend and calculate the trend
                    if last_trend == TREND_DOWN:
                        result[curr_idx] = calculate_down_trend(val, target[curr_idx-past_bars+1: curr_idx+1])
                    elif last_trend == TREND_UP:
                        result[curr_idx] = calculate_up_trend(val, target[curr_idx-past_bars+1: curr_idx+1])

        # return pd.DataFrame(result).rename(columns={'close': 'trend_{}'.format(args[1:4])})
        # self._label = 'trend_{}'.format("_".join([str(v) for v in args[1:4]]))
        # return pd.DataFrame(data=result, index=self._index.flatten(), columns=[self._label])
        args_str = "_".join([str(v) for v in args[1:4]])
        return pd.DataFrame(data=result, index=self._index.flatten(), columns=["trend_backward|{}|{}".format(input_col[0], args_str)])

    # Fourier transformation
    def fft(self, *args):
        target = args[0]
        input_col = args[-1][0]
        # args_str = ["FTT{}Comps".format(x) for x in args[1:]]
        result = target.copy()
        fft_list = np.fft.fft(result)
        df_all = pd.DataFrame(index=self._index.flatten())
        for num_ in args[1:-1]:
            col_name_str = "FFT{}|{}Comps".format(input_col, num_)
            fft_list_temp = np.copy(fft_list)
            fft_list_temp[num_:-num_] = 0
            fft_list_temp = np.abs(np.fft.ifft(fft_list_temp))
            df_all[col_name_str] = fft_list_temp
        return df_all


     #input (p_d_q)
     #p: periods taken for auto-regressive model
     #d: Intergrated order, difference
    #q: moving average, periods in moving average model
    def arima(self, *args):
        from statsmodels.tsa.arima_model import ARIMA
        target = args[0]
        p = args[1]
        d = args[2]
        q = args[3]
        input_col = args[-1][0]
        train = target[:11]
        test = target[11:]
        history = [x for x in train]
        predictions = list()
        for t in range(len(test)):
            try:
                model = ARIMA(history, order=(p, d, q))
                model_fit = model.fit(disp=0)
                output = model_fit.forecast()
                yhat = output[0]
            except Exception:
                yhat = np.nan
            predictions.append(yhat)
            obs = test[t]
            history.append(obs)
        predictions = [np.nan] * 11 + predictions
        print(predictions)
        args_str = "_".join([str(v) for v in args[1:4]])
        return pd.DataFrame(data=predictions, index=self._index.flatten(),
                            columns=["arima|{}|{}".format(input_col, args_str)])

    @catch_exception(LOGGER)
    def analyze(self):
        df_indicators = pd.DataFrame()
        # instance = self.get_instance()
        for indicator in self._indicators:
            indicator = indicator.lower()
            meta_info = indicator.split('|')
            # if len(meta_info) == 4 and meta_info[3] == "label":
            #     self._label = "_".join([meta_info[0],meta_info[2]])
            method_name = meta_info[0]
            input_col = meta_info[1].split('_')
            # method_name = meta_info[0]
            # del meta_info[0]
            # input_col = [val for val in paras if val.startswith(input_selector)]
            # remove the columns, only arguments remained
            # args = list((arg for arg in paras if not any(col == arg for col in input_col)))
            args = []
            if len(meta_info) == 3:
                args = meta_info[2].split('_')
                args = list(map(int, args))  # convert from string to int

            # input_col_final = [col.replace(input_selector, '') for col in input_col]
            input = self._origin_frame[input_col].transpose().values

            method = getattr(self, method_name, None)
            if method is not None:

                result = method(*input, *args, input_col)

                if df_indicators.empty:
                    df_indicators = result if result is not None else df_indicators
                else:
                    df_indicators = df_indicators.join(result) if result is not None else df_indicators

            else:
                # try to get the method from talib
                method = get_attribute('.'.join(['talib', method_name.upper()]))
                # # get input columns
                # input_col = [val for val in meta_info if val.startswith(source_selector)]
                #
                # # remove the columns, only arguments remained
                # args = list((arg for arg in meta_info if not any(col == arg for col in input_col)))
                # args = list(map(int, args))  # convert from string to int
                # input_col_final = [col.replace(source_selector, '') for col in input_col]
                # input = self._origin_frame[input_col_final].transpose().values
                result = method(*input, *args)
                args_str = "_".join([str(v) for v in args])
                # if isinstance(result, pd.core.series.Series):
                if not isinstance(result, tuple):
                    df_result = pd.DataFrame(data=result, index=self._index.flatten(), columns=["{}|{}|{}".format(method_name, input_col[0], args_str)])
                else:
                    for idx, res in enumerate(result):
                        if idx == 0:
                            df_result = pd.DataFrame(data=res, index=self._index.flatten(),
                                                     columns=["{}_{}_{}".format(method_name,args_str, str(idx))])
                        else:
                            df_result = df_result.join(pd.DataFrame(data=res, index=self._index.flatten(),
                                                                columns=["{}_{}_{}".format(method_name,args_str, str(idx))]))
                    # df_result = pd.DataFrame(result[0], columns=[method_name])
                if df_indicators.empty:
                    df_indicators = df_result
                else:
                    df_indicators = df_indicators.join(df_result)

                df_result = None  # clean the data frame

        return df_indicators

    def add_analysis(self):
        return self._origin_frame.join(self.analyze())

    def get_instance(self):
        """ initialize a instance """
        ds_cls = get_attribute(
            inspect.__package__ + inspect.getmodulename(__file__) + '.{}'.format(self.__class__.__name__))
        return ds_cls

