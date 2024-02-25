from _socket import gethostbyname


def get_ip(url):
    url = url.split('//')[1]
    if '/' in url:
        url = url.split('/')[0]
        ip = gethostbyname(url)
        return ip
    else:
        return False