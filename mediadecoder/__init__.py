"""Media-decoding library based on MoviePy"""

__version__ = "0.2.2"
__author__ = "Daniel Schreij"
__license__ = "MIT"

from .states import *
from .decoder import Decoder
from .timer import Timer

__all__ = ["Decoder", "Timer"]
