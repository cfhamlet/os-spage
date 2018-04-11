import zlib

import pytest
from jsonschema import ValidationError
from os_spage import open_file, read, write
from os_spage.compat import iteritems
from os_spage.default_schema import InnerHeaderKeys as I_KEYS
from os_spage.default_schema import RecordTypes as R_TYPES
from os_spage.default_schema import SpageKeys as S_KEYS


def test_write_invalid_data(tmpdir):
    with tmpdir.as_cwd():
        f = open_file('test', 'w')
        with pytest.raises(ValidationError):
            f.write(url='abc', inner_header={I_KEYS.BATCH_ID: 'test'})


def check_inner_header(w_inner_header, r_inner_header):
    if not w_inner_header:
        assert r_inner_header[I_KEYS.BATCH_ID] == '__CHANGE_ME__'
        return

    for k, v in iteritems(w_inner_header):
        k = str(k)
        if k != I_KEYS.STORE_SIZE:
            assert r_inner_header[k] == str(v)


def check_http_header(w_http_header, r_http_header):
    if w_http_header is None:
        assert r_http_header == {}
        return
    for k, v in iteritems(w_http_header):
        assert r_http_header[str(k)] == str(v)


def check_data(w_data, r_data, r_type):
    if w_data is None:
        assert r_data is None
        return
    if r_type == R_TYPES.COMPRESSED:
        assert zlib.decompress(r_data) == w_data
    else:
        assert r_data == w_data


RECORDS = [
    # inner_header, http_header, data
    (None, None, None),
    ({I_KEYS.BATCH_ID: 'test'}, {'k1': 'v1'}, b'hello'),
    ({I_KEYS.BATCH_ID: 'test'}, {}, b'hello'),
    ({I_KEYS.BATCH_ID: 'test'}, {'k1': 'v1'}, None),
    ({}, {'k1': 'v1'}, b'hello'),
    ({}, {'k1': 'v1'}, None),
]


def test_spage_reader_and_writer(tmpdir):
    base_url = "http://www.test.com/"
    filename_prefix = 'test_file_'
    with tmpdir.as_cwd():
        f = open_file(filename_prefix, 'w', roll_size=100)
        idx = 0
        for inner_header, http_header, data in RECORDS:
            url = base_url + str(idx)
            idx += 1
            f.write(url, inner_header=inner_header,
                    http_header=http_header, data=data, flush=True)
        f.close()
        f = open_file(filename_prefix, 'r')
        idx = 0
        for record in f.read():
            inner_header, http_header, data = RECORDS[idx]
            url = base_url + str(idx)
            idx += 1
            assert url == record[S_KEYS.URL]
            check_inner_header(inner_header, record[S_KEYS.INNER_HEADER])
            check_http_header(http_header, record[S_KEYS.HTTP_HEADER])
            check_data(data, record[S_KEYS.DATA],
                       record[S_KEYS.INNER_HEADER][I_KEYS.TYPE])


def test_genergal_read_and_write(tmpdir):
    base_url = "http://www.test.com/"
    with tmpdir.as_cwd():
        filename = 'test_file'
        f = open(filename, 'wb')
        idx = 0
        for inner_header, http_header, data in RECORDS:
            url = base_url + str(idx)
            idx += 1
            write(f, url, inner_header=inner_header,
                  http_header=http_header, data=data)
        f.close()
        f = open(filename, 'rb')
        idx = 0
        for record in read(f):
            inner_header, http_header, data = RECORDS[idx]
            url = base_url + str(idx)
            idx += 1
            assert url == record[S_KEYS.URL]
            check_inner_header(inner_header, record[S_KEYS.INNER_HEADER])
            check_http_header(http_header, record[S_KEYS.HTTP_HEADER])
            check_data(data, record[S_KEYS.DATA],
                       record[S_KEYS.INNER_HEADER][I_KEYS.TYPE])


CUSTOM_RECORDS = [
    # inner_header, http_header, data
    ({I_KEYS.BATCH_ID: 'test', I_KEYS.TYPE: R_TYPES.COMPRESSED,
      I_KEYS.ORIGINAL_SIZE: 5}, {'k1': 'v1'}, zlib.compress(b'hello')),
    ({I_KEYS.BATCH_ID: 'test', I_KEYS.TYPE: R_TYPES.FLAT,
      I_KEYS.ORIGINAL_SIZE: 5}, {'k1': 'v1'}, b'hello'),
    ({I_KEYS.BATCH_ID: 'test', I_KEYS.TYPE: R_TYPES.DELETED,
      I_KEYS.ORIGINAL_SIZE: 5}, {'k1': 'v1'}, b'hello'),
]


def check_custom_data(w_data, r_data):
    if w_data is None:
        assert r_data is None
        return
    assert r_data == w_data


def test_write_custom_data_and_read(tmpdir):
    base_url = "http://www.test.com/"
    with tmpdir.as_cwd():
        filename_prefix = 'test_file_'
        f = open_file(filename_prefix, 'w', roll_size=100)
        idx = 0
        for inner_header, http_header, data in CUSTOM_RECORDS:
            url = base_url + str(idx)
            idx += 1
            f.write(url, inner_header=inner_header,
                    http_header=http_header, data=data)
        f.close()
        f = open_file(filename_prefix, 'r')
        idx = 0
        for record in f.read():
            inner_header, http_header, data = CUSTOM_RECORDS[idx]
            url = base_url + str(idx)
            idx += 1
            assert url == record[S_KEYS.URL]
            check_inner_header(inner_header, record[S_KEYS.INNER_HEADER])
            check_http_header(http_header, record[S_KEYS.HTTP_HEADER])
            check_custom_data(data, record[S_KEYS.DATA])


INVALID_CUSTOM_RECORDS = [
    # inner_header, http_header, data
    ({I_KEYS.BATCH_ID: 'test', I_KEYS.TYPE: R_TYPES.COMPRESSED},
     {'k1': 'v1'}, zlib.compress(b'hello')),
    ({I_KEYS.BATCH_ID: 'test', I_KEYS.ORIGINAL_SIZE: 5},
     {'k1': 'v1'}, zlib.compress(b'hello')),
]


def test_write_invalid_custom_data(tmpdir):
    base_url = "http://www.test.com/"
    with tmpdir.as_cwd():
        filename_prefix = 'test_file_'
        f = open_file(filename_prefix, 'w', roll_size=100)
        idx = 0
        for inner_header, http_header, data in INVALID_CUSTOM_RECORDS:
            url = base_url + str(idx)
            idx += 1
            with pytest.raises(ValueError):
                f.write(url, inner_header=inner_header,
                        http_header=http_header, data=data)
        f.close()
