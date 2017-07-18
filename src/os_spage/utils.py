def is_url(url):
    if not url:
        return False
    return len(url) > 10 and (url.startswith('http://') or url.startswith('https://'))