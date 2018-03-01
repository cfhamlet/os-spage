import copy
import StringIO
import time
import zlib
from datetime import datetime
from collections import OrderedDict

from os_rotatefile import open_file

from default_schema import META_SCHEMA
from validator import create_validator, TIME_FORMAT


class SpageWriter(object):
    def __init__(self, base_filename, roll_size='1G', compress=True, validator=None):
        self._fp = open_file(base_filename, 'w', roll_size=roll_size)
        self._compress = compress
        self._validator = create_validator(
            META_SCHEMA) if validator is None else validator

    def close(self):
        self._fp.close()

    def _http_header_str(self, http_header):
        return '\r\n'.join([': '.join((k, v)) for k, v in http_header.items()])

    def _inner_header_str(self, inner_header):
        o = StringIO.StringIO()
        for k in self._validator.schema['properties']['inner_header'].keys():
            if k in inner_header:
                v = inner_header[k]
                if v is None:
                    continue
                if isinstance(v, datetime):
                    v = v.strftime(TIME_FORMAT)
                o.write('\n'.join((str(k), str(v))))

        l = o.tell() - 1
        return o.read(l)

    def _compress_data(self, data):
        return zlib.compress(data)

    def _pre_process(self, record):
        inner_header = record['inner_header']
        store_size = original_size = len(
            record['data']) if record['data'] is not None else -1
        inner_header['Original-Size'] = original_size

        if original_size >= 0:
            data = record['data']
            if inner_header.get('Type', None) is None:
                if self._compress:
                    inner_header['Type'] = 'compressed'
                    data = self._compress_data(data)
                    store_size = len(data)
                else:
                    inner_header['Type'] = 'flat'

            record['data'] = data
            inner_header['Store-Size'] = store_size
        else:
            for i in ['Original-Size', 'Store-Size']:
                if i in inner_header:
                    inner_header.pop(i)
            if 'data' in record:
                record.pop('data')

        if record['http_header'] is None:
            record.pop('http_header')

        return record

    def _dumps(self, record):

        o = StringIO.StringIO()
        o.write(record['url'])
        o.write('\n')

        inner_header_str = self._inner_header_str(record['inner_header'])
        o.write(inner_header_str)
        o.write('\n\n')

        http_header = record.get('http_header', None)
        if http_header is None:
            o.write('\r\n')
        else:
            http_header_str = self._http_header_str(http_header)
            o.write(http_header_str)
            o.write('\r\n\r\n')

        data = record.get('data', None)
        if data is not None:
            o.write(data)
            o.write('\r\n')

        o.seek(0)
        return o.read()

    def write(self, url, inner_header, http_header=None, data=None, flush=False):
        record = {'url': url}
        record['inner_header'] = inner_header
        record['http_header'] = http_header
        record['data'] = data

        record = self._pre_process(record)
        self._validator.validate(record)

        store_data = self._dumps(record)
        self._fp.write(store_data, flush)
