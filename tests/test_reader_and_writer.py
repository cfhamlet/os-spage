import zlib

import pytest
from jsonschema import ValidationError

from os_spage import open_file, read, write


def test_write_invalid_data(tmpdir):
    with tmpdir.as_cwd():
        f = open_file('test', 'w')
        with pytest.raises(ValidationError):
            f.write(url='abc', inner_header={'batchID': 'test'})


def check_inner_header(w_inner_header, r_inner_header):
    if not w_inner_header:
        assert r_inner_header['batchID'] == '__CHANGE_ME__'
        return

    for k, v in w_inner_header.iteritems():
        k = str(k)
        if k not in {'Store-Size', 'Original-Size'}:
            assert r_inner_header[k] == str(v)


def check_http_header(w_http_header, r_http_header):
    if w_http_header is None:
        assert r_http_header == {}
        return
    for k, v in w_http_header.iteritems():
        assert r_http_header[str(k)] == str(v)


def check_data(w_data, r_data):
    if w_data is None:
        assert r_data is None
        return
    assert zlib.decompress(r_data) == w_data


RECORDS = [
    # inner_header, http_header, data
    (None, None, None),
    ({'batchID': 'test'}, {'k1': 'v1'}, 'hello'),
    ({'batchID': 'test'}, {}, 'hello'),
    ({'batchID': 'test'}, {'k1': 'v1'}, None),
    ({}, {'k1': 'v1'}, 'hello'),
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
            assert url == record['url']
            check_inner_header(inner_header, record['inner_header'])
            check_http_header(http_header, record['http_header'])
            check_data(data, record['data'])


def test_genergal_read_and_write(tmpdir):
    base_url = "http://www.test.com/"
    with tmpdir.as_cwd():
        filename = 'test_file'
        f = open(filename, 'w')
        idx = 0
        for inner_header, http_header, data in RECORDS:
            url = base_url + str(idx)
            idx += 1
            write(f, url, inner_header=inner_header,
                  http_header=http_header, data=data)
        f.close()
        f = open(filename, 'r')
        idx = 0
        for record in read(f):
            inner_header, http_header, data = RECORDS[idx]
            url = base_url + str(idx)
            idx += 1
            assert url == record['url']
            check_inner_header(inner_header, record['inner_header'])
            check_http_header(http_header, record['http_header'])
            check_data(data, record['data'])
