Synolopy
========

Synology is a Python library aimed to help using Synology device's APIs.


Version
-------

Current stable version: 0.1.2


Features
--------

##### Synology NAS (aka DiskStation Manager)
* [[doc.1]] Download station API
* [[doc.2]] File station API
* [doc.3] Video station API

##### Common Gateway Interface builder
Since Synology APIs are build using the same pattern, this library also uses and provides tools to instanciate a pythonic consumer for any CGI-based API.


Installation
------------

##### Easy way

```sh
pip install synolopy
```

##### "Hard" way

```sh
git clone git@github.com:thavel/synolopy.git synolopy
cd ./synolopy
pip install .
```


Disk Station Manager API
------------------------

Disk Station Manager is the name of the system on any Synology NAS devices.

##### Quick start

To start using the NAS API, you need to import the library:

```python
from synolopy import NasApi

nas = NasApi('http://192.168.0.99:5000/webapi/', 'admin', 'my_super_strong_password')
```

Basically, any API request follows this pattern:
> nas.*application*.*service*.request(*method*, *[params]*)

For further information about methods and parameters, you need to read the
official documentation of the related application (cf. docs linked above).


##### Download Station

```python
nas.downloadstation.info.request('getinfo')

>>> {
    'version_string': '3.4-2558',
    'version': 2558, 
    'is_manager': True
}
```

Available services:
info, schedule, task, statistic, RSSsite, RSSfeed, btsearch


##### File Station

```python
nas.filestation.file_share.request('list_share', additional='real_path')

>>> {
    'total': 2,
    'shares': [
        {
            'isdir': True,
            'path': '/public',
            'additional': {
                'real_path': '/volume1/public'
            },
            'name': 'public'
        },
        {
            'isdir': True,
            'path': '/web',
            'additional': {
                'real_path': '/volume1/web'
            },
            'name': 'web'
        }
    ],
    'offset': 0
}
```

Available services:
info, file_share, file_find, file_virtual, file_favorite, file_thumb,
file_dirSize, file_md5, file_permission, api_upload, file_download,
file_sharing, file_crtfdr, file_rename, file_MVCP, file_delete, file_extract,
file_compress, background_task


##### Video Station

```python
nas.videostation.programlist.request(<request>)
```


[doc.1]:https://global.download.synology.com/download/Document/DeveloperGuide/Synology_Download_Station_Web_API.pdf
[doc.2]:https://global.download.synology.com/download/Document/DeveloperGuide/Synology_File_Station_API_Guide.pdf
