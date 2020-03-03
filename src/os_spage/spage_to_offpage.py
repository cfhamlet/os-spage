import zlib

from os_rotatefile import open_file

from .compat import BytesIO
from .validator import simple_check_url


def read(fp):
    reader = Reader(fp)
    for record in reader.read():
        yield record


class Reader(object):
    def __init__(self, fp):
        self._fp = fp
        self._url_latest = None
        self._store_size = 0
        self._reset()

    def _reset(self):
        self._url = self._url_latest
        self._store_size = 0
        self._inner_header = BytesIO()
        self._data = BytesIO()
        self._read = self._read_inner_header
        self._url_latest = None

    def _generate(self):
        out = BytesIO()
        out.write(self._url)
        out.write(b"\n")

        self._inner_header.seek(0)
        out.write(self._inner_header.read())

        self._data.seek(0)
        data = self._data.read()
        original_size = len(data)
        if original_size > 0:
            data = zlib.compress(data)
        store_size = len(data)
        out.write(b"Content-Type: snapshot, %d;\n" % store_size)
        out.write(b"Original-Size: snapshot, %d;\n" % original_size)
        out.write(b"\n")

        out.write(data)
        out.write(b"\n")
        out.seek(0)
        return out.read()

    def _read_inner_header(self):
        line = self._fp.readline()
        if not line:
            raise StopIteration
        line = line.strip()
        line_length = len(line)
        if line_length <= 0 and self._inner_header and self._url:
            self._read = self._read_http_header
        elif line_length > 1024:
            pass
        elif simple_check_url(line):
            self._reset()
            self._url = line
        else:
            if line.startswith(b"Original-Size:"):
                pass
            elif line.startswith(b"Store-Size: "):
                self._store_size = int(line.split(b":")[1].strip())
            else:
                self._inner_header.write(line)
                self._inner_header.write(b"\n")
        return self._read()

    def _read_http_header(self):
        line = self._fp.readline()
        if not line:
            raise StopIteration
        nline = line.strip()
        if not nline:
            self._data.write(line)
            self._read = self._read_data
        elif simple_check_url(nline):
            self._url_latest = nline
            self._read = self._read_data
        else:
            self._data.write(line)
        return self._read()

    def _read_data(self):
        if self._store_size <= 0 or self._url_latest is not None:
            return self._generate()

        data = self._fp.read(self._store_size)
        try:
            data = zlib.decompress(data)
        except:
            pass
        if self._store_size > 0 and not data:
            raise StopIteration

        if (
            self._data.tell() <= 0
        ):  # compat invalid format: no http headers but write two '\r\n'
            if data[0:2] == b"\r\n":
                o = self._fp.read(2)
                data = data[2:] + o
        self._data.write(data)
        return self._generate()

    def read(self):
        while True:
            try:
                yield self._read()
                self._reset()
            except StopIteration:
                return


class SpageToOffpage(object):
    def __init__(self, base_filename):
        self._fp = open_file(base_filename, "r")

    def close(self):
        self._fp.close()

    def read(self):
        for record in read(self._fp):
            yield record
