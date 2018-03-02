import copy
import StringIO
import time
import zlib
from collections import OrderedDict
from datetime import datetime

from os_rotatefile import open_file

from default_schema import META_SCHEMA
from validator import TIME_FORMAT, create_validator


class RecordProcessor(object):
    def process(self, record, **kwargs):
        return record


class SpageRecordProcessor(RecordProcessor):
    def __init__(self, validator, compress=True):
        self._validator = validator
        self._compress = compress

    def _compress_data(self, data):
        return zlib.compress(data)

    def process(self, record, **kwargs):
        if not record['http_header']:
            record.pop('http_header')
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
            record.pop('data')

        self._validator.validate(record)
        return record


class RecordEncoder(object):
    def dumps(self, record, **kwargs):
        raise NotImplementedError


class SpageRecordEncoder(RecordEncoder):

    def __init__(self, allowed_inner_header_keys=None):
        self._inner_header_keys = allowed_inner_header_keys

    def _http_header_str(self, http_header):
        if not http_header:
            return None
        return '\r\n'.join([': '.join((k.strip(), v.strip())) for k, v in http_header.items()])

    def _inner_header_str(self, inner_header):
        o = StringIO.StringIO()
        keys = self._inner_header_keys if self._inner_header_keys \
            else inner_header.keys()
        for k in keys:
            if k in inner_header:
                v = inner_header[k]
                if v is None:
                    continue
                if isinstance(v, datetime):
                    v = v.strftime(TIME_FORMAT)
                o.write(': '.join((str(k).strip(), str(v).strip())))
                o.write('\n')

        data_length = o.tell() - 1
        o.seek(0)
        return o.read(data_length)

    def dumps(self, record, **kwargs):
        o = StringIO.StringIO()
        o.write(record['url'])
        o.write('\n')

        inner_header_str = self._inner_header_str(record['inner_header'])
        o.write(inner_header_str)
        o.write('\n\n')

        http_header_str = self._http_header_str(
            record.get('http_header', None))
        if not http_header_str:
            o.write('\r\n')
        else:
            o.write(http_header_str)
            o.write('\r\n\r\n')

        data = record.get("data", None)
        if data is not None:
            o.write(data)
            o.write('\r\n')

        o.seek(0)
        return o.read()


class RecordWriter(object):
    def write(self, f, url, inner_header=None, http_header=None, data=None):
        raise NotImplementedError


class SpageRecordWriter(RecordWriter):
    def __init__(self, processor, encoder):
        self._processor = processor
        self._encoder = encoder

    def write(self, f, url, inner_header=None, http_header=None, data=None):
        record = {}
        record["url"] = url
        record["inner_header"] = {} if inner_header is None else copy.deepcopy(
            inner_header)
        record["http_header"] = {} if http_header is None else copy.deepcopy(
            http_header)
        record["data"] = data

        record = self._processor.process(record)
        f.write(self._encoder.dumps(record))


def create_writer(**kwargs):
    validator = kwargs.get('validator', None)
    if validator is None:
        validator = create_validator(
            META_SCHEMA) if validator is None else validator
    processor = SpageRecordProcessor(validator, kwargs.get('compress', True))
    allowed_keys = validator.schema['properties']['inner_header']['properties'].keys(
    )
    encoder = SpageRecordEncoder(allowed_keys)
    return SpageRecordWriter(processor, encoder)


class SpageWriter(object):
    def __init__(self, base_filename, roll_size='1G', compress=True, validator=None):
        self._fp = open_file(base_filename, 'w', roll_size=roll_size)
        self._record_writer = create_writer(
            validator=validator, compress=compress)

    def close(self):
        self._fp.close()

    def write(self, url, inner_header=None, http_header=None, data=None, flush=False):
        self._record_writer.write(
            self._fp, url,
            inner_header=inner_header,
            http_header=http_header,
            data=data)

        if flush:
            self._fp.flush()


write = create_writer().write
