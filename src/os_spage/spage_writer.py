import copy
import StringIO
import time
import zlib
from collections import OrderedDict

from os_rotatefile import open_file

from utils import is_url

_TIME_FORMAT = "%a %b %d %X %Y"

COMPRESSED_TYPE = 'compressed'
DELETED_TYPE = 'deleted'
FLAT_TYPE = 'flat'

INNER_HEADER = OrderedDict({
    "Version": 1.2,
    "Type": None,
    "Fetch-Time": None,
    "Original-Size": None,
    "Store-Size": None,
    "batchID": None,
    "attach": None,
    "IP-Address": '0.0.0.0',
    "Spider-Address": '0.0.0.0',
    "Digest": '0' * 32,
    "User-Agent": None,
    "Fetch-IP": '0.0.0.0',
    "Node-Fetch-Time": None,
})


class SpageWriter(object):
    def __init__(self, base_filename, roll_size='1G', compress=True):
        self._fp = open_file(base_filename, 'w', roll_size=roll_size)
        self._compress = compress

    def close(self):
        self._fp.close()

    def _http_header_str(self, http_header):
        if http_header is None:
            return None
        return '\r\n'.join([': '.join((k, v)) for k, v in http_header.items()])

    def _inner_header_str(self, inner_header):
        return "\n".join([": ".join([str(k), str(v)]) for
                          k, v in inner_header.items() if v is not None])

    def _inner_header(self, inner_header):
        d = copy.deepcopy(INNER_HEADER)
        if inner_header is not None:
            d.update(inner_header)
        if d['Fetch-Time'] is None:
            d['Fetch-Time'] = time.strftime(_TIME_FORMAT,
                                            time.localtime())
        return d

    def _compress_data(self, data):
        return zlib.compress(data)

    def _process(self, item, skip_store=False):
        http_header_str = self._http_header_str(item["http_header"])
        inner_header = item['inner_header']

        store_size = original_size = len(
            item['data']) if item['data'] is not None else None
        inner_header['Original-Size'] = original_size

        out_data = None
        if original_size is not None:
            if not skip_store:
                if inner_header.get('Type', None) is None:
                    if self._compress:
                        inner_header['Type'] = COMPRESSED_TYPE
                        out_data = self._compress_data(item['data'])
                        store_size = len(out_data)
                    else:
                        inner_header['Type'] = FLAT_TYPE
                        out_data = item['data']
                else:
                    out_data = item['data']
            else:
                store_size = None

        inner_header['Store-Size'] = store_size

        inner_header_str = self._inner_header_str(inner_header)
        o = StringIO.StringIO()
        o.write(item['url'])
        o.write('\n')
        o.write(inner_header_str)
        o.write('\n\n')
        if http_header_str or store_size is not None:
            o.write(http_header_str)
            o.write('\r\n\r\n')
        if store_size is not None:
            o.write(out_data)
            o.write('\r\n')
        o.seek(0)
        return o.read()

    def write(self, url, data=None, inner_header=None, http_header=None,
              skip_store=False, flush=False):
        if not is_url(url):
            raise ValueError, 'Invalid url'
        item = {'url': url}
        item['inner_header'] = self._inner_header(inner_header)
        item['http_header'] = http_header
        item['data'] = data
        store_data = self._process(item, skip_store)
        self._fp.write(store_data, flush)
