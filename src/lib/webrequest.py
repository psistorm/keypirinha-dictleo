from urllib import request


def get_opener(http_url=None):
    if not http_url:
        return request.build_opener()
    else:
        proxy_handler = request.ProxyHandler({'http': http_url})
        return request.build_opener(proxy_handler)
