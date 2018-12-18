import zlib
from io import BytesIO

from os_spage import open_file, read


def test_read_offpage(tmpdir):
    url = 'http://www.google.com/'
    data1 = '1'*10
    data2 = '2'*11
    data3 = '3'*12
    raw = '''
{url}
Key1: Value1
Content-Type: A, 10;B, 11;C, 12;

{data1}{data2}{data3}
    '''.format(url=url, data1=data1, data2=data2, data3=data3)
    f = tmpdir.join('testfile.dat')
    f.write(raw.encode('utf8'))
    reader = open_file(f.strpath, 'r', page_type='offpage')
    for page in reader.read():
        assert page['url'] == 'http://www.google.com/'
        assert page['header']['Key1'] == 'Value1'
        assert page['data']['A'] == data1.encode()
        assert page['data']['B'] == data2.encode()
        assert page['data']['C'] == data3.encode()

    s = BytesIO(raw.encode('utf8'))
    for page in read(s, page_type='offpage'):
        assert page['url'] == 'http://www.google.com/'
        assert page['header']['Key1'] == 'Value1'
        assert page['data']['A'] == data1.encode()
        assert page['data']['B'] == data2.encode()
        assert page['data']['C'] == data3.encode()
