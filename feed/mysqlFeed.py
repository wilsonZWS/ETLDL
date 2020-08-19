from typing import Tuple

import pymysql
from datetime import *
import traceback
from queue import Queue
import configobj
from constantl import *
import pandas as pd
import six
import abc


@six.add_metaclass(abc.ABCMeta)
class DBService:
    __instance = dict()

    def __init__(self, path=DIR_DEFAULT_CFG, dbFile='Database'):

        dbFilePath = path + dbFile + SUFFIX_CFG
        self._db_config = configobj.ConfigObj(dbFilePath, interpolation=False)
        self._db_host = self._db_config["Database"]['host']
        self._db_port = int(self._db_config["Database"]['port'])
        self._db_username = self._db_config["Database"]['username']
        self._db_password = self._db_config["Database"]['password']
        self._db_instance = self._db_config["Database"]['instance']
        self._db_encoding = self._db_config["Database"]['encoding']
        self._db_max_conn = int(self._db_config["Database"]['maxConn'])
        self._pool = Queue(self._db_max_conn)

        self.init()

    def __del__(self):
        class_name = self.__class__.__name__

    def init(self):
        try:
            for i in range(self._db_max_conn):
                conn = pymysql.connect(host=self._db_host,
                                       port=self._db_port,
                                       user=self._db_username,
                                       password=self._db_password,
                                       db=self._db_instance,
                                       charset=self._db_encoding)
                conn.autocommit(True)
                self._pool.put(conn)
        except Exception as e:
            traceback.print_exc()
            # self._runtime_log.error("DB Connection Error! Create DB Connection Pool Failed! msg=%s", e)
            raise IOError(e)

    @staticmethod
    def get_instance(cls, *args, **kwargs):
        if len(args) == 0:
            tag = "Database"
        else:
            tag = args[0]
        if tag in cls.__instance and cls.__instance[tag]:
            return cls.__instance[tag]
        else:
            cls.__instance[tag] = DBService(*args, **kwargs)
            return cls.__instance[tag]

    # execute sql without return
    def exec_sql(self, sql, operation=None):
        cursor = None
        conn = None
        try:
            conn = self._pool.get()
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            response = cursor.execute(sql, operation) if operation else cursor.execute(sql)
        except Exception as e:
            print(e)
            traceback.print_exc()
            # self._runtime_log.error("Execute sql: %s Failed! msg=%s", sql, e)
            cursor.close()
            self._pool.put(conn)
            return None
        else:
            cursor.close()
            self._pool.put(conn)
            return response


    # execute sql and fetch
    def exec_sql_fetch(self, sql, operation=None):
        cursor = None
        conn = None
        try:
            conn = self._pool.get()
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            response = cursor.execute(sql, operation) if operation else cursor.execute(sql)
        except Exception as e:
            print(e)
            traceback.print_exc()
            # self._runtime_log.error("Execute sql: %s Failed! msg=%s", sql, e)
            cursor.close()
            self._pool.put(conn)
            return None, None
        else:
            data = cursor.fetchall()
            cursor.close()
            self._pool.put(conn)
            return data

    # batch execute sql and fetch
    def exec_sql_batch(self, sql, operation=None):
        cursor = None
        conn = None
        try:
            conn = self._pool.get()
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            response = cursor.execute(sql, operation) if operation else cursor.execute(sql)
        except Exception as e:
            print(e)
            traceback.print_exc()
            # self._runtime_log.error("Execute sql: %s Failed! msg=%s", sql, e)
            cursor.close()
            self._pool.put(conn)
        else:
            cursor.close()
            self._pool.put(conn)
            return response

    def close_conn(self):
        for i in range(self._db_max_conn):
            self._pool.get().close()

    @staticmethod
    def rs2dict(rs, fields, isList=False):
        if not isList:
            ret = dict()
            if len(rs) == 0:
                return None
            elif len(rs) > 1:
                print("multiple records found!")
                return None
            else:
                row = rs[0]
                if isinstance(row, dict):
                    return row
                assert len(row) == len(fields), "result doesn't match fields!"
                for f, r in zip(fields, row):
                    ret.update({f: r})
            return ret
        else:
            ret = []
            for row in rs:
                positionRecord = dict()
                assert len(row) == len(fields), "result doesn't match fields!"
                for f, r in zip(fields, row):
                    positionRecord.update({f: r})
                ret.append(positionRecord)
            return ret

    @staticmethod
    def fields2str(fields):
        if isinstance(fields, str):
            print("String is given while expected a list!")
            return fields
        return ','.join(fields)

    def read_table(self, table, fields, conditions="1"):
        sql = "SELECT " + fields + " FROM " + self._db_instance + "." + table + " WHERE " + conditions
        return self.exec_sql_fetch(sql)

    ### add by wilson, new pandas read sql function
    def readOHLCpd(self, inst, table="dailydata", startdate='2020-01-01', enddate='2020-01-31', frame=1440, DSource='DS000001'):
        sql = "SELECT instCode,date,open,high,low,close FROM " + self._db_instance + "." + table + " WHERE instCode = '" + str(inst) \
              +"' and frame =" + str(frame) + " and date < '" + enddate + "' and date >'" + startdate + "' and dataSrcId = '" + DSource + "'"
        return pd.read_sql(sql, self._pool.get())

    def insert_table(self, sql, values):
        self.exec_sql_batch(sql, values)

    def update_table(self, table, fields, values, conditions='1'):
        assert len(fields) == len(values), "length of fields and values not match!"
        sql = "UPDATE %s.%s SET %s WHERE %s" % (
            self._db_instance, table, ",".join(["%s = \'%s\'" % (f, v) for f, v in zip(fields, values)]), conditions)
        self.exec_sql_batch(sql)

    def insert_frame_data(self, table, values):
        fields = self.fields2str(FRAME_DATA_FIELDS)
        sql = "INSERT IGNORE INTO " + table + " (" + fields + ")" \
              + " VALUES (" + ",".join(['%s'] * len(FRAME_DATA_FIELDS)) + ")"
        assert len(FRAME_DATA_FIELDS) == len(values), "number of values not equal to number of fields"
        self.insert_table(sql, values)

    def insert_contract_info(self, table, entity):
        ori_fields = CONTRACT_INFO_FIELDS
        fields = self.fields2str(ori_fields)
        values = (
            entity.contract, entity.code, entity.symbol, entity.description, entity.changeLimit, entity.targetMargin,
            entity.deliveryMonth, entity.issueDate, entity.lastTradeDate, entity.lastDeliveryDate)
        sql = "REPLACE INTO " + table + " (" + fields + ")" \
              + " VALUES (" + ",".join(['%s'] * len(ori_fields)) + ")"
        assert len(ori_fields) == len(values), "number of values not equal to number of fields"
        self.insert_table(sql, values)

    def merge_frame_data(self, table, values):
        fields = self.fields2str(FRAME_DATA_FIELDS)
        sql = "REPLACE INTO " + table + " (" + fields + ")" \
              + " VALUES (" + ",".join(['%s'] * len(FRAME_DATA_FIELDS)) + ")"
        assert len(FRAME_DATA_FIELDS) == len(values), "number of values not equal to number of fields"
        self.insert_table(sql, values)

    def merge_frame_data_batch(self, table, values):
        fields = self.__db_service.fields2str(FRAME_DATA_FIELDS)
        sql = "REPLACE INTO " + table + " (" + fields + ")" \
              + " VALUES (" + ",".join(['%s'] * len(FRAME_DATA_FIELDS)) + ")"
        self.__db_service.insert_table_batch(sql, values)

    def insert_sector_data(self, table, values):
        fields = self.fields2str(SECTOR_DATA_FIELDS)
        sql = "INSERT IGNORE INTO " + table + " (" + fields + ")" \
              + " VALUES (" + ",".join(['%s'] * len(SECTOR_DATA_FIELDS)) + ")"
        assert len(SECTOR_DATA_FIELDS) == len(values), "number of values not equal to number of fields"
        self.insert_table(sql, values)

    def remove_sector_by_code(self, table, sector):
        conditions = 'sectorCode = "' + sector + '"'
        sql = "DELETE FROM " + self._db_instance + "." + table + " WHERE " + conditions
        return self.exec_sql(sql)

    def save_tick(self, tick):
        sql = "REPLACE INTO tickData (instCode,datetime,open,high,low,close,volume,amount,vwap,ccyId,timestamp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        value = [tick.instCode, tick.datetime, tick.open, tick.high, tick.low, tick.close, tick.volume, tick.amount,
                 tick.vwap, tick.ccyId, tick.timestamp]
        value_tuple = tuple(value)
        self.insert_table(sql, value_tuple)

    def get_inst_list_by_index_list(self, index_set):
        table = 'indexweight'
        fields = 'distinct(instCode)'
        index_code_list = '('
        for index_code in index_set:
            index_code_list += '"' + index_code
            if index_code == index_set[-1]:
                index_code_list += '")'
            else:
                index_code_list += '",'
        index_conditions = 'indexCode in ' + index_code_list
        result = self.read_table(table, fields, conditions=index_conditions)
        test = map(int, {1: 2, 2: 3, 3: 4})
        inst_list = []
        for item in result:
            inst_list.append(item["instCode"])
        return inst_list

    def heart_beat(self, venue):
        self.update_venue_status(venue, VENUE_STATUS_UP)

    def shut_down_venue(self, venue):
        self.update_venue_status(venue, VENUE_STATUS_DOWN)

    def update_venue_status(self, venue, status):
        table = TABLE_VENUE
        fields = self.fields2str(VENUE_FIELDS)
        values = (venue.venueId, venue.venueName, venue.venueGatewayAddress, status, venue.ccyId)
        sql = "REPLACE INTO " + table + " (" + fields + ")" \
              + " VALUES (" + ",".join(['%s'] * len(VENUE_FIELDS)) + ")"
        assert len(VENUE_FIELDS) == len(values), "number of values not equal to number of fields"
        self.insert_table(sql, values)

    def is_trading_day(self, exch_id):
        today = date.today().strftime('%Y-%m-%d')
        todayStr = today + ' 00:00:00'
        table = 'calendar'
        fields = 'tradingDate'
        calendar_condition = 'tradingDate = "%s" and exchId = "%s"' % (todayStr, exch_id)
        result = self.read_table(table, fields, conditions=calendar_condition)
        if len(result) > 0:
            return True
        else:
            return False

    def is_delivery_day(self, inst):
        today = date.today().strftime('%Y-%m-%d')
        todayStr = today + ' 00:00:00'
        table = TABLE_CONTRACT_INFO
        fields = 'lastDeliveryDate'
        condition = 'lastDeliveryDate = "%s" and symbol = "%s"' % (todayStr, inst)
        result = self.read_table(table, fields, conditions=condition)
        if len(result) > 0:
            return True
        else:
            return False

    def get_next_contract(self, inst, gap=1):
        today = date.today().strftime('%Y-%m-%d')
        todayStr = today + ' 00:00:00'
        table = TABLE_CONTRACT_INFO
        fields = 'contract, lastDeliveryDate'
        condition = 'lastDeliveryDate > "%s" and symbol = "%s" order by contract asc limit %d' % (
            todayStr, inst, gap)
        result = self.read_table(table, fields, conditions=condition)
        if len(result) > 0:
            return result[-1]['contract'], result[-1]['lastDeliveryDate']
        else:
            return None

    def roll_contract(self, inst, contract):
        table = TABLE_PRODUCT
        fields = ["contract"]
        values = [contract]
        conditions = "instCode='{instCode}'".format(instCode=inst)
        self.update_table(table, fields, values, conditions=conditions)

    def save_trading_date(self, table, exchId, date):
        ori_fields = CALENDAR_FIELDS
        fields = self.fields2str(ori_fields)
        if exchId == '':
            exchId = 'SSH'
        values = (exchId, date, 'DS00001')
        sql = "REPLACE INTO " + table + " (" + fields + ")" \
              + " VALUES (" + ",".join(['%s'] * len(ori_fields)) + ")"
        assert len(ori_fields) == len(values), "number of values not equal to number of fields"
        self.insert_table(sql, values)

    def merge_netbuyvol_data(self, table, values):
        fields = self.fields2str(NET_BUY_VOL_DATA_FIELDS)
        sql = "REPLACE INTO " + table + " (" + fields + ")" \
              + " VALUES (" + ",".join(['%s'] * len(NET_BUY_VOL_DATA_FIELDS)) + ")"
        assert len(NET_BUY_VOL_DATA_FIELDS) == len(values), "number of values not equal to number of fields"
        self.insert_table(sql, values)

    def merge_mfd_netbuyvol_data(self, table, values):
        fields = self.fields2str(MFD_NET_BUY_VOL_M_DATA_FIELDS)
        sql = "REPLACE INTO " + table + " (" + fields + ")" \
              + " VALUES (" + ",".join(['%s'] * len(MFD_NET_BUY_VOL_M_DATA_FIELDS)) + ")"
        assert len(MFD_NET_BUY_VOL_M_DATA_FIELDS) == len(values), "number of values not equal to number of fields"
        self.insert_table(sql, values)

    def merge_suspendedDate_data(self, table, values):
        fields = self.fields2str(SUSPENDED_DATA_FIELDS)
        print (fields)
        print (values)
        sql = "REPLACE INTO " + table + " (" + fields + ")" \
              + " VALUES (" + ",".join(['%s'] * len(SUSPENDED_DATA_FIELDS)) + ")"
        assert len(SUSPENDED_DATA_FIELDS) == len(values), "number of values not equal to number of fields"
        self.insert_table(sql, values)