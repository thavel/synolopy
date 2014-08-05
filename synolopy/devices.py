import requests

from synolopy.cgi import CGIFactory, SessionManager, ValidationManager
from synolopy.errors import API_ERROR, SynologyException


class _NasValidationManager(ValidationManager):
    @staticmethod
    def validate(response):
        status = response.status_code

        if status is not 200:
            raise SynologyException('The API request cannot been made')

        rsp = response.json()

        if not rsp['success']:
            code = rsp['error']['code']
            if code in API_ERROR:
                raise SynologyException(API_ERROR[code])
            else:
                raise SynologyException('Unknown error from API (%d)' % code)

        return rsp['data']


class _NasSessionManager(SessionManager):
    def credentials(self, node):
        url = self.api.auth.url('login',
                                account=self.login,
                                passwd=self.password,
                                session=node.path()[:-1],
                                format='cookie')
        resp = requests.get(url, timeout=10, )
        cookie = _NasValidationManager.validate(resp)
        sid = dict(id=cookie['sid'])
        self.session(node, session=sid)
        return sid


def _nas_api(url, login, password):
    struct = {
        'URL': url,
        'PATH': {
            'DownloadStation': {
                'AUTH': True,
                'CGI': {
                    'schedule': {
                        'api': 'SYNO.DownloadStation.Schedule',
                        'version': 1
                    },
                    'task': {
                        'api': 'SYNO.DownloadStation.Task',
                        'version': 1
                    }
                }
            }
        },
        'CGI': {
            'auth': {
                'api': 'SYNO.API.Auth',
                'version': 2
            },
        }
    }
    api = CGIFactory.build(struct)
    api.session_manager = _NasSessionManager(login, password, api)
    api.validation_manager = _NasValidationManager
    return api


SynologyNasApi = _nas_api