import json
import requests

from  urlparse import urljoin
from urllib import urlencode
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException, Timeout

from synolopy.errors import SynologyError


BASE_TIMEOUT = 10
BASE_VERSION = 1


def url_format(url):
    if not url.endswith('/'):
        return url+'/'
    return url


class BaseConsumer(object):
    def __init__(self, url, login=None, password=None, timeout=BASE_TIMEOUT):
        self.url = url_format(url)
        self.login = login
        self.password = password
        self.timeout = timeout

    def register(self, name, interface):
        assert isinstance(interface, CGI), 'Only accepts CGI objects'
        interface.__base__ = self
        setattr(self, name, interface)


class CGI(object):
    def __init__(self, path, auth=True):
        self.path = url_format(path)
        self.auth = auth
        self.__base__ = None

    def service(self, name, **kwargs):
        srv = Service(name, **kwargs)
        srv.__cgi__ = self
        setattr(self, name, srv)


class Service(object):
    def __init__(self, interface, **kwargs):
        self.interface = interface
        self.params = kwargs
        self.__cgi__ = None

    def url(self):
        base = urljoin(self.__cgi__.__base__.url, self.__cgi__.path)
        return urljoin(base, self.interface+'.cgi')

    def get(self, method, **kwargs):
        params = self.params
        params['method'] = method
        params.update(kwargs)
        url = self.url()

        return '{url}?{params}'.format(url=url, params=urlencode(params))




















def _clean_response(func, *args, **kwargs):
    try:
        request = func(*args, **kwargs)
    except RequestException:
        raise SynologyError('The API request cannot been made')
    else:
        status = request.status_code

        # Check returned status code and raise exception if any
        if status is not 200:
            raise SynologyError('Request failed')

        # The request is valid, now check if it succeed
        content = request.json()
        if not content['success']:
            raise SynologyError('Error %d' % content['error'])

        # The request is valid, and it succeed
        return content['data']