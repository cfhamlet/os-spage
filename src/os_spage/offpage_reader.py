from os_rotatefile import open_file

from .common import COLON, DEFAULT_ENCODING
from .validator import simple_check_url

_CONTENT_TYPE = 'Content-Type'
_ORIGINAL_SIZE = 'Original-Size'

_SERIES = (_CONTENT_TYPE, _ORIGINAL_SIZE)


def read(fp):
    reader = Reader(fp)
    for record in reader.read():
        yield record


class Reader(object):
    def __init__(self, fp):
        self._fp = fp
        self._url_latest = None
        self._reset()

    def _reset(self):
        self._url = self._url_latest
        self._header = {}
        self._data = {}
        self._read = self._read_header
        self._url_latest = None

    def _generate(self):
        d = {}
        d[u'url'] = self._url
        d[u'header'] = self._header
        d[u'data'] = self._data
        return d

    def _read_header(self):
        line = self._fp.readline()
        if not line:
            raise StopIteration
        try:
            line = line.decode(DEFAULT_ENCODING).strip()
        except Exception as e:
            return self._read()
        line_length = len(line)
        if line_length <= 0 and self._header:
            self._read = self._read_data
        elif line_length > 1024:
            pass
        elif simple_check_url(line):
            self._reset()
            self._url = line
        else:
            d = line.find(COLON)
            if d > 0:
                key = line[0:d].strip()
                value = line[d + 1:].strip()
                if key in _SERIES:
                    value = self._split_series(value)
                self._header[key] = value
        return self._read()

    def _split_series(self, series):
        s = [tuple(i.split(',')) for i in series.split(';') if ',' in i]
        return s

    def _read_data(self):
        data = {}
        for key, size in self._header[_CONTENT_TYPE]:
            size = int(size)
            if size < 0 or self._url_latest is not None:
                return self._generate()
            d = self._fp.read(size)
            if size > 0 and not d:
                raise StopIteration
            data[key] = d

        self._data = data
        return self._generate()

    def read(self):
        while True:
            yield self._read()
            self._reset()


class OffpageReader(object):
    def __init__(self, base_filename):
        self._fp = open_file(base_filename, 'r')

    def close(self):
        self._fp.close()

    def read(self):
        for record in read(self._fp):
            yield record
