# os-spage
[![Build Status](https://www.travis-ci.org/cfhamlet/os-spage.svg?branch=master)](https://www.travis-ci.org/cfhamlet/os-spage)
[![codecov](https://codecov.io/gh/cfhamlet/os-spage/branch/master/graph/badge.svg)](https://codecov.io/gh/cfhamlet/os-spage)

Read and write spage.

# Install
  `pip install os-spage`

# Usage
  * Write
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
    f.write(url, html, inner_header=req_headers, http_header=res_headers, flush=True)
    f.close()
  ```
  * Read
  ```
    from os_spage import open_file
    f = open_file('file', 'r')
    for data in f.read():
        if data['url'] is None:
            continue
        print data['url']
        print data['inner_header'] # dict
        print data['http_header']  # dict
        print data['data']
    f.close()

  ```

# Unit Tests
  `$ tox`

# License
MIT licensed.
