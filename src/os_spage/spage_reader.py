import StringIO

from os_rotatefile import open_file

from validator import simple_check_url

TAG_STORE_SIZE = 'Store-Size'


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
        self._inner_header = {}
        self._http_header = {}
        self._data = None
        self._read = self._read_inner_header
        self._url_latest = None

    def _generate(self):
        d = {}
        d['url'] = self._url
        d['inner_header'] = self._inner_header
        d['http_header'] = self._http_header
        d['data'] = self._data
        return d

    def _read_inner_header(self):
        line = self._fp.readline()
        if not line:
            raise StopIteration
        line = line.strip()
        line_length = len(line)
        if line_length <= 0 and self._inner_header:
            self._read = self._read_http_header
        elif line_length > 1024:
            pass
        elif simple_check_url(line):
            self._reset()
            self._url = line
        else:
            d = line.find(":")
            if d > 0:
                key = line[0:d].strip()
                value = line[d + 1:].strip()
                self._inner_header[key] = value
        return self._read()

    def _read_http_header(self):
        line = self._fp.readline()
        if not line:
            raise StopIteration
        if not line.strip():
            self._read = self._read_data
        elif simple_check_url(line):
            self._url_latest = line.strip()
            self._read = self._read_data
        else:
            d = line.find(":")
            if d > 0:
                key = line[0:d].strip()
                value = line[d + 1:].strip()
                self._http_header[key] = value

        return self._read()

    def _read_data(self):
        size = int(self._inner_header.get(TAG_STORE_SIZE, -1))
        if size < 0 or self._url_latest is not None:
            return self._generate()

        data = self._fp.read(size)
        if size > 0 and not data:
            raise StopIteration
        self._data = data
        return self._generate()

    def read(self):
        while True:
            yield self._read()
            self._reset()


class SpageReader(object):
    def __init__(self, base_filename):
        self._fp = open_file(base_filename, 'r')

    def close(self):
        self._fp.close()

    def read(self):
        for record in read(self._fp):
            yield record
