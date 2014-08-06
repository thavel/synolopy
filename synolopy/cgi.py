import requests

from Queue import Queue
from urlparse import urljoin
from urllib import urlencode

from synolopy.errors import *


TIMEOUT = 10


# ------------------------------------------------------------------------------
# Tools
# ------------------------------------------------------------------------------


def _url_formatter(url):
    if not url.endswith('/'):
        return url+'/'
    return url


# ------------------------------------------------------------------------------
# Common Gateway Interface URL building.
# ------------------------------------------------------------------------------


def _with_validation(func, *args, **kwargs):
    def inner(*args, **kwargs):
        obj = args[0]
        manager = obj.base().validation_manager
        if manager:
            return manager.validate(func(*args, **kwargs))
        return func(*args, **kwargs)
    return inner


class PathElement(object):
    """
    Object representation of any path URL node.
    """
    def __init__(self, path, parent, auth=False):
        self._path = path
        self._auth = auth
        self.__parent__ = parent
        if parent:
            setattr(parent, path.lower(), self)

    def base(self):
        """
        Gives the base element of an URL (starting with `http://`).
        """
        return self.__parent__.base()

    def parents(self):
        """
        Returns an simple FIFO queue with the ancestors and itself.
        """
        q = self.__parent__.parents()
        q.put(self)
        return q

    def path(self):
        """
        Gives a ready to use path element (ease join).
        """
        return _url_formatter(self._path)

    def url(self):
        """
        Returns the whole URL from the base to this node.
        """
        path = None
        nodes = self.parents()
        while not nodes.empty():
            path = urljoin(path, nodes.get().path())
        return path

    def auth_required(self):
        """
        If any ancestor required an authentication, this node needs it too.
        """
        if self._auth:
            return self._auth, self
        return self.__parent__.auth_required()


class BaseConsumer(PathElement):
    """
    Root element for the CGI services tree.
    """
    def __init__(self, url):
        super(BaseConsumer, self).__init__(url, None)
        self.session_manager = None
        self.validation_manager = None

    def parents(self):
        q = Queue()
        q.put(self)
        return q

    def auth_required(self):
        return self._auth, None

    def base(self):
        return self


class CGI(PathElement):
    """
    Object representation of a CGI, with useful methods to request and valid
    returned data and
    """
    def __init__(self, path, parent, **kwargs):
        super(CGI, self).__init__(path, parent)
        self.params = kwargs

    def path(self):
        return self._path

    def url(self, method=None, **kwargs):
        base = super(CGI, self).url()
        base = '{path}.cgi'.format(path=base)

        params = self.params
        if method:
            params['method'] = method
            params.update(kwargs)

        if params:
            return '{url}?{params}'.format(url=base, params=urlencode(params))
        return base

    @_with_validation
    def request(self, method, **kwargs):
        url = self.url(method, **kwargs)

        auth, node = self.auth_required()
        if auth:
            manager = self.base().session_manager
            if not manager:
                raise CGIException(
                    'Authentication is required by %s but no session manager '
                    'has been defined' % node.path()
                )
            session = manager.session(node) or manager.credentials(node)
            return requests.get(url, cookies=session, timeout=TIMEOUT)
        else:
            return requests.get(url, timeout=TIMEOUT)


# ------------------------------------------------------------------------------
# Factory tool
# ------------------------------------------------------------------------------


class CGIFactory(object):
    """
    Allows to build a CGI consumer from a python dictionary.
    """
    @staticmethod
    def build(data):
        base = BaseConsumer(data['URL'])
        CGIFactory._build_path(data, base)
        CGIFactory._build_cgi(data, base)
        return base

    @staticmethod
    def _build_path(data, parent):
        path_set = data['PATH'] if 'PATH' in data else dict()
        for path, content in path_set.iteritems():
            auth = content['AUTH'] if 'AUTH' in content else False
            pe = PathElement(path, parent, auth)
            CGIFactory._build_path(content, pe)
            CGIFactory._build_cgi(content, pe)

    @staticmethod
    def _build_cgi(data, parent):
        cgi_set = data['CGI'] if 'CGI' in data else dict()
        for cgi, content in cgi_set.iteritems():
            CGI(cgi, parent, **content)


# ------------------------------------------------------------------------------
# Managers
# ------------------------------------------------------------------------------


class SessionManager(object):
    def __init__(self, login, password, consumer):
        self.login = login
        self.password = password
        self.api = consumer
        self._sessions = dict()

    def session(self, node, session=None):
        if not session:
            try:
                return self._sessions[node.path]
            except KeyError:
                return None
        self._sessions[node.path] = session

    def credentials(self, node):
        raise NotImplementedError


class ValidationManager(object):
    @staticmethod
    def validate(response):
        raise NotImplementedError