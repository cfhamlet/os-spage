import abc
import copy
import time
import zlib
from collections import OrderedDict
from datetime import datetime
from io import BytesIO

from os_rotatefile import open_file

from .common import DEFAULT_ENCODING, TIME_FORMAT
from .compat import StringIO, iteritems
from .default_schema import InnerHeaderKeys as I_KEYS
from .default_schema import RecordTypes as R_TYPES
from .default_schema import SpageKeys as S_KEYS
from .default_schema import META_SCHEMA
from .validator import create_validator


class RecordProcessor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process(self, record, **kwargs):
        return record


class SpageRecordProcessor(RecordProcessor):
    def __init__(self, validator, compress=True):
        self._validator = validator
        self._compress = compress

    def _compress_data(self, data):
        return zlib.compress(data)

    def process(self, record, **kwargs):
        if not record[S_KEYS.HTTP_HEADER]:
            record.pop(S_KEYS.HTTP_HEADER)
        inner_header = record[S_KEYS.INNER_HEADER]
        store_size = original_size = len(
            record[S_KEYS.DATA]) if record[S_KEYS.DATA] is not None else -1

        if original_size >= 0:
            data = record[S_KEYS.DATA]
            r_type = inner_header.get(I_KEYS.TYPE, None)
            if r_type is None:
                if I_KEYS.ORIGINAL_SIZE in inner_header:
                    raise ValueError(
                        'do not specify %s without Type' % I_KEYS.ORIGINAL_SIZE)
                inner_header[I_KEYS.ORIGINAL_SIZE] = original_size
                if self._compress:
                    inner_header[I_KEYS.TYPE] = R_TYPES.COMPRESSED
                    data = self._compress_data(data)
                    store_size = len(data)
                else:
                    inner_header[I_KEYS.TYPE] = R_TYPES.FLAT
            elif r_type == R_TYPES.COMPRESSED or r_type == R_TYPES.DELETED:
                if I_KEYS.ORIGINAL_SIZE not in inner_header:
                    raise ValueError('inner_header require %s' %
                                     I_KEYS.ORIGINAL_SIZE)
            elif r_type == R_TYPES.FLAT:
                inner_header[I_KEYS.ORIGINAL_SIZE] = original_size

            record[S_KEYS.DATA] = data
            inner_header[I_KEYS.STORE_SIZE] = store_size
        else:
            if I_KEYS.TYPE not in inner_header:
                inner_header[I_KEYS.TYPE] = R_TYPES.FLAT
            for i in (I_KEYS.ORIGINAL_SIZE, I_KEYS.STORE_SIZE):
                if i in inner_header:
                    inner_header.pop(i)
            record.pop(S_KEYS.DATA)

        self._validator.validate(record)
        return record


class RecordEncoder(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def dumps(self, record, **kwargs):
        raise NotImplementedError


class SpageRecordEncoder(RecordEncoder):

    def __init__(self, allowed_inner_header_keys=None):
        self._inner_header_keys = allowed_inner_header_keys

    def _http_header_str(self, http_header):
        if not http_header:
            return None
        return '\r\n'.join([': '.join((k.strip(), v.strip()))
                            for k, v in iteritems(http_header)])

    def _inner_header_str(self, inner_header):
        o = StringIO()
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
        o = BytesIO()
        o.write(record[S_KEYS.URL].encode(DEFAULT_ENCODING))
        o.write(b'\n')

        inner_header_str = self._inner_header_str(record[S_KEYS.INNER_HEADER])
        o.write(inner_header_str.encode(DEFAULT_ENCODING))
        o.write(b'\n\n')

        http_header_str = self._http_header_str(
            record.get(S_KEYS.HTTP_HEADER, None))
        if not http_header_str:
            o.write(b'\r\n')
        else:
            o.write(http_header_str.encode(DEFAULT_ENCODING))
            o.write(b'\r\n\r\n')

        data = record.get(S_KEYS.DATA, None)
        if data is not None:
            o.write(data)
            o.write(b'\r\n')

        o.seek(0)
        return o.read()


class RecordWriter(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def write(self, f, url, inner_header=None, http_header=None, data=None):
        raise NotImplementedError


class SpageRecordWriter(RecordWriter):
    def __init__(self, processor, encoder):
        self._processor = processor
        self._encoder = encoder

    def write(self, f, url, inner_header=None, http_header=None, data=None):
        if not isinstance(data, (bytes, type(None))):
            raise ValueError(
                "bytes-like data is required, not {}".format(type(data).__name__))
        record = {}
        record[S_KEYS.URL] = url
        record[S_KEYS.INNER_HEADER] = {} if inner_header is None else copy.deepcopy(
            inner_header)
        record[S_KEYS.HTTP_HEADER] = {} if http_header is None else copy.deepcopy(
            http_header)
        record[S_KEYS.DATA] = data

        record = self._processor.process(record)
        f.write(self._encoder.dumps(record))


def create_writer(**kwargs):
    validator = kwargs.get('validator', None)
    validator = create_validator(
        META_SCHEMA) if validator is None else validator
    processor = SpageRecordProcessor(validator, kwargs.get('compress', True))
    allowed_keys = validator.schema['properties'][S_KEYS.INNER_HEADER]['properties'].keys(
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
