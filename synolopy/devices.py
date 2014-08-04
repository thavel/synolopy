from synolopy.cgi import CGIConsumerFactory


DEFAULT_TIMEOUT = 5


def _nas(url, login, password):
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
    return CGIConsumerFactory.build(struct)


SynologyNasApi = _nas