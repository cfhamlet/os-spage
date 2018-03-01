import pytest
import zlib
from os_spage import open_file
from jsonschema import ValidationError


def test_write_invalid_data(tmpdir):
    with tmpdir.as_cwd():
        f = open_file('test', 'w')
        with pytest.raises(ValidationError):
            f.write('abc', {'batch-ID': 'test'})


def test_read_skip_store(tmpdir):
    with tmpdir.as_cwd():
        url = 'http://www.not_exist.com/'
        data = None
        inner_header = {'batch-ID': 'test'}
        f = open_file('test', 'w')
        f.write(url + '1', inner_header=inner_header,
                data=data, http_header={'try': 'exist'})
        f.write(url + '2', inner_header=inner_header, data='test')
        f.write(url + '3', inner_header=inner_header, data='test')
        f.close()
        f = open_file('test', 'r')
        count = 0
        for page in f.read():
            count += 1
            assert page["url"] == url + str(count)
            if count == 3:
                assert zlib.decompress(page['data']) == 'test'
            else:
                assert page['data'] is None


def test_read_has_http_header_no_data(tmpdir):
    with tmpdir.as_cwd():
        url = 'http://www.not_exist.com/'
        data = None
        f = open_file('test', 'w')
        inner_header = {'batch-ID': 'test'}
        f.write(url + '1', inner_header=inner_header,
                data=data, http_header={'try': 'exist'})
        f.write(url + '2', inner_header=inner_header, data='test')
        f.close()
        f = open_file('test', 'r')
        count = 0
        for page in f.read():
            count += 1
            assert page["url"] == url + str(count)
            if count == 2:
                assert zlib.decompress(page['data']) == 'test'
            else:
                assert page['data'] is None


def test_read_no_data(tmpdir):
    with tmpdir.as_cwd():
        url = 'http://www.not_exist.com/'
        data = None
        f = open_file('test', 'w')
        f.write(url, inner_header={'batch-ID': 'test'}, data=data)
        f.close()
        f = open_file('test', 'r')
        for page in f.read():
            assert page["url"] == url
            assert zlib.decompress(page['data']) == None


def test_read_with_http_header(tmpdir):
    with tmpdir.as_cwd():
        url = 'http://www.not_exist.com/'
        data = 'hello world!'
        f = open_file('test', 'w')
        headers = {'Server': 'nginx'}
        inner_header = {'batch-ID': 'test'}
        f.write(url, data=data, http_header=headers, inner_header=inner_header)
        f.close()
        f = open_file('test', 'r')
        for page in f.read():
            assert page["url"] == url
            assert zlib.decompress(page['data']) == data
            assert page["http_header"] == headers


def test_read_with_inner_header(tmpdir):
    with tmpdir.as_cwd():
        url = 'http://www.not_exist.com/'
        data = 'hello world!'
        headers = {'User-Agent': 'Mozilla/5.0', 'batch-ID': 'test'}
        f = open_file('test', 'w')
        f.write(url, data=data, inner_header=headers)
        f.close()
        f = open_file('test', 'r')
        for page in f.read():
            assert page["url"] == url
            assert zlib.decompress(page['data']) == data
            assert page['inner_header']['User-Agent'] == 'Mozilla/5.0'


def test_read_no_http_header(tmpdir):
    with tmpdir.as_cwd():
        url = 'http://www.not_exist.com/'
        data = 'hello world!'
        f = open_file('test', 'w', roll_size=10)
        f.write(url, inner_header={'batch-ID': 'test'}, data=data)
        f.close()
        f = open_file('test', 'r')
        for page in f.read():
            assert page["url"] == url
            assert zlib.decompress(page['data']) == data
