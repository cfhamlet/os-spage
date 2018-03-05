# os-spage
[![Build Status](https://www.travis-ci.org/cfhamlet/os-spage.svg?branch=master)](https://www.travis-ci.org/cfhamlet/os-spage)
[![codecov](https://codecov.io/gh/cfhamlet/os-spage/branch/master/graph/badge.svg)](https://codecov.io/gh/cfhamlet/os-spage)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/os-spage.svg)](https://pypi.python.org/pypi/os-spage)
[![PyPI](https://img.shields.io/pypi/v/os-spage.svg)](https://pypi.python.org/pypi/os-spage)


Read and write Spage.

Spage is an incompact data structure to specify fetched record. Generally speaking, it contains four sub-block: *url*, *inner_header*, *http_header*, and *data*.

Spage:
- __url__: the URL.
- __inner_header__: key-values, can be used to record fetch/process info, such as fetch-time, data-digest, record-type,  ect.
- __http_header__: key-values, server's response HTTP Header as you know.
- __data__: fetched data, can be flat or compressed html.

We use dict type to implements Spage. A predefined [schema](https://github.com/cfhamlet/os-spage/blob/master/src/os_spage/default_schema.py) can be used for validating

It is common to write Spage to size-rotate-file, we choice [os-rotatefile](https://github.com/cfhamlet/os-rotatefile.git) as default back-end.
 

# Install
  `pip install os-spage`

# Usage
  * Write to size-rotate-file
  ```
    import urllib2
    from os_spage import open_file

    url = 'http://www.google.com/'
    req_headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(url, None, req_headers)

    response = urllib2.urlopen(req)
    html = response.read()
    res_headers = response.headers.dict

    f = open_file('file', 'w', roll_size='1G', compress=True)
    f.write(url, inner_header=req_headers, http_header=res_headers, data=html, flush=True)
    f.close()
  ```
  * Read from size-rotate-file
  ```
    from os_spage import open_file

    f = open_file('file', 'r')

    for record in f.read():
        print record
    f.close()
  ```
  * R/W from other file-like object
  ```
    import StringIO
    from os_spage import read, write

    s = StringIO.StringIO()
    write(s, "http://www.google.com/")

    s.seek(0)
    for record in read(s):
        print record

  ```

# Unit Tests
  `$ tox`

# License
MIT licensed.
