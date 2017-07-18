import pytest
import zlib
from os_spage import open_file


def test_write_invalid_data(tmpdir):
    with tmpdir.as_cwd():
        f = open_file('test', 'w')
        with pytest.raises(ValueError):
            f.write('abc')


def test_read_skip_store(tmpdir):
    with tmpdir.as_cwd():
        url = 'http://www.not_exist.com/'
        data = None
        f = open_file('test', 'w')
        f.write(url + '1', data, http_header={'try': 'exist'})
        f.write(url + '2', 'test', skip_store=True)
        f.write(url + '3', 'test')
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
        f.write(url + '1', data, http_header={'try': 'exist'})
        f.write(url + '2', 'test')
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
        f.write(url, data)
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
        f.write(url, data, http_header=headers)
        f.close()
        f = open_file('test', 'r')
        for page in f.read():
            assert page["url"] == url
            assert zlib.decompress(page['data']) == data
            assert page["http_header"] == 'Server: nginx\r\n'


def test_read_with_inner_header(tmpdir):
    with tmpdir.as_cwd():
        url = 'http://www.not_exist.com/'
        data = 'hello world!'
        headers = {'User-Agent': 'Mozilla/5.0'}
        f = open_file('test', 'w')
        f.write(url, data, inner_header=headers)
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
        f.write(url, data)
        f.close()
        f = open_file('test', 'r')
        for page in f.read():
            assert page["url"] == url
            assert zlib.decompress(page['data']) == data
