import json
import requests

from  urlparse import urljoin
from urllib import urlencode
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException, Timeout

from synolopy.errors import *


BASE_TIMEOUT = 10
BASE_VERSION = 1


def _validator(func, *args, **kwargs):
    def inner(*args, **kwargs):
        obj = args[0]
        if isinstance(obj, Service):
            valid = obj.__cgi__.__base__.validator
            if valid:
                return valid(func(*args, **kwargs))
        return func(*args, **kwargs)
    return inner


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
        self.validator = None

    def register(self, name, interface):
        assert isinstance(interface, CGI), 'Only accepts CGI objects'
        interface.__base__ = self
        setattr(self, name, interface)

    def set_validator(self, valid):
        self.validator = valid


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

    def _base_url(self):
        base = urljoin(self.__cgi__.__base__.url, self.__cgi__.path)
        return urljoin(base, self.interface+'.cgi')

    def url(self, method, **kwargs):
        params = self.params
        params['method'] = method
        params.update(kwargs)
        url = self._base_url()
        return '{url}?{params}'.format(url=url, params=urlencode(params))

    @_validator
    def request(self, *args, **kwargs):
        url = self.url(*args, **kwargs)
        timeout = self.__cgi__.__base__.timeout
        return requests.get(url, timeout=timeout)


class CGIConsumerFactory(object):
    @staticmethod
    def build(struct):
        try:
            # BaseConsumer
            url = struct['url']
            login = struct['login']
            password = struct['password']
            api = BaseConsumer(url, login, password)

            # Interfaces
            for i_name, i_params in struct['interfaces'].iteritems():
                auth = True
                if 'authentication' in i_params:
                    auth = i_params['authentication']
                cgi = CGI(i_name, auth)
                # Services
                for s_name, s_params in i_params['services'].iteritems():
                    cgi.service(s_name, **s_params)
                api.register(i_name.lower(), cgi)
        except KeyError:
            raise ConsumerFactoryException('Invalid struct declaration')
        else:
            return api


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