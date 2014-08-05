from synolopy.cgi import CGIFactory
from synolopy.errors import API_ERROR, SynologyException


DEFAULT_TIMEOUT = 5


def _nas_validator(response):
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


def _nas_api(url):
    struct = {
        'URL': url,
        'PATH': {
            'DownloadStation': {
                'AUTH': False,
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
                'api': 'SYNO.DownloadStation.Schedule',
                'version': 1
            },
        }
    }
    return CGIFactory.build(struct)


SynologyNasApi = _nas_api