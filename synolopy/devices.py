from synolopy.cgi import CGIConsumerFactory
from synolopy.errors import API_ERROR, SynologyError


DEFAULT_TIMEOUT = 5


def _nas_validator(response):
    status = response.status_code

    if status is not 200:
        raise SynologyError('The API request cannot been made')

    rsp = response.json()

    if not rsp['success']:
        code = rsp['error']['code']
        if code in API_ERROR:
            raise SynologyError(API_ERROR[code])
        else:
            raise SynologyError('Unknown error from API (%d)' % code)

    return rsp['data']


def _nas_api(url, login, password):
    assert url is not None, 'An URL is required'
    assert login and password, 'Authentication is required'
    struct = {
        'url': url,
        'login': login,
        'password': password,
        'interfaces': {
            'DownloadStation': {
                'authentication': True,
                'services': {
                    'schedule': {
                        'api': 'SYNO.DownloadStation.Schedule',
                        'version': 1
                    }
                }
            }
        }
    }
    api = CGIConsumerFactory.build(struct)
    api.set_validator(_nas_validator)
    return api


SynologyNasApi = _nas_api