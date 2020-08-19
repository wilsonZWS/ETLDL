import csv
import logging

import six
from six.moves import xrange
import requests


logging.getLogger("requests").setLevel(logging.ERROR)


# A faster (but limited) version of csv.DictReader
class FastDictReader(object):
    def __init__(self, f, fieldnames=None, dialect="excel", *args, **kwargs):
        self.__fieldNames = fieldnames
        self.reader = csv.reader(f, dialect, *args, **kwargs)
        if self.__fieldNames is None:
            self.__fieldNames = six.next(self.reader)
        self.__dict = {}

    def _next_impl(self):
        # Skip empty rows.
        row = six.next(self.reader)
        while row == []:
            row = six.next(self.reader)

        # Check that the row has the right number of columns.
        assert len(self.__fieldNames) == len(row), "Expected columns: %s. Actual columns: %s" % (
            self.__fieldNames, list(row.keys())
        )

        # Copy the row values into the dict.
        for i in xrange(len(self.__fieldNames)):
            self.__dict[self.__fieldNames[i]] = row[i]

        return self.__dict

    def __iter__(self):
        return self

    def __next__(self):
        return self._next_impl()

    def next(self):
        return self._next_impl()


def download_csv(url, url_params=None, content_type="text/csv"):
    response = requests.get(url, params=url_params)

    response.raise_for_status()
    response_content_type = response.headers['content-type']
    if response_content_type != content_type:
        raise Exception("Invalid content-type: %s" % response_content_type)

    ret = response.text

    # Remove the BOM
    while not ret[0].isalnum():
        ret = ret[1:]

    return ret


def float_or_string(value):
    try:
        ret = float(value)
    except Exception:
        ret = value
    return ret