# Easy use of the lib
from .devices import NasApi

# To implement its own CGI-based API wrapper easily
from .cgi import CGIFactory, SessionManager, ValidationManager

# To implement its own CGI-based API wrapper (hard way)
from .cgi import BaseConsumer, PathElement, CGI

# Errors
from .errors import *