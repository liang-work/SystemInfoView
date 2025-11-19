###import modules
from . import CPU
from . import Memory
from . import Network
from . import Disk
#from . import Sensor
from . import SystemConst

import warnings
import psutil

try:
    from . import GPU
except Exception as e:
    warnings.warn(f"GPU module load failure, GPU info will not be available. Error: {e}")

__VERSION__ = "0.0.1"
__package__ = "PySystemInfo"
__author__ = "liang-work"

def GetBootTime() -> float:
    """Get boot time"""
    return psutil.boot_time()

def GetUser() -> list:
    """Get user info"""
    return psutil.users()