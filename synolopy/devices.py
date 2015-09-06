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

        if 'data' in rsp:
            return rsp['data']


class _NasSessionManager(SessionManager):
    def credentials(self, node):
        url = self.api.auth.url('login',
                                account=self.login, passwd=self.password,
                                session=node.path()[:-1], format='cookie')

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
                    'info': {
                        'api': 'SYNO.DownloadStation.Info',
                        'version': 1
                    },
                    'schedule': {
                        'api': 'SYNO.DownloadStation.Schedule',
                        'version': 1
                    },
                    'task': {
                        'api': 'SYNO.DownloadStation.Task',
                        'version': 1
                    },
                    'statistic': {
                        'api': 'SYNO.DownloadStation.Statistic',
                        'version': 1
                    },
                    'RSSsite': {
                        'api': 'SYNO.DownloadStation.RSS.Site',
                        'version': 1
                    },
                    'RSSfeed': {
                        'api': 'SYNO.DownloadStation.RSS.Feed',
                        'version': 1
                    },
                    'btsearch': {
                        'api': 'SYNO.DownloadStation.BTSearch',
                        'version': 1
                    }
                }
            },
            'FileStation': {
                'AUTH': True,
                'CGI': {
                    'info': {
                        'api': 'SYNO.FileStation.Info',
                        'version': 1
                    },
                    'file_share': {
                        'api': 'SYNO.FileStation.List',
                        'version': 1
                    },
                    'file_find': {
                        'api': 'SYNO.FileStation.Search',
                        'version': 1
                    },
                    'file_virtual': {
                        'api': 'SYNO.FileStation.VirtualFolder',
                        'version': 1
                    },
                    'file_favorite': {
                        'api': 'SYNO.FileStation.Favorite',
                        'version': 1
                    },
                    'file_thumb': {
                        'api': 'SYNO.FileStation.Thumb',
                        'version': 1
                    },
                    'file_dirSize': {
                        'api': 'SYNO.FileStation.DirSize',
                        'version': 1
                    },
                    'file_md5': {
                        'api': 'SYNO.FileStation.MD5',
                        'version': 1
                    },
                    'file_permission': {
                        'api': 'SYNO.FileStation.CheckPermission',
                        'version': 1
                    },
                    'api_upload': {
                        'api': 'SYNO.FileStation.Upload',
                        'version': 1
                    },
                    'file_download': {
                        'api': 'SYNO.FileStation.Download',
                        'version': 1
                    },
                    'file_sharing': {
                        'api': 'SYNO.FileStation.Sharing',
                        'version': 1
                    },
                    'file_crtfdr': {
                        'api': 'SYNO.FileStation.CreateFolder',
                        'version': 1
                    },
                    'file_rename': {
                        'api': 'SYNO.FileStation.Rename',
                        'version': 1
                    },
                    'file_MVCP': {
                        'api': 'SYNO.FileStation.CopyMove',
                        'version': 1
                    },
                    'file_delete': {
                        'api': 'SYNO.FileStation.Delete',
                        'version': 1
                    },
                    'file_extract': {
                        'api': 'SYNO.FileStation.Extract',
                        'version': 1
                    },
                    'file_compress': {
                        'api': 'SYNO.FileStation.Compress',
                        'version': 1
                    },
                    'background_task': {
                        'api': 'SYNO.FileStation.BackgroundTask',
                        'version': 1
                    }
                }
            },
            'VideoStation': {
                'AUTH': True,
                'CGI': {
                    'channellist': {
                        'api': 'SYNO.DTV.Channel',
                        'version': 1
                    },
                    'programlist': {
                        'api': 'SYNO.DTV.Program',
                        'version': 1
                    },
                    'schedule_recording' : {
                        'api': 'SYNO.DTV.Schedule',
                        'version': 1
                    }
                },
            },
        },
        'CGI': {
            'auth': {
                'api': 'SYNO.API.Auth',
                'version': 2
            },
            'query': {
                'api': 'SYNO.API.Info',
                'version': 1
            }
        }
    }
    api = CGIFactory.build(struct)
    api.session_manager = _NasSessionManager(login, password, api)
    api.validation_manager = _NasValidationManager
    return api


NasApi = _nas_api