import datetime
import traceback

import six


def get_datetime_from_nano(dt_in_nano):
    if not isinstance(dt_in_nano, int):
        return None
    if len(str(dt_in_nano)) != 19:
        return None
    dt_in_nano = datetime.datetime.fromtimestamp(dt_in_nano / 1000 / 1000 / 1000)
    return dt_in_nano


def get_change_percentage(actual, prev):
    if actual is None or prev is None or prev == 0:
        raise Exception("Invalid values")

    diff = actual - prev
    ret = diff / float(abs(prev))
    return ret


def safe_min(left, right):
    if left is None:
        return right
    elif right is None:
        return left
    else:
        return min(left, right)


def safe_max(left, right):
    if left is None:
        return right
    elif right is None:
        return left
    else:
        return max(left, right)


def time_delta_with_rate(time_base, interval, unit, rate=1):
    delta = eval('datetime.timedelta(' + unit + '={})'.format(int(interval * rate)))
    return time_base + delta


def time_delta(time_base, interval, unit):
    return time_delta_with_rate(time_base, interval, unit)


def init_trading_session(session_list, log):
    ret = {}
    try:
        for session in session_list:
            session_parts = session.split('-')
            if len(session_parts) == 2:
                ret[session_parts[0]] = session_parts[1]
            else:
                log.error('error session %s' % session)
        return ret
    except Exception as e:
        log.error(e)
        traceback.print_exc()
        return ret


def is_in_trading_session(dt, session_dict, log, delay=None, unit='seconds', current=False):
    if session_dict == {}:
        return True
    if datetime.datetime.now().date() != dt.date() and current:
        log.warning("%s is other day data." % (dt.strftime('%Y-%m-%d %H:%M:%S')))
        return False
    tick_time = dt.strftime("%H:%M:%S")
    for start, end in six.iteritems(session_dict):
        if delay is not None:
            start_dt = datetime.datetime.strptime(start, "%H:%M:%S")
            start = time_delta(start_dt, delay, unit).time().strftime("%H:%M:%S")
        if start <= tick_time <= end:
            return True
    log.debug("%s is not in trading session." % (dt.strftime('%Y-%m-%d %H:%M:%S')))
    return False


def is_in_trading_date(db_service, exch_id, log):
    try:
        if db_service.is_trading_day(exch_id):
            log.debug(
                "%s: %s is trading day." % (exch_id, datetime.datetime.now().strftime('%Y-%m-%d')))
            return True
        else:
            log.debug(
                "%s: %s is not trading day." % (exch_id, datetime.datetime.now().strftime('%Y-%m-%d')))
            return False
    except Exception as e:
        log.error(e)
        traceback.print_exc()
