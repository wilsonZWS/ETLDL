#!/usr/bin/python
# -*- coding: UTF-8 -*-

import csv
import datetime as dt
import importlib
import importlib.util
import json
import logging
import os
import traceback

import numpy as np

from utils import logger

def safe_round(value, digits):
    if value is not None:
        value = round(value, digits)
    return value


class LogTools:
    @staticmethod
    def setup_logger(logger_name, log_file, fmt=None, level=logging.INFO):
        l = logging.getLogger(logger_name)
        if not l.handlers:
            if fmt is None:
                fmt = '[%(levelname)s][%(asctime)s]\n[%(funcName)s] %(message)s'
            formatter = logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S")
            fileHandler = logging.FileHandler(log_file, mode='a')
            # fileHandler = TimedRotatingFileHandler(log_file, when='midnight')
            fileHandler.setFormatter(formatter)
            l.setLevel(level)
            l.addHandler(fileHandler)
        return l, l.handlers


class BHTLib_Aux:
    @staticmethod
    def strToClass(name, path):
        try:
            module = importlib.import_module(path)
            return getattr(module, name)
        except ImportError as e:
            traceback.print_exc()
            print(e)

    @staticmethod
    def load_from_location(clazzName, modulePath, moduleName):
        try:
            spec = importlib.util.spec_from_file_location(moduleName, modulePath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, clazzName)
        except ImportError as e:
            traceback.print_exc()
            print(e)

    @staticmethod
    def sharpe(r):
        riskFree = 0.02
        std = np.std(r)
        if std == 0:
            return 1
        return (np.mean(r) - riskFree) / std

    @staticmethod
    def mdd(timeseries):
        # 回撤结束时间点
        i = np.argmax(np.maximum.accumulate(timeseries) - timeseries)
        if i == 0:
            return 0
        # 回撤开始的时间点
        j = np.argmax(timeseries[:i])
        return (timeseries[i] / timeseries[j]) - 1


class BHTMath_Aux:
    @staticmethod
    def safe_min(left, right):
        if left is None:
            return right
        elif right is None:
            return left
        else:
            return min(left, right)

    @staticmethod
    def safe_max(left, right):
        if left is None:
            return right
        elif right is None:
            return left
        else:
            return max(left, right)

    @staticmethod
    def safeDiv(a, b):
        return a / b if b != 0 else 0

    @staticmethod
    def safeFloat(s):
        return float(s) if s is not None else 0

    @staticmethod
    def safeInt(s):
        return int(s) if s is not None else 0


class CSVUtils:
    def __init__(self):
        pass

    @staticmethod
    def parseStr(line, delimiter=','):
        return line.split(delimiter)

    @staticmethod
    def write(file_dir, file_name, line, delimiter=','):
        file_path = file_dir + file_name
        try:
            if isinstance(line, str):
                line = CSVUtils.parseStr(line)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as csv_file:
                    writer = csv.writer(csv_file, delimiter=delimiter)
                    writer.writerow(line)
            else:
                with open(file_path, 'a') as csv_file:
                    writer = csv.writer(csv_file, delimiter=delimiter)
                    writer.writerow(line)
            # print("Write a CSV file to path %s Successful." % file_path)
        except Exception as e:
            print("Write an CSV file to path error: %s, Case: %s" % (file_path, e))
            traceback.print_exc()

    @staticmethod
    def write_dict(file_dir, file_name, dict_data, header):
        file_path = file_dir + file_name
        try:
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as csv_file:
                    writer = csv.DictWriter(csv_file, header)
                    writer.writeheader()
                    writer.writerow(dict_data)
            else:
                with open(file_path, 'a') as csv_file:
                    writer = csv.DictWriter(csv_file, header)
                    writer.writerow(dict_data)
            # print("Write a CSV file to path %s Successful." % file_path)
        except Exception as e:
            print("Write an CSV file to path error: %s, Case: %s" % (file_path, e))
            traceback.print_exc()

    @staticmethod
    def write_lines(file_dir, file_name, lines, delimiter=','):
        for line in lines:
            CSVUtils.write(file_dir, file_name, line, delimiter)

    @staticmethod
    def backup(file_dir, file_name, backup_dir, backup_name):
        file_path = file_dir + file_name
        backup_path = backup_dir + backup_name
        try:
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            with open(file_path, 'rb') as fin, open(backup_path, 'wb') as fout:
                csv_in = csv.DictReader(fin, skipinitialspace=True)
                csv_out = csv.DictWriter(fout, csv_in.fieldnames)
            for row in csv_in:
                csv_out.writerow(row)
        except Exception as e:
            print("backup an CSV file to path error: %s, Case: %s" % (backup_dir, e))
            traceback.print_exc()

    @staticmethod
    def delete_file(file_dir, file_name):
        file_path = file_dir + file_name
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("CSV file in path: %s does not exist" % file_path)

    # data must be dict, something like: update_data = {"id": [1,2,3]}
    @staticmethod
    def update(path, data):
        try:
            to_update = {k: iter(v) for k, v in data.items()}
            with open(path, 'rb') as fin, open(path, 'wb') as fout:
                csv_in = csv.DictReader(fin, skipinitialspace=True)
                csv_out = csv.DictWriter(fout, csv_in.fieldnames)
            for row in csv_in:
                # Update rows - if we have something left and it's in the update dictionary,
                # use that value, otherwise we use the value that's already in the column.
                row.update({k: next(to_update[k], row[k]) for k in row if k in to_update})
                csv_out.writerow(row)
        except Exception as e:
            print("update an CSV file to path error: %s, Case: %s" % (path, e))
            traceback.print_exc()

    @staticmethod
    def delete(path, ticker):
        try:
            with open(path, 'rb') as fin, open(path, 'wb') as fout:
                csv_in = csv.DictReader(fin, skipinitialspace=True)
                csv_out = csv.DictWriter(fout, csv_in.fieldnames)
                rows = (tuple(item for idx, item in enumerate(row) if idx != ticker) for row in csv_in)
                csv_out.writerows(rows)
        except Exception as e:
            print("delete an CSV file to path error: %s, Case: %s" % (path, e))
            traceback.print_exc()

class JSONUtils:

    def __init__(self):
        pass

    @staticmethod
    def read(self, file_dir, file_name):
        log = logger.getLogger()
        file_path = file_dir + file_name
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    meta = json.loads(f.read())
                    self.__dict__ = meta
                log.debug('loading %s' % file_path)
                return True
            else:
                log.debug('No {} file founded. Creating new one.'.format(file_name))
                JSONUtils.write(self, file_dir, file_name)
                return False
        except Exception as e:
            traceback.print_exc()
            print("read an JSON file to path error: %s, Case: %s" % (file_path, e))
            return False

    @staticmethod
    def json_default(value):
        if isinstance(value, dt.date):
            return dict(year=value.year, month=value.month, day=value.day)
        else:
            return value.__dict__

    @staticmethod
    def write(self, file_dir, file_name):
        file_path = file_dir + file_name
        try:
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            with open(file_path, "w") as f:
                json.dump(self, f, default=JSONUtils.json_default, indent=4)
            return True
        except Exception as e:
            traceback.print_exc()
            print("save an JSON file to path error: %s, Case: %s" % (file_path, e))
            return False
